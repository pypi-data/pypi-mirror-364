"""
YAML配置加载器

从pytest-dsl的YAML变量系统中加载SSH服务器配置，
实现配置的自动发现和加载
"""

import logging
from typing import Dict, Optional, Any
from pytest_dsl_ssh.core.config_manager import SSHServerConfig

logger = logging.getLogger(__name__)


class YAMLConfigLoader:
    """YAML配置加载器

    从pytest-dsl的YAML变量系统中加载SSH服务器配置
    """

    def __init__(self):
        self._loaded_servers: Dict[str, SSHServerConfig] = {}

    def load_from_yaml_vars(self) -> Dict[str, SSHServerConfig]:
        """从pytest-dsl的YAML变量系统中加载SSH配置

        支持的配置结构：
        ssh_servers:
          server1:
            hostname: "192.168.1.100"
            username: "root"
            password: "password"
            port: 22
          server2:
            hostname: "test.example.com"
            username: "testuser"
            private_key_path: "~/.ssh/id_rsa"

        Returns:
            Dict[str, SSHServerConfig]: 加载的服务器配置字典
        """
        try:
            # 尝试从pytest-dsl的全局上下文获取SSH配置
            ssh_configs = self._get_ssh_configs_from_context()

            if not ssh_configs:
                logger.info("未找到SSH服务器配置")
                return {}

            loaded_configs = {}

            # 解析配置
            for server_name, config_data in ssh_configs.items():
                try:
                    # 确保必需的字段存在
                    if not isinstance(config_data, dict):
                        logger.warning(f"SSH服务器配置 '{server_name}' 格式无效，跳过")
                        continue

                    # 创建SSH服务器配置对象
                    server_config = self._create_server_config(server_name, config_data)
                    if server_config:
                        loaded_configs[server_name] = server_config
                        logger.info(f"成功加载SSH服务器配置: {server_name}")

                except Exception as e:
                    logger.error(f"加载SSH服务器配置 '{server_name}' 失败: {e}")
                    continue

            self._loaded_servers = loaded_configs
            logger.info(f"总共加载了 {len(loaded_configs)} 个SSH服务器配置")

            return loaded_configs

        except Exception as e:
            logger.error(f"从YAML变量加载SSH配置失败: {e}")
            return {}

    def _get_ssh_configs_from_context(self) -> Optional[Dict[str, Any]]:
        """从pytest-dsl全局上下文获取SSH配置"""
        try:
            # 方法1：尝试从全局上下文获取
            from pytest_dsl.core.global_context import global_context
            ssh_configs = global_context.get_variable('ssh_servers')

            if ssh_configs:
                logger.debug("从全局上下文获取到SSH配置")
                return ssh_configs

        except ImportError:
            logger.debug("pytest-dsl全局上下文不可用")
        except Exception as e:
            logger.debug(f"从全局上下文获取SSH配置失败: {e}")

        try:
            # 方法2：尝试从YAML变量管理器获取
            from pytest_dsl.core.yaml_vars import yaml_vars
            ssh_configs = yaml_vars.get_variable('ssh_servers')

            if ssh_configs:
                logger.debug("从YAML变量管理器获取到SSH配置")
                return ssh_configs

        except ImportError:
            logger.debug("pytest-dsl YAML变量管理器不可用")
        except Exception as e:
            logger.debug(f"从YAML变量管理器获取SSH配置失败: {e}")

        try:
            # 方法3：尝试从当前测试上下文获取
            from pytest_dsl.core.context import get_current_context
            context = get_current_context()
            ssh_configs = context.get_variable('ssh_servers')

            if ssh_configs:
                logger.debug("从当前测试上下文获取到SSH配置")
                return ssh_configs

        except ImportError:
            logger.debug("pytest-dsl测试上下文不可用")
        except Exception as e:
            logger.debug(f"从测试上下文获取SSH配置失败: {e}")

        return None

    def _create_server_config(self, name: str, config_data: Dict[str, Any]) -> Optional[SSHServerConfig]:
        """创建SSH服务器配置对象

        Args:
            name: 服务器名称
            config_data: 配置数据

        Returns:
            SSHServerConfig: 服务器配置对象，失败返回None
        """
        try:
            # 检查必需字段
            hostname = config_data.get('hostname') or config_data.get('host')
            if not hostname:
                logger.error(f"SSH服务器配置 '{name}' 缺少hostname字段")
                return None

            # 创建配置对象，使用默认值
            server_config = SSHServerConfig(
                name=name,
                hostname=hostname,
                port=config_data.get('port', 22),
                username=config_data.get('username'),
                password=config_data.get('password'),
                private_key_path=config_data.get('private_key_path') or config_data.get('key_file'),
                private_key_password=config_data.get('private_key_password') or config_data.get('key_password'),
                timeout=config_data.get('timeout', 30),
                connect_timeout=config_data.get('connect_timeout', 10),
                auto_add_host_keys=config_data.get('auto_add_host_keys', True),
                compress=config_data.get('compress', False),
                keep_alive_interval=config_data.get('keep_alive_interval', 0),
                description=config_data.get('description'),
                tags=config_data.get('tags', [])
            )

            return server_config

        except Exception as e:
            logger.error(f"创建SSH服务器配置对象失败: {e}")
            return None

    def get_loaded_servers(self) -> Dict[str, SSHServerConfig]:
        """获取已加载的服务器配置"""
        return self._loaded_servers.copy()

    def get_server(self, name: str) -> Optional[SSHServerConfig]:
        """获取指定名称的服务器配置"""
        return self._loaded_servers.get(name)

    def refresh_config(self) -> Dict[str, SSHServerConfig]:
        """刷新配置，重新从YAML变量系统加载"""
        return self.load_from_yaml_vars()


# 全局YAML配置加载器实例
_global_yaml_loader = None


def get_global_yaml_loader() -> YAMLConfigLoader:
    """获取全局YAML配置加载器实例"""
    global _global_yaml_loader
    if _global_yaml_loader is None:
        _global_yaml_loader = YAMLConfigLoader()
        # 初始化时加载配置
        _global_yaml_loader.load_from_yaml_vars()
    return _global_yaml_loader


def set_global_yaml_loader(loader: YAMLConfigLoader) -> None:
    """设置全局YAML配置加载器实例"""
    global _global_yaml_loader
    _global_yaml_loader = loader
