"""
统一配置管理器单元测试
"""

import pytest
from unittest.mock import Mock
from pytest_dsl_ssh.core.unified_config import (
    SSHConnectionConfig,
    UnifiedSSHConfigManager,
    get_unified_config_manager,
    get_ssh_connection_config
)


class TestSSHConnectionConfig:
    """SSH连接配置测试"""
    
    def test_default_values(self):
        """测试默认值"""
        config = SSHConnectionConfig(hostname="test.example.com")
        
        assert config.hostname == "test.example.com"
        assert config.port == 22
        assert config.username is None
        assert config.password is None
        assert config.private_key_path is None
        assert config.private_key_password is None
        assert config.connect_timeout == 10
    
    def test_custom_values(self):
        """测试自定义值"""
        config = SSHConnectionConfig(
            hostname="custom.example.com",
            port=2222,
            username="testuser",
            password="testpass",
            private_key_path="/path/to/key",
            private_key_password="keypass",
            connect_timeout=30
        )
        
        assert config.hostname == "custom.example.com"
        assert config.port == 2222
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.private_key_path == "/path/to/key"
        assert config.private_key_password == "keypass"
        assert config.connect_timeout == 30
    
    def test_to_dict(self):
        """测试转换为字典"""
        config = SSHConnectionConfig(
            hostname="test.example.com",
            port=2222,
            username="testuser"
        )
        
        result = config.to_dict()
        expected = {
            'hostname': 'test.example.com',
            'port': 2222,
            'username': 'testuser',
            'password': None,
            'private_key_path': None,
            'private_key_password': None,
            'connect_timeout': 10
        }
        
        assert result == expected


class TestUnifiedSSHConfigManager:
    """统一SSH配置管理器测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.manager = UnifiedSSHConfigManager()
    
    def test_get_config_from_context_success(self):
        """测试从context成功获取配置"""
        # 模拟context
        mock_context = Mock()
        mock_context.get.return_value = {
            'test_server': {
                'hostname': '192.168.1.100',
                'port': 2222,
                'username': 'testuser',
                'password': 'testpass',
                'connect_timeout': 15
            }
        }
        
        config = self.manager.get_connection_config(mock_context, 'test_server')
        
        assert config.hostname == '192.168.1.100'
        assert config.port == 2222
        assert config.username == 'testuser'
        assert config.password == 'testpass'
        assert config.connect_timeout == 15
    
    def test_get_config_from_context_with_overrides(self):
        """测试从context获取配置并覆盖参数"""
        # 模拟context
        mock_context = Mock()
        mock_context.get.return_value = {
            'test_server': {
                'hostname': '192.168.1.100',
                'port': 2222,
                'username': 'testuser',
                'password': 'testpass'
            }
        }
        
        # 覆盖端口和用户名
        config = self.manager.get_connection_config(
            mock_context, 'test_server',
            port=3333,
            username='override_user'
        )
        
        assert config.hostname == '192.168.1.100'  # 来自配置
        assert config.port == 3333  # 被覆盖
        assert config.username == 'override_user'  # 被覆盖
        assert config.password == 'testpass'  # 来自配置
    
    def test_get_config_context_not_found(self):
        """测试context中找不到服务器配置"""
        # 模拟context，但没有目标服务器
        mock_context = Mock()
        mock_context.get.return_value = {
            'other_server': {
                'hostname': '192.168.1.200'
            }
        }
        
        config = self.manager.get_connection_config(mock_context, 'test_server')
        
        # 应该使用直接参数
        assert config.hostname == 'test_server'
        assert config.port == 22
        assert config.username is None
    
    def test_get_config_no_context(self):
        """测试没有context的情况"""
        mock_context = Mock()
        mock_context.get.return_value = None
        
        config = self.manager.get_connection_config(
            mock_context, 'direct.example.com',
            port=2222,
            username='directuser'
        )
        
        # 应该使用直接参数
        assert config.hostname == 'direct.example.com'
        assert config.port == 2222
        assert config.username == 'directuser'
    
    def test_get_config_context_exception(self):
        """测试context获取异常的情况"""
        # 模拟context抛出异常
        mock_context = Mock()
        mock_context.get.side_effect = Exception("Context error")
        
        config = self.manager.get_connection_config(
            mock_context, 'fallback.example.com',
            username='fallbackuser'
        )
        
        # 应该回退到直接参数
        assert config.hostname == 'fallback.example.com'
        assert config.username == 'fallbackuser'


class TestGlobalFunctions:
    """全局函数测试"""
    
    def test_get_unified_config_manager_singleton(self):
        """测试全局配置管理器单例"""
        manager1 = get_unified_config_manager()
        manager2 = get_unified_config_manager()
        
        assert manager1 is manager2
    
    def test_get_ssh_connection_config_convenience(self):
        """测试便捷函数"""
        mock_context = Mock()
        mock_context.get.return_value = {
            'test_server': {
                'hostname': 'convenience.example.com',
                'username': 'convuser'
            }
        }
        
        config = get_ssh_connection_config(mock_context, 'test_server')
        
        assert config.hostname == 'convenience.example.com'
        assert config.username == 'convuser'


class TestConfigPriority:
    """配置优先级测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.manager = UnifiedSSHConfigManager()
    
    def test_parameter_overrides_context(self):
        """测试参数覆盖context配置"""
        mock_context = Mock()
        mock_context.get.return_value = {
            'test_server': {
                'hostname': 'context.example.com',
                'port': 22,
                'username': 'contextuser',
                'password': 'contextpass'
            }
        }
        
        config = self.manager.get_connection_config(
            mock_context, 'test_server',
            port=3333,  # 覆盖端口
            username='paramuser',  # 覆盖用户名
            private_key_path='/param/key'  # 添加新参数
        )
        
        assert config.hostname == 'context.example.com'  # 来自context
        assert config.port == 3333  # 参数覆盖
        assert config.username == 'paramuser'  # 参数覆盖
        assert config.password == 'contextpass'  # 来自context
        assert config.private_key_path == '/param/key'  # 来自参数
    
    def test_none_values_dont_override(self):
        """测试None值不会覆盖配置"""
        mock_context = Mock()
        mock_context.get.return_value = {
            'test_server': {
                'hostname': 'context.example.com',
                'port': 2222,
                'username': 'contextuser'
            }
        }
        
        config = self.manager.get_connection_config(
            mock_context, 'test_server',
            port=None,  # None值不应该覆盖
            username=None,  # None值不应该覆盖
            password='newpass'  # 非None值应该设置
        )
        
        assert config.hostname == 'context.example.com'
        assert config.port == 2222  # 保持context值
        assert config.username == 'contextuser'  # 保持context值
        assert config.password == 'newpass'  # 使用参数值
