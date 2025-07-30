"""
SSH客户端封装

基于paramiko实现的SSH连接和命令执行功能
"""

import logging
import socket
import time
from typing import Dict, List, Optional, Union
from pathlib import Path

import paramiko
from paramiko import SSHClient as ParamikoSSHClient, AutoAddPolicy
from paramiko.ssh_exception import (
    AuthenticationException,
    NoValidConnectionsError,
)

from pytest_dsl_ssh.exceptions import (
    SSHConnectionError,
    SSHAuthenticationError,
    SSHCommandError,
)

logger = logging.getLogger(__name__)


class SSHClient:
    """SSH客户端类，封装SSH连接和操作"""

    def __init__(self,
                 hostname: str,
                 port: int = 22,
                 username: str = None,
                 password: str = None,
                 private_key_path: str = None,
                 private_key_password: str = None,
                 timeout: int = 30,
                 connect_timeout: int = 10,
                 auto_add_host_keys: bool = True,
                 compress: bool = False,
                 keep_alive_interval: int = 0):
        """
        初始化SSH客户端

        Args:
            hostname: SSH服务器地址
            port: SSH端口，默认22
            username: 用户名
            password: 密码
            private_key_path: 私钥文件路径
            private_key_password: 私钥密码
            timeout: 操作超时时间（秒）
            connect_timeout: 连接超时时间（秒）
            auto_add_host_keys: 是否自动添加主机密钥
            compress: 是否启用压缩
            keep_alive_interval: 保活间隔（秒），0表示禁用
        """
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.private_key_path = private_key_path
        self.private_key_password = private_key_password
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.auto_add_host_keys = auto_add_host_keys
        self.compress = compress
        self.keep_alive_interval = keep_alive_interval

        self._client: Optional[ParamikoSSHClient] = None
        self._is_connected = False

    def connect(self) -> None:
        """建立SSH连接"""
        try:
            logger.info(f"正在连接SSH服务器: {self.username}@{self.hostname}:{self.port}")

            self._client = ParamikoSSHClient()

            if self.auto_add_host_keys:
                self._client.set_missing_host_key_policy(AutoAddPolicy())

            # 准备连接参数
            connect_kwargs = {
                'hostname': self.hostname,
                'port': self.port,
                'username': self.username,
                'timeout': self.connect_timeout,
                'compress': self.compress,
            }

            # 设置认证方式
            if self.private_key_path:
                # 使用私钥认证
                private_key = self._load_private_key()
                connect_kwargs['pkey'] = private_key
            elif self.password:
                # 使用密码认证
                connect_kwargs['password'] = self.password
            else:
                raise SSHAuthenticationError("必须提供密码或私钥")

            # 建立连接
            self._client.connect(**connect_kwargs)

            # 设置保活
            if self.keep_alive_interval > 0:
                transport = self._client.get_transport()
                if transport:
                    transport.set_keepalive(self.keep_alive_interval)

            self._is_connected = True
            logger.info(f"SSH连接成功: {self.username}@{self.hostname}:{self.port}")

        except AuthenticationException as e:
            raise SSHAuthenticationError(f"SSH认证失败", str(e))
        except NoValidConnectionsError as e:
            raise SSHConnectionError(f"无法连接到SSH服务器", str(e))
        except socket.timeout as e:
            raise SSHConnectionError(f"SSH连接超时", str(e))
        except Exception as e:
            raise SSHConnectionError(f"SSH连接失败", str(e))

    def disconnect(self) -> None:
        """断开SSH连接"""
        if self._client:
            try:
                self._client.close()
                logger.info(f"SSH连接已断开: {self.hostname}")
            except Exception as e:
                logger.warning(f"断开SSH连接时出现异常: {e}")
            finally:
                self._client = None
                self._is_connected = False

    def is_connected(self) -> bool:
        """检查连接状态"""
        if not self._client or not self._is_connected:
            return False

        try:
            transport = self._client.get_transport()
            return transport and transport.is_active()
        except Exception:
            return False

    def execute_command(self,
                        command: str,
                        timeout: Optional[int] = None,
                        get_pty: bool = False,
                        combine_stderr: bool = True) -> Dict[str, Union[str, int]]:
        """
        执行SSH命令

        Args:
            command: 要执行的命令
            timeout: 命令超时时间，None使用默认值
            get_pty: 是否请求伪终端
            combine_stderr: 是否将stderr合并到stdout

        Returns:
            包含命令执行结果的字典：
            {
                'command': 执行的命令,
                'exit_code': 退出码,
                'stdout': 标准输出,
                'stderr': 标准错误,
                'execution_time': 执行时间（秒）
            }
        """
        if not self.is_connected():
            raise SSHConnectionError("SSH连接未建立或已断开")

        if timeout is None:
            timeout = self.timeout

        logger.info(f"执行SSH命令: {command}")
        start_time = time.time()

        try:
            stdin, stdout, stderr = self._client.exec_command(
                command,
                timeout=timeout,
                get_pty=get_pty
            )

            # 等待命令完成
            exit_code = stdout.channel.recv_exit_status()

            # 读取输出
            stdout_data = stdout.read().decode('utf-8', errors='replace')
            stderr_data = stderr.read().decode('utf-8', errors='replace')

            # 关闭通道
            stdin.close()
            stdout.close()
            stderr.close()

            execution_time = time.time() - start_time

            result = {
                'command': command,
                'exit_code': exit_code,
                'stdout': stdout_data,
                'stderr': stderr_data,
                'execution_time': round(execution_time, 3)
            }

            if combine_stderr and stderr_data:
                result['stdout'] = stdout_data + stderr_data

            logger.info(f"命令执行完成，退出码: {exit_code}，耗时: {execution_time:.3f}秒")

            return result

        except socket.timeout:
            raise SSHCommandError(f"命令执行超时（{timeout}秒）", command)
        except Exception as e:
            raise SSHCommandError(f"命令执行失败", command, details=str(e))

    def execute_commands(self,
                         commands: List[str],
                         stop_on_error: bool = True,
                         timeout: Optional[int] = None) -> List[Dict[str, Union[str, int]]]:
        """
        批量执行SSH命令

        Args:
            commands: 命令列表
            stop_on_error: 遇到错误是否停止
            timeout: 每个命令的超时时间

        Returns:
            命令执行结果列表
        """
        results = []

        for i, command in enumerate(commands):
            try:
                result = self.execute_command(command, timeout=timeout)
                results.append(result)

                # 检查是否需要在错误时停止
                if stop_on_error and result['exit_code'] != 0:
                    logger.warning(f"命令 {i + 1} 执行失败，停止后续命令执行")
                    break

            except Exception as e:
                error_result = {
                    'command': command,
                    'exit_code': -1,
                    'stdout': '',
                    'stderr': str(e),
                    'execution_time': 0,
                    'error': str(e)
                }
                results.append(error_result)

                if stop_on_error:
                    logger.warning(f"命令 {i + 1} 执行异常，停止后续命令执行")
                    break

        return results

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """
        通过SCP上传文件

        Args:
            local_path: 本地文件路径
            remote_path: 远程文件路径

        Returns:
            是否成功
        """
        try:
            with self._client.open_sftp() as sftp:
                sftp.put(local_path, remote_path)
                logger.info(f"文件上传成功: {local_path} -> {remote_path}")
                return True
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        通过SCP下载文件

        Args:
            remote_path: 远程文件路径  
            local_path: 本地文件路径

        Returns:
            是否成功
        """
        try:
            with self._client.open_sftp() as sftp:
                sftp.get(remote_path, local_path)
                logger.info(f"文件下载成功: {remote_path} -> {local_path}")
                return True
        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            return False

    def _load_private_key(self) -> paramiko.PKey:
        """加载私钥文件"""
        if not self.private_key_path:
            raise SSHAuthenticationError("私钥路径不能为空")

        key_path = Path(self.private_key_path)
        if not key_path.exists():
            raise SSHAuthenticationError(f"私钥文件不存在: {self.private_key_path}")

        try:
            # 尝试不同的私钥格式
            for key_class in [paramiko.RSAKey, paramiko.DSAKey, paramiko.ECDSAKey, paramiko.Ed25519Key]:
                try:
                    return key_class.from_private_key_file(
                        str(key_path),
                        password=self.private_key_password
                    )
                except paramiko.SSHException:
                    continue

            raise SSHAuthenticationError(f"无法解析私钥文件: {self.private_key_path}")

        except Exception as e:
            raise SSHAuthenticationError(f"加载私钥失败", str(e))

    def get_connection_info(self) -> Dict[str, Union[str, int, bool]]:
        """获取连接信息"""
        return {
            'hostname': self.hostname,
            'port': self.port,
            'username': self.username,
            'is_connected': self.is_connected(),
            'auth_method': 'key' if self.private_key_path else 'password',
            'auto_add_host_keys': self.auto_add_host_keys,
            'compress': self.compress,
            'keep_alive_interval': self.keep_alive_interval
        }

    def __enter__(self):
        """上下文管理器入口"""
        if not self.is_connected():
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.disconnect()

    def __repr__(self):
        status = "连接中" if self.is_connected() else "未连接"
        return f"SSHClient(host={self.hostname}:{self.port}, user={self.username}, status={status})"
