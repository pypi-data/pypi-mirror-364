"""
统一SSH配置管理器

整合所有配置获取逻辑，提供统一的配置获取接口
"""

import logging
from typing import Dict, Optional, Any, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SSHConnectionConfig:
    """SSH连接配置（简化版）"""
    hostname: str
    port: int = 22
    username: Optional[str] = None
    password: Optional[str] = None
    private_key_path: Optional[str] = None
    private_key_password: Optional[str] = None
    connect_timeout: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'hostname': self.hostname,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'private_key_path': self.private_key_path,
            'private_key_password': self.private_key_password,
            'connect_timeout': self.connect_timeout
        }


class UnifiedSSHConfigManager:
    """统一SSH配置管理器
    
    按优先级获取SSH配置：
    1. Context配置（最高优先级）
    2. 全局配置管理器
    3. 直接参数（最低优先级）
    """
    
    def __init__(self):
        self._global_config_manager = None
    
    def get_connection_config(
        self,
        context: Any,
        server: str,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        private_key_path: Optional[str] = None,
        private_key_password: Optional[str] = None,
        connect_timeout: Optional[int] = None
    ) -> SSHConnectionConfig:
        """获取SSH连接配置
        
        Args:
            context: 测试上下文
            server: 服务器名称或主机地址
            port: 端口号（可选）
            username: 用户名（可选）
            password: 密码（可选）
            private_key_path: 私钥路径（可选）
            private_key_password: 私钥密码（可选）
            connect_timeout: 连接超时时间（可选）
            
        Returns:
            SSHConnectionConfig: SSH连接配置
        """
        # 1. 尝试从context获取配置
        context_config = self._get_config_from_context(context, server)
        if context_config:
            logger.debug(f"使用context配置获取SSH服务器信息: {server}")
            return self._merge_config(
                context_config, port, username, password, 
                private_key_path, private_key_password, connect_timeout
            )
        
        # 2. 尝试从全局配置管理器获取
        global_config = self._get_config_from_global_manager(server)
        if global_config:
            logger.debug(f"使用全局配置获取SSH服务器信息: {server}")
            return self._merge_config(
                global_config, port, username, password,
                private_key_path, private_key_password, connect_timeout
            )
        
        # 3. 使用直接参数
        logger.debug(f"使用直接参数创建SSH配置: {server}")
        return SSHConnectionConfig(
            hostname=server,
            port=port or 22,
            username=username,
            password=password,
            private_key_path=private_key_path,
            private_key_password=private_key_password,
            connect_timeout=connect_timeout or 10
        )
    
    def _get_config_from_context(self, context: Any, server: str) -> Optional[Dict[str, Any]]:
        """从context获取配置"""
        try:
            if not hasattr(context, 'get'):
                return None
                
            ssh_servers_config = context.get("ssh_servers")
            if ssh_servers_config and server in ssh_servers_config:
                print(f"✓ 从context找到服务器 '{server}' 的配置")
                return ssh_servers_config[server]
                
        except Exception as e:
            logger.debug(f"从context获取配置失败: {e}")
        
        return None
    
    def _get_config_from_global_manager(self, server: str) -> Optional[Dict[str, Any]]:
        """从全局配置管理器获取配置（暂时禁用，专注于context配置）"""
        # 暂时禁用全局配置管理器，专注于context配置
        # 如果需要支持配置文件，可以在这里添加简单的文件读取逻辑
        return None
    
    def _merge_config(
        self,
        base_config: Dict[str, Any],
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        private_key_path: Optional[str] = None,
        private_key_password: Optional[str] = None,
        connect_timeout: Optional[int] = None
    ) -> SSHConnectionConfig:
        """合并配置，参数优先级高于配置"""
        return SSHConnectionConfig(
            hostname=base_config.get('hostname'),
            port=port if port is not None else base_config.get('port', 22),
            username=username or base_config.get('username'),
            password=password or base_config.get('password'),
            private_key_path=private_key_path or base_config.get('private_key_path'),
            private_key_password=private_key_password or base_config.get('private_key_password'),
            connect_timeout=connect_timeout if connect_timeout is not None else base_config.get('connect_timeout', 10)
        )


# 全局统一配置管理器实例
_unified_config_manager = None


def get_unified_config_manager() -> UnifiedSSHConfigManager:
    """获取全局统一配置管理器实例"""
    global _unified_config_manager
    if _unified_config_manager is None:
        _unified_config_manager = UnifiedSSHConfigManager()
    return _unified_config_manager


def get_ssh_connection_config(
    context: Any,
    server: str,
    **kwargs
) -> SSHConnectionConfig:
    """便捷函数：获取SSH连接配置"""
    manager = get_unified_config_manager()
    return manager.get_connection_config(context, server, **kwargs)
