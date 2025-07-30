"""
SSH配置管理器

用于管理SSH连接配置、服务器预设和认证信息
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from ..exceptions import SSHConfigError

logger = logging.getLogger(__name__)


@dataclass
class SSHServerConfig:
    """SSH服务器配置"""
    name: str  # 配置名称
    hostname: str  # 服务器地址
    port: int = 22  # SSH端口
    username: Optional[str] = None  # 用户名
    password: Optional[str] = None  # 密码
    private_key_path: Optional[str] = None  # 私钥文件路径
    private_key_password: Optional[str] = None  # 私钥密码
    timeout: int = 30  # 操作超时时间
    connect_timeout: int = 10  # 连接超时时间
    auto_add_host_keys: bool = True  # 是否自动添加主机密钥
    compress: bool = False  # 是否启用压缩
    keep_alive_interval: int = 0  # 保活间隔
    description: Optional[str] = None  # 配置描述
    tags: Optional[List[str]] = None  # 标签

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SSHServerConfig':
        """从字典创建配置"""
        return cls(**data)


class ConfigManager:
    """SSH配置管理器"""

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路径，None则使用默认路径
        """
        self.config_file = config_file or self._get_default_config_file()
        self.configs: Dict[str, SSHServerConfig] = {}

        # 尝试加载配置文件
        if Path(self.config_file).exists():
            self.load_config()

    def _get_default_config_file(self) -> str:
        """获取默认配置文件路径"""
        # 优先使用环境变量
        if 'PYTEST_DSL_SSH_CONFIG' in os.environ:
            return os.environ['PYTEST_DSL_SSH_CONFIG']

        # 在用户主目录查找
        home_config = Path.home() / '.pytest-dsl-ssh' / 'config.yaml'
        if home_config.exists():
            return str(home_config)

        # 在当前目录查找
        local_config = Path.cwd() / 'ssh_config.yaml'
        if local_config.exists():
            return str(local_config)

        # 返回默认路径
        return str(home_config)

    def load_config(self, file_path: Optional[str] = None) -> None:
        """
        加载配置文件

        Args:
            file_path: 配置文件路径，None则使用默认路径
        """
        config_path = file_path or self.config_file

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.json'):
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)

            # 解析服务器配置，支持多种字段名
            servers = data.get('servers', {}) or data.get('ssh_servers', {})
            self.configs.clear()

            for name, config_data in servers.items():
                config_data['name'] = name
                try:
                    server_config = SSHServerConfig.from_dict(config_data)
                    self.configs[name] = server_config
                except Exception as e:
                    logger.warning(f"解析服务器配置失败 '{name}': {e}")

            logger.info(f"加载SSH配置文件成功: {config_path}, 共 {len(self.configs)} 个服务器配置")

        except FileNotFoundError:
            logger.warning(f"SSH配置文件不存在: {config_path}")
        except Exception as e:
            raise SSHConfigError(f"加载SSH配置文件失败: {str(e)}")

    def save_config(self, file_path: Optional[str] = None) -> None:
        """
        保存配置文件

        Args:
            file_path: 配置文件路径，None则使用默认路径
        """
        config_path = file_path or self.config_file

        try:
            # 准备配置数据
            data = {
                'servers': {
                    name: {k: v for k, v in config.to_dict().items() if k != 'name'}
                    for name, config in self.configs.items()
                }
            }

            # 确保目录存在
            Path(config_path).parent.mkdir(parents=True, exist_ok=True)

            # 保存文件
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.endswith('.json'):
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"保存SSH配置文件成功: {config_path}")

        except Exception as e:
            raise SSHConfigError(f"保存SSH配置文件失败: {str(e)}")

    def add_server(self, config: SSHServerConfig) -> None:
        """
        添加服务器配置

        Args:
            config: 服务器配置
        """
        if config.name in self.configs:
            logger.warning(f"服务器配置 '{config.name}' 已存在，将被覆盖")

        self.configs[config.name] = config
        logger.info(f"添加服务器配置: {config.name}")

    def remove_server(self, name: str) -> bool:
        """
        移除服务器配置

        Args:
            name: 配置名称

        Returns:
            是否成功移除
        """
        if name in self.configs:
            del self.configs[name]
            logger.info(f"移除服务器配置: {name}")
            return True
        else:
            logger.warning(f"服务器配置不存在: {name}")
            return False

    def get_server(self, name: str) -> Optional[SSHServerConfig]:
        """
        获取服务器配置

        优先级：
        1. 本地配置文件中的配置
        2. YAML变量系统中的配置

        Args:
            name: 配置名称

        Returns:
            服务器配置，不存在返回None
        """
        # 首先检查本地配置
        local_config = self.configs.get(name)
        if local_config:
            return local_config

        # 如果本地配置中没有，尝试从YAML变量系统获取
        try:
            from .yaml_config_loader import get_global_yaml_loader
            yaml_loader = get_global_yaml_loader()
            yaml_config = yaml_loader.get_server(name)
            if yaml_config:
                logger.info(f"从YAML变量系统获取SSH服务器配置: {name}")
                return yaml_config
        except Exception as e:
            logger.debug(f"从YAML变量系统获取配置失败: {e}")

        return None

    def list_servers(self, tags: Optional[List[str]] = None) -> List[SSHServerConfig]:
        """
        列出服务器配置

        Args:
            tags: 筛选标签，None表示返回所有

        Returns:
            服务器配置列表
        """
        if tags is None:
            return list(self.configs.values())

        filtered_configs = []
        for config in self.configs.values():
            if any(tag in config.tags for tag in tags):
                filtered_configs.append(config)

        return filtered_configs

    def search_servers(self, keyword: str) -> List[SSHServerConfig]:
        """
        搜索服务器配置

        Args:
            keyword: 搜索关键词（匹配名称、主机名、描述）

        Returns:
            匹配的服务器配置列表
        """
        keyword = keyword.lower()
        matching_configs = []

        for config in self.configs.values():
            if (keyword in config.name.lower() or
                keyword in config.hostname.lower() or
                    (config.description and keyword in config.description.lower())):
                matching_configs.append(config)

        return matching_configs

    def update_server(self, name: str, **updates) -> bool:
        """
        更新服务器配置

        Args:
            name: 配置名称
            **updates: 要更新的字段

        Returns:
            是否成功更新
        """
        if name not in self.configs:
            logger.warning(f"服务器配置不存在: {name}")
            return False

        config = self.configs[name]
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                logger.warning(f"无效的配置字段: {key}")

        logger.info(f"更新服务器配置: {name}")
        return True

    def create_default_config(self) -> None:
        """创建默认配置文件"""
        default_configs = [
            SSHServerConfig(
                name="localhost",
                hostname="localhost",
                port=22,
                username="root",
                description="本地SSH服务器",
                tags=["local", "test"]
            ),
            SSHServerConfig(
                name="test_server",
                hostname="test.example.com",
                port=22,
                username="testuser",
                description="测试服务器",
                tags=["test", "staging"]
            ),
            SSHServerConfig(
                name="prod_server",
                hostname="prod.example.com",
                port=22,
                username="produser",
                private_key_path="~/.ssh/id_rsa",
                description="生产服务器",
                tags=["production", "critical"]
            )
        ]

        for config in default_configs:
            self.add_server(config)

        self.save_config()
        logger.info("创建默认SSH配置文件")

    def validate_config(self, config: SSHServerConfig) -> List[str]:
        """
        验证配置有效性

        Args:
            config: 服务器配置

        Returns:
            错误信息列表，空列表表示配置有效
        """
        errors = []

        # 检查必需字段
        if not config.name:
            errors.append("配置名称不能为空")

        if not config.hostname:
            errors.append("主机名不能为空")

        if not (1 <= config.port <= 65535):
            errors.append("端口号必须在1-65535之间")

        # 检查认证配置
        if not config.username:
            errors.append("用户名不能为空")

        if not config.password and not config.private_key_path:
            errors.append("必须提供密码或私钥文件路径")

        # 检查私钥文件
        if config.private_key_path:
            key_path = Path(config.private_key_path).expanduser()
            if not key_path.exists():
                errors.append(f"私钥文件不存在: {config.private_key_path}")
            elif not key_path.is_file():
                errors.append(f"私钥路径不是文件: {config.private_key_path}")

        # 检查超时配置
        if config.timeout <= 0:
            errors.append("操作超时时间必须大于0")

        if config.connect_timeout <= 0:
            errors.append("连接超时时间必须大于0")

        return errors

    def get_config_stats(self) -> Dict[str, Any]:
        """获取配置统计信息"""
        total_configs = len(self.configs)

        # 统计认证方式
        password_auth = sum(1 for c in self.configs.values() if c.password and not c.private_key_path)
        key_auth = sum(1 for c in self.configs.values() if c.private_key_path)

        # 统计标签
        all_tags = set()
        for config in self.configs.values():
            all_tags.update(config.tags)

        # 统计端口分布
        port_distribution = {}
        for config in self.configs.values():
            port = config.port
            port_distribution[port] = port_distribution.get(port, 0) + 1

        return {
            'total_configs': total_configs,
            'auth_methods': {
                'password': password_auth,
                'private_key': key_auth,
                'mixed': total_configs - password_auth - key_auth
            },
            'tags': list(all_tags),
            'port_distribution': port_distribution,
            'config_file': self.config_file
        }

    def export_config(self, file_path: str, names: Optional[List[str]] = None) -> None:
        """
        导出配置到文件

        Args:
            file_path: 导出文件路径
            names: 要导出的配置名称列表，None表示导出所有
        """
        configs_to_export = {}

        if names is None:
            configs_to_export = self.configs
        else:
            for name in names:
                if name in self.configs:
                    configs_to_export[name] = self.configs[name]
                else:
                    logger.warning(f"配置不存在，跳过导出: {name}")

        # 准备导出数据
        export_data = {
            'servers': {
                name: {k: v for k, v in config.to_dict().items() if k != 'name'}
                for name, config in configs_to_export.items()
            }
        }

        # 保存到文件
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                else:
                    yaml.safe_dump(export_data, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"导出配置成功: {file_path}, 共 {len(configs_to_export)} 个配置")

        except Exception as e:
            raise SSHConfigError(f"导出配置失败: {str(e)}")

    def import_config(self, file_path: str, overwrite: bool = False) -> None:
        """
        从文件导入配置

        Args:
            file_path: 导入文件路径
            overwrite: 是否覆盖已存在的配置
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)

            servers = data.get('servers', {})
            imported_count = 0
            skipped_count = 0

            for name, config_data in servers.items():
                if name in self.configs and not overwrite:
                    logger.warning(f"配置已存在，跳过导入: {name}")
                    skipped_count += 1
                    continue

                config_data['name'] = name
                try:
                    server_config = SSHServerConfig.from_dict(config_data)
                    errors = self.validate_config(server_config)

                    if errors:
                        logger.warning(f"配置验证失败，跳过导入 '{name}': {'; '.join(errors)}")
                        skipped_count += 1
                        continue

                    self.configs[name] = server_config
                    imported_count += 1

                except Exception as e:
                    logger.warning(f"解析配置失败，跳过导入 '{name}': {e}")
                    skipped_count += 1

            logger.info(f"导入配置完成: 成功 {imported_count}, 跳过 {skipped_count}")

        except Exception as e:
            raise SSHConfigError(f"导入配置失败: {str(e)}")


# 全局配置管理器实例
_global_config_manager: Optional[ConfigManager] = None


def get_global_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _global_config_manager

    if _global_config_manager is None:
        _global_config_manager = ConfigManager()

    return _global_config_manager


def set_global_config_manager(manager: ConfigManager) -> None:
    """设置全局配置管理器实例"""
    global _global_config_manager
    _global_config_manager = manager
