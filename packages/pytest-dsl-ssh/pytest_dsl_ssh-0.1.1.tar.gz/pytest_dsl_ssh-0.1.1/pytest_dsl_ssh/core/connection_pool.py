"""
SSH连接池管理

实现SSH连接的复用和生命周期管理，避免频繁创建和销毁连接
"""

import logging
import threading
import time
from typing import Dict, Optional, Set

from pytest_dsl_ssh.core.ssh_client import SSHClient
from pytest_dsl_ssh.core.sftp_client import SFTPClient

logger = logging.getLogger(__name__)


class ConnectionPool:
    """SSH连接池管理器"""

    def __init__(self, max_connections: int = 10, connection_timeout: int = 300):
        """
        初始化连接池

        Args:
            max_connections: 最大连接数
            connection_timeout: 连接超时时间（秒），超时未使用的连接将被回收
        """
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout

        # 连接存储：{connection_key: SSHClient}
        self._connections: Dict[str, SSHClient] = {}

        # SFTP客户端存储：{connection_key: SFTPClient}
        self._sftp_clients: Dict[str, SFTPClient] = {}

        # 连接最后使用时间：{connection_key: timestamp}
        self._last_used: Dict[str, float] = {}

        # 正在使用的连接：{connection_key}
        self._in_use: Set[str] = set()

        # 线程锁
        self._lock = threading.RLock()

        # 清理线程
        self._cleanup_thread = None
        self._cleanup_stop_event = threading.Event()

        # 启动清理线程
        self._start_cleanup_thread()

    def _generate_connection_key(self, hostname: str, port: int, username: str) -> str:
        """生成连接唯一标识"""
        return f"{username}@{hostname}:{port}"

    def get_ssh_client(self,
                       hostname: str,
                       port: int = 22,
                       username: str = None,
                       password: str = None,
                       private_key_path: str = None,
                       private_key_password: str = None,
                       **kwargs) -> SSHClient:
        """
        获取SSH客户端（从池中复用或创建新的）

        Args:
            hostname: SSH服务器地址
            port: SSH端口
            username: 用户名
            password: 密码
            private_key_path: 私钥文件路径
            private_key_password: 私钥密码
            **kwargs: 其他SSH客户端参数

        Returns:
            SSH客户端实例
        """
        connection_key = self._generate_connection_key(hostname, port, username)

        with self._lock:
            # 检查是否有可复用的连接
            if connection_key in self._connections:
                ssh_client = self._connections[connection_key]

                # 检查连接是否仍然有效
                if ssh_client.is_connected():
                    self._last_used[connection_key] = time.time()
                    self._in_use.add(connection_key)
                    logger.debug(f"复用SSH连接: {connection_key}")
                    return ssh_client
                else:
                    # 连接已断开，移除并创建新的
                    logger.debug(f"SSH连接已断开，移除并重新创建: {connection_key}")
                    self._remove_connection(connection_key)

            # 检查连接池大小限制
            if len(self._connections) >= self.max_connections:
                # 尝试清理未使用的连接
                self._cleanup_unused_connections()

                # 如果还是达到限制，移除最旧的连接
                if len(self._connections) >= self.max_connections:
                    self._remove_oldest_connection()

            # 创建新连接
            ssh_client = SSHClient(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                private_key_path=private_key_path,
                private_key_password=private_key_password,
                **kwargs
            )

            try:
                ssh_client.connect()

                self._connections[connection_key] = ssh_client
                self._last_used[connection_key] = time.time()
                self._in_use.add(connection_key)

                logger.info(f"创建新SSH连接: {connection_key}")
                return ssh_client

            except Exception as e:
                logger.error(f"创建SSH连接失败: {connection_key} - {e}")
                raise

    def get_sftp_client(self,
                        hostname: str,
                        port: int = 22,
                        username: str = None,
                        password: str = None,
                        private_key_path: str = None,
                        private_key_password: str = None,
                        **kwargs) -> SFTPClient:
        """
        获取SFTP客户端

        Args:
            与get_ssh_client相同

        Returns:
            SFTP客户端实例
        """
        connection_key = self._generate_connection_key(hostname, port, username)

        with self._lock:
            # 检查是否有可复用的SFTP客户端
            if connection_key in self._sftp_clients:
                sftp_client = self._sftp_clients[connection_key]

                if sftp_client.is_connected():
                    self._last_used[connection_key] = time.time()
                    logger.debug(f"复用SFTP连接: {connection_key}")
                    return sftp_client
                else:
                    # SFTP连接已断开，移除
                    logger.debug(f"SFTP连接已断开，移除: {connection_key}")
                    del self._sftp_clients[connection_key]

            # 获取SSH客户端（可能创建新的或复用现有的）
            ssh_client = self.get_ssh_client(
                hostname, port, username, password,
                private_key_path, private_key_password, **kwargs
            )

            # 创建SFTP客户端
            sftp_client = SFTPClient(ssh_client)
            sftp_client.connect()

            self._sftp_clients[connection_key] = sftp_client
            self._last_used[connection_key] = time.time()

            logger.info(f"创建新SFTP连接: {connection_key}")
            return sftp_client

    def release_connection(self, hostname: str, port: int = 22, username: str = None) -> None:
        """
        释放连接（标记为不再使用，但保持在池中）

        Args:
            hostname: SSH服务器地址
            port: SSH端口
            username: 用户名
        """
        connection_key = self._generate_connection_key(hostname, port, username)

        with self._lock:
            if connection_key in self._in_use:
                self._in_use.remove(connection_key)
                self._last_used[connection_key] = time.time()
                logger.debug(f"释放连接: {connection_key}")

    def close_connection(self, hostname: str, port: int = 22, username: str = None) -> None:
        """
        关闭并移除连接

        Args:
            hostname: SSH服务器地址
            port: SSH端口
            username: 用户名
        """
        connection_key = self._generate_connection_key(hostname, port, username)

        with self._lock:
            self._remove_connection(connection_key)
            logger.info(f"关闭连接: {connection_key}")

    def close_all_connections(self) -> None:
        """关闭所有连接"""
        with self._lock:
            connection_keys = list(self._connections.keys())

            for connection_key in connection_keys:
                self._remove_connection(connection_key)

            logger.info(f"关闭所有连接，共 {len(connection_keys)} 个")

    def get_connection_stats(self) -> Dict[str, int]:
        """获取连接池统计信息"""
        with self._lock:
            return {
                'total_connections': len(self._connections),
                'active_connections': len(self._in_use),
                'idle_connections': len(self._connections) - len(self._in_use),
                'sftp_connections': len(self._sftp_clients),
                'max_connections': self.max_connections
            }

    def list_connections(self) -> Dict[str, Dict]:
        """列出所有连接信息"""
        with self._lock:
            connections_info = {}

            for connection_key, ssh_client in self._connections.items():
                connections_info[connection_key] = {
                    'hostname': ssh_client.hostname,
                    'port': ssh_client.port,
                    'username': ssh_client.username,
                    'is_connected': ssh_client.is_connected(),
                    'in_use': connection_key in self._in_use,
                    'last_used': self._last_used.get(connection_key, 0),
                    'has_sftp': connection_key in self._sftp_clients,
                    'auth_method': 'key' if ssh_client.private_key_path else 'password'
                }

            return connections_info

    def _remove_connection(self, connection_key: str) -> None:
        """移除连接（内部方法，需要持有锁）"""
        # 关闭SFTP连接
        if connection_key in self._sftp_clients:
            try:
                self._sftp_clients[connection_key].disconnect()
            except Exception as e:
                logger.warning(f"关闭SFTP连接时出现异常: {e}")
            del self._sftp_clients[connection_key]

        # 关闭SSH连接
        if connection_key in self._connections:
            try:
                self._connections[connection_key].disconnect()
            except Exception as e:
                logger.warning(f"关闭SSH连接时出现异常: {e}")
            del self._connections[connection_key]

        # 清理相关数据
        self._in_use.discard(connection_key)
        self._last_used.pop(connection_key, None)

    def _remove_oldest_connection(self) -> None:
        """移除最旧的连接（内部方法）"""
        if not self._connections:
            return

        # 找到最旧的未使用连接
        unused_connections = {
            key: last_used for key, last_used in self._last_used.items()
            if key not in self._in_use
        }

        if unused_connections:
            oldest_key = min(unused_connections.items(), key=lambda x: x[1])[0]
        else:
            # 如果所有连接都在使用，移除最旧的连接
            oldest_key = min(self._last_used.items(), key=lambda x: x[1])[0]

        logger.warning(f"连接池已满，移除最旧连接: {oldest_key}")
        self._remove_connection(oldest_key)

    def _cleanup_unused_connections(self) -> None:
        """清理超时未使用的连接（内部方法）"""
        current_time = time.time()
        expired_connections = []

        for connection_key, last_used in self._last_used.items():
            if (connection_key not in self._in_use and
                    current_time - last_used > self.connection_timeout):
                expired_connections.append(connection_key)

        for connection_key in expired_connections:
            logger.debug(f"清理超时连接: {connection_key}")
            self._remove_connection(connection_key)

    def _start_cleanup_thread(self) -> None:
        """启动清理线程"""
        def cleanup_worker():
            while not self._cleanup_stop_event.wait(60):  # 每60秒检查一次
                try:
                    with self._lock:
                        self._cleanup_unused_connections()
                except Exception as e:
                    logger.error(f"清理线程出现异常: {e}")

        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        logger.debug("连接池清理线程已启动")

    def _stop_cleanup_thread(self) -> None:
        """停止清理线程"""
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_stop_event.set()
            self._cleanup_thread.join(timeout=5)
            logger.debug("连接池清理线程已停止")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close_all_connections()
        self._stop_cleanup_thread()

    def __del__(self):
        """析构函数"""
        try:
            self.close_all_connections()
            self._stop_cleanup_thread()
        except Exception:
            pass  # 忽略析构时的异常


# 全局连接池实例
_global_connection_pool: Optional[ConnectionPool] = None


def get_global_connection_pool() -> ConnectionPool:
    """获取全局连接池实例"""
    global _global_connection_pool

    if _global_connection_pool is None:
        _global_connection_pool = ConnectionPool()

    return _global_connection_pool


def set_global_connection_pool(pool: ConnectionPool) -> None:
    """设置全局连接池实例"""
    global _global_connection_pool

    if _global_connection_pool is not None:
        _global_connection_pool.close_all_connections()

    _global_connection_pool = pool


def close_global_connection_pool() -> None:
    """关闭全局连接池"""
    global _global_connection_pool

    if _global_connection_pool is not None:
        _global_connection_pool.close_all_connections()
        _global_connection_pool = None
