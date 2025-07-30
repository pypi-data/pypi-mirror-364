#!/usr/bin/env python3
"""
SSH关键字使用Context配置的示例

展示如何在YAML变量文件中配置SSH服务器，并在测试中使用
"""

# 示例YAML变量文件内容 (variables.yaml)
yaml_example = """
# SSH服务器配置
ssh_servers:
  production_server:
    hostname: "prod.example.com"
    port: 22
    username: "deploy"
    private_key_path: "/path/to/prod_key"
    connect_timeout: 15
    
  test_server:
    hostname: "192.168.1.100"
    port: 2222
    username: "testuser"
    password: "testpass123"
    connect_timeout: 10
    
  staging_server:
    hostname: "staging.example.com"
    port: 22
    username: "staging"
    private_key_path: "/path/to/staging_key"
    private_key_password: "keypass"
    connect_timeout: 20

# HTTP客户端配置（对比参考）
http_clients:
  api_server:
    base_url: "https://api.example.com"
    timeout: 30
    headers:
      Authorization: "Bearer token123"
"""

# 示例测试用例
test_case_example = """
# 测试用例示例 (test_ssh_operations.py)

def test_ssh_operations(context):
    '''测试SSH操作'''
    
    # 1. SSH连接 - 自动从context获取production_server配置
    result = SSH连接(context, 服务器="production_server")
    assert result['success'] == True
    
    # 2. 执行命令 - 使用配置中的连接信息
    result = SSH执行命令(
        context,
        服务器="production_server", 
        命令="ls -la /var/log"
    )
    assert result['success'] == True
    assert "access.log" in result['output']
    
    # 3. 参数覆盖 - 可以覆盖配置中的值
    result = SSH执行命令(
        context,
        服务器="test_server",
        命令="whoami",
        端口=3333,  # 覆盖配置中的2222端口
        用户名="override_user"  # 覆盖配置中的testuser
    )
    
    # 4. SFTP文件操作
    result = SFTP上传文件(
        context,
        服务器="staging_server",
        本地文件="/local/path/file.txt",
        远程文件="/remote/path/file.txt"
    )
    assert result['success'] == True
    
    # 5. 批量命令执行
    commands = [
        "cd /tmp",
        "ls -la",
        "df -h"
    ]
    result = SSH批量执行命令(
        context,
        服务器="test_server",
        命令列表=commands
    )
    assert result['success'] == True
    
    # 6. 连接状态查询
    result = SSH连接状态(context, 服务器="production_server")
    print(f"连接状态: {result['message']}")
    
    # 7. 断开连接
    result = SSH断开连接(context, 服务器="production_server")
    assert result['success'] == True

def test_fallback_to_direct_params(context):
    '''测试直接参数回退'''
    
    # 当配置中没有服务器信息时，直接使用参数
    result = SSH连接(
        context,
        服务器="192.168.1.200",  # 直接使用IP
        端口=22,
        用户名="admin",
        密码="admin123"
    )
    assert result['success'] == True
"""

# 配置优先级说明
priority_explanation = """
配置获取优先级说明：

1. Context配置优先级最高
   - 从 context.get("ssh_servers") 获取
   - 支持完整的服务器配置信息

2. 参数覆盖
   - 传入的参数可以覆盖配置中的对应值
   - 例如：配置中port=22，传入port=2222，最终使用2222

3. 全局配置管理器作为后备
   - 如果context中没有找到配置，使用原有的配置管理器
   - 保持向后兼容性

4. 直接参数作为最后选择
   - 如果都没有找到配置，直接使用传入的参数
   - 服务器名称作为hostname使用

调试信息：
- ✓ 找到ssh_servers配置，包含 N 个服务器
- ✓ 找到服务器 'server_name' 的配置
- ⚠️ 未找到服务器 'server_name' 的配置
- ⚠️ 未找到ssh_servers配置，尝试使用全局配置管理器
"""

if __name__ == "__main__":
    print("SSH关键字Context配置使用示例")
    print("=" * 50)
    
    print("\n1. YAML变量文件配置示例:")
    print(yaml_example)
    
    print("\n2. 测试用例示例:")
    print(test_case_example)
    
    print("\n3. 配置优先级说明:")
    print(priority_explanation)
