"""
测试YAML配置加载器
"""

import pytest
from unittest.mock import Mock, patch
from pytest_dsl_ssh.core.yaml_config_loader import YAMLConfigLoader, get_global_yaml_loader
from pytest_dsl_ssh.core.config_manager import SSHServerConfig


class TestYAMLConfigLoader:
    """YAML配置加载器测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.loader = YAMLConfigLoader()
    
    def test_init(self):
        """测试初始化"""
        assert self.loader._loaded_servers == {}
    
    @patch('pytest_dsl_ssh.core.yaml_config_loader.logger')
    def test_load_from_yaml_vars_no_config(self, mock_logger):
        """测试没有配置时的处理"""
        with patch.object(self.loader, '_get_ssh_configs_from_context', return_value=None):
            result = self.loader.load_from_yaml_vars()
            
            assert result == {}
            assert self.loader._loaded_servers == {}
            mock_logger.info.assert_called_with("未找到SSH服务器配置")
    
    def test_load_from_yaml_vars_valid_config(self):
        """测试加载有效配置"""
        mock_config = {
            'test_server': {
                'hostname': '192.168.1.100',
                'username': 'testuser',
                'password': 'testpass',
                'port': 22
            },
            'prod_server': {
                'hostname': 'prod.example.com',
                'username': 'admin',
                'private_key_path': '~/.ssh/prod_key',
                'port': 2222
            }
        }
        
        with patch.object(self.loader, '_get_ssh_configs_from_context', return_value=mock_config):
            result = self.loader.load_from_yaml_vars()
            
            assert len(result) == 2
            assert 'test_server' in result
            assert 'prod_server' in result
            
            # 验证test_server配置
            test_config = result['test_server']
            assert isinstance(test_config, SSHServerConfig)
            assert test_config.hostname == '192.168.1.100'
            assert test_config.username == 'testuser'
            assert test_config.password == 'testpass'
            assert test_config.port == 22
            
            # 验证prod_server配置
            prod_config = result['prod_server']
            assert isinstance(prod_config, SSHServerConfig)
            assert prod_config.hostname == 'prod.example.com'
            assert prod_config.username == 'admin'
            assert prod_config.private_key_path == '~/.ssh/prod_key'
            assert prod_config.port == 2222
    
    def test_load_from_yaml_vars_invalid_config(self):
        """测试加载无效配置"""
        mock_config = {
            'invalid_server': 'not_a_dict',  # 无效的配置格式
            'missing_hostname': {
                'username': 'user'
                # 缺少必需的hostname字段
            },
            'valid_server': {
                'hostname': 'valid.example.com',
                'username': 'validuser'
            }
        }
        
        with patch.object(self.loader, '_get_ssh_configs_from_context', return_value=mock_config):
            result = self.loader.load_from_yaml_vars()
            
            # 只有valid_server应该被成功加载
            assert len(result) == 1
            assert 'valid_server' in result
            assert 'invalid_server' not in result
            assert 'missing_hostname' not in result
    
    def test_create_server_config_basic(self):
        """测试创建基本服务器配置"""
        config_data = {
            'hostname': 'test.example.com',
            'username': 'testuser',
            'password': 'testpass'
        }
        
        result = self.loader._create_server_config('test_server', config_data)
        
        assert isinstance(result, SSHServerConfig)
        assert result.name == 'test_server'
        assert result.hostname == 'test.example.com'
        assert result.username == 'testuser'
        assert result.password == 'testpass'
        assert result.port == 22  # 默认值
        assert result.connect_timeout == 10  # 默认值
    
    def test_create_server_config_full(self):
        """测试创建完整服务器配置"""
        config_data = {
            'hostname': 'full.example.com',
            'username': 'admin',
            'private_key_path': '~/.ssh/full_key',
            'private_key_password': 'key_pass',
            'port': 2222,
            'connect_timeout': 15,
            'timeout': 45,
            'compress': True,
            'keep_alive_interval': 60,
            'description': 'Full configuration server',
            'tags': ['production', 'critical']
        }
        
        result = self.loader._create_server_config('full_server', config_data)
        
        assert isinstance(result, SSHServerConfig)
        assert result.name == 'full_server'
        assert result.hostname == 'full.example.com'
        assert result.username == 'admin'
        assert result.private_key_path == '~/.ssh/full_key'
        assert result.private_key_password == 'key_pass'
        assert result.port == 2222
        assert result.connect_timeout == 15
        assert result.timeout == 45
        assert result.compress is True
        assert result.keep_alive_interval == 60
        assert result.description == 'Full configuration server'
        assert result.tags == ['production', 'critical']
    
    def test_create_server_config_alternative_fields(self):
        """测试创建服务器配置（使用备用字段名）"""
        config_data = {
            'host': 'alt.example.com',  # 使用host而不是hostname
            'username': 'altuser',
            'key_file': '~/.ssh/alt_key',  # 使用key_file而不是private_key_path
            'key_password': 'alt_key_pass'  # 使用key_password而不是private_key_password
        }
        
        result = self.loader._create_server_config('alt_server', config_data)
        
        assert isinstance(result, SSHServerConfig)
        assert result.hostname == 'alt.example.com'
        assert result.private_key_path == '~/.ssh/alt_key'
        assert result.private_key_password == 'alt_key_pass'
    
    def test_create_server_config_missing_hostname(self):
        """测试创建缺少hostname的配置"""
        config_data = {
            'username': 'user',
            'password': 'pass'
            # 缺少hostname/host字段
        }
        
        result = self.loader._create_server_config('no_host_server', config_data)
        
        assert result is None
    
    def test_get_ssh_configs_from_context_global_context(self):
        """测试从全局上下文获取SSH配置"""
        mock_context = Mock()
        mock_context.get_variable.return_value = {'server1': {'hostname': 'test.com'}}
        
        with patch('pytest_dsl_ssh.core.yaml_config_loader.global_context', mock_context):
            result = self.loader._get_ssh_configs_from_context()
            
            assert result == {'server1': {'hostname': 'test.com'}}
            mock_context.get_variable.assert_called_with('ssh_servers')
    
    def test_get_ssh_configs_from_context_yaml_vars(self):
        """测试从YAML变量管理器获取SSH配置"""
        mock_yaml_vars = Mock()
        mock_yaml_vars.get_variable.return_value = {'server2': {'hostname': 'yaml.com'}}
        
        with patch('pytest_dsl_ssh.core.yaml_config_loader.global_context') as mock_global_context:
            mock_global_context.get_variable.return_value = None  # 全局上下文没有配置
            
            with patch('pytest_dsl_ssh.core.yaml_config_loader.yaml_vars', mock_yaml_vars):
                result = self.loader._get_ssh_configs_from_context()
                
                assert result == {'server2': {'hostname': 'yaml.com'}}
                mock_yaml_vars.get_variable.assert_called_with('ssh_servers')
    
    def test_get_ssh_configs_from_context_test_context(self):
        """测试从测试上下文获取SSH配置"""
        mock_context = Mock()
        mock_context.get_variable.return_value = {'server3': {'hostname': 'context.com'}}
        
        with patch('pytest_dsl_ssh.core.yaml_config_loader.global_context') as mock_global_context:
            mock_global_context.get_variable.return_value = None
            
            with patch('pytest_dsl_ssh.core.yaml_config_loader.yaml_vars') as mock_yaml_vars:
                mock_yaml_vars.get_variable.return_value = None
                
                with patch('pytest_dsl_ssh.core.yaml_config_loader.get_current_context', return_value=mock_context):
                    result = self.loader._get_ssh_configs_from_context()
                    
                    assert result == {'server3': {'hostname': 'context.com'}}
                    mock_context.get_variable.assert_called_with('ssh_servers')
    
    def test_get_ssh_configs_from_context_no_source(self):
        """测试所有源都不可用时的处理"""
        with patch('pytest_dsl_ssh.core.yaml_config_loader.global_context') as mock_global_context:
            mock_global_context.get_variable.side_effect = ImportError("Not available")
            
            with patch('pytest_dsl_ssh.core.yaml_config_loader.yaml_vars') as mock_yaml_vars:
                mock_yaml_vars.get_variable.side_effect = ImportError("Not available")
                
                with patch('pytest_dsl_ssh.core.yaml_config_loader.get_current_context') as mock_get_context:
                    mock_get_context.side_effect = ImportError("Not available")
                    
                    result = self.loader._get_ssh_configs_from_context()
                    
                    assert result is None
    
    def test_get_loaded_servers(self):
        """测试获取已加载的服务器"""
        # 设置一些测试数据
        mock_config = SSHServerConfig(name='test', hostname='test.com')
        self.loader._loaded_servers = {'test': mock_config}
        
        result = self.loader.get_loaded_servers()
        
        assert len(result) == 1
        assert 'test' in result
        assert result['test'] == mock_config
        
        # 确保返回的是副本，修改不会影响原始数据
        result['test2'] = Mock()
        assert 'test2' not in self.loader._loaded_servers
    
    def test_get_server(self):
        """测试获取指定服务器"""
        mock_config = SSHServerConfig(name='test', hostname='test.com')
        self.loader._loaded_servers = {'test': mock_config}
        
        result = self.loader.get_server('test')
        assert result == mock_config
        
        result = self.loader.get_server('nonexistent')
        assert result is None
    
    def test_refresh_config(self):
        """测试刷新配置"""
        with patch.object(self.loader, 'load_from_yaml_vars', return_value={'refreshed': Mock()}) as mock_load:
            result = self.loader.refresh_config()
            
            assert result == {'refreshed': Mock()}
            mock_load.assert_called_once()


class TestGlobalYAMLLoader:
    """全局YAML加载器测试"""
    
    def test_get_global_yaml_loader_singleton(self):
        """测试全局YAML加载器是单例模式"""
        loader1 = get_global_yaml_loader()
        loader2 = get_global_yaml_loader()
        
        assert loader1 is loader2
        assert isinstance(loader1, YAMLConfigLoader)
    
    @patch('pytest_dsl_ssh.core.yaml_config_loader._global_yaml_loader', None)
    def test_get_global_yaml_loader_initialization(self):
        """测试全局YAML加载器的初始化"""
        with patch.object(YAMLConfigLoader, 'load_from_yaml_vars') as mock_load:
            loader = get_global_yaml_loader()
            
            assert isinstance(loader, YAMLConfigLoader)
            mock_load.assert_called_once()  # 确保初始化时加载了配置


if __name__ == '__main__':
    pytest.main([__file__]) 