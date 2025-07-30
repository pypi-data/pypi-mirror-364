"""
完整的集成测试

测试统一配置管理器与关键字的集成
"""

import pytest
from unittest.mock import Mock, patch
from pytest_dsl_ssh.core.unified_config import get_ssh_connection_config


class MockContext:
    """模拟测试上下文"""
    
    def __init__(self, ssh_servers=None):
        self.data = {
            'ssh_servers': ssh_servers or {}
        }
    
    def get(self, key, default=None):
        return self.data.get(key, default)


class TestConfigurationIntegration:
    """配置管理器集成测试"""

    def test_config_retrieval_with_real_context(self):
        """测试使用真实context结构的配置获取"""
        # 准备测试数据
        ssh_servers_config = {
            'test_server': {
                'hostname': '192.168.1.100',
                'port': 2222,
                'username': 'testuser',
                'password': 'testpass',
                'connect_timeout': 15
            }
        }

        context = MockContext(ssh_servers_config)

        # 测试配置获取
        config = get_ssh_connection_config(context, 'test_server')

        # 验证配置
        assert config.hostname == '192.168.1.100'
        assert config.port == 2222
        assert config.username == 'testuser'
        assert config.password == 'testpass'
        assert config.connect_timeout == 15
    
    def test_config_with_private_key(self):
        """测试包含私钥的配置获取"""
        # 准备测试数据
        ssh_servers_config = {
            'prod_server': {
                'hostname': 'prod.example.com',
                'port': 22,
                'username': 'admin',
                'private_key_path': '/path/to/key',
                'connect_timeout': 20
            }
        }

        context = MockContext(ssh_servers_config)

        # 测试配置获取
        config = get_ssh_connection_config(context, 'prod_server')

        # 验证配置
        assert config.hostname == 'prod.example.com'
        assert config.port == 22
        assert config.username == 'admin'
        assert config.password is None
        assert config.private_key_path == '/path/to/key'
        assert config.connect_timeout == 20
    
    def test_parameter_override_context_config(self):
        """测试参数覆盖context配置"""
        # 准备测试数据
        ssh_servers_config = {
            'test_server': {
                'hostname': '192.168.1.100',
                'port': 22,
                'username': 'defaultuser',
                'password': 'defaultpass'
            }
        }

        context = MockContext(ssh_servers_config)

        # 测试参数覆盖
        config = get_ssh_connection_config(
            context,
            'test_server',
            port=3333,  # 覆盖配置中的22
            username='overrideuser'  # 覆盖配置中的defaultuser
        )

        # 验证配置（应该使用覆盖的值）
        assert config.hostname == '192.168.1.100'  # 来自配置
        assert config.port == 3333  # 被覆盖
        assert config.username == 'overrideuser'  # 被覆盖
        assert config.password == 'defaultpass'  # 来自配置
    
    def test_direct_parameters_when_no_context_config(self):
        """测试没有context配置时使用直接参数"""
        # 空的context
        context = MockContext()

        # 测试直接参数
        config = get_ssh_connection_config(
            context,
            'direct.example.com',
            port=2222,
            username='directuser',
            password='directpass'
        )

        # 验证配置（应该使用直接参数）
        assert config.hostname == 'direct.example.com'
        assert config.port == 2222
        assert config.username == 'directuser'
        assert config.password == 'directpass'


class TestComplexScenarios:
    """复杂场景测试"""

    def test_multiple_servers_config(self):
        """测试多服务器配置"""
        # 准备测试数据
        ssh_servers_config = {
            'web_server': {
                'hostname': 'web.example.com',
                'port': 22,
                'username': 'webuser',
                'password': 'webpass'
            },
            'db_server': {
                'hostname': 'db.example.com',
                'port': 3306,
                'username': 'dbuser',
                'private_key_path': '/path/to/db_key'
            },
            'file_server': {
                'hostname': 'files.example.com',
                'port': 2222,
                'username': 'fileuser',
                'password': 'filepass'
            }
        }

        context = MockContext(ssh_servers_config)

        # 测试不同服务器的配置获取
        web_config = get_ssh_connection_config(context, 'web_server')
        db_config = get_ssh_connection_config(context, 'db_server')
        file_config = get_ssh_connection_config(context, 'file_server')

        # 验证web服务器配置
        assert web_config.hostname == 'web.example.com'
        assert web_config.port == 22
        assert web_config.username == 'webuser'
        assert web_config.password == 'webpass'

        # 验证数据库服务器配置
        assert db_config.hostname == 'db.example.com'
        assert db_config.port == 3306
        assert db_config.username == 'dbuser'
        assert db_config.private_key_path == '/path/to/db_key'

        # 验证文件服务器配置
        assert file_config.hostname == 'files.example.com'
        assert file_config.port == 2222
        assert file_config.username == 'fileuser'
        assert file_config.password == 'filepass'
