"""
SSH配置管理器

统一的SSH配置管理，支持从context和配置文件获取配置
"""

# 直接使用统一配置管理器
from .unified_config import (
    SSHConnectionConfig as SSHServerConfig,
    UnifiedSSHConfigManager as ConfigManager,
    get_unified_config_manager as get_global_config_manager,
    get_ssh_connection_config
)

__all__ = [
    'SSHServerConfig',
    'ConfigManager', 
    'get_global_config_manager',
    'get_ssh_connection_config'
]
