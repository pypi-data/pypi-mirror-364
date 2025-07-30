# SSH配置自动加载指南

## 概述

pytest-dsl-ssh现在支持从YAML配置文件中自动加载SSH服务器连接信息，让SSH操作更加简洁和易于管理。您不再需要在每个SSH关键字中重复填写连接参数，只需在配置文件中定义一次，然后通过服务器名称引用即可。

## 主要特性

- 🎯 **自动配置加载** - 从YAML配置中自动加载SSH连接信息
- 🔧 **参数覆盖** - 支持在使用时覆盖配置中的默认值
- 📦 **统一管理** - 集中管理所有服务器的连接配置
- 🔄 **多环境支持** - 支持不同环境的配置切换
- 🛡️ **安全性** - 支持私钥认证和密码认证

## 配置文件格式

### 基本配置结构

```yaml
# config/ssh_servers.yaml
ssh_servers:
  server_name:
    hostname: "服务器地址"
    username: "用户名"
    password: "密码"  # 可选，建议使用私钥
    private_key_path: "私钥路径"  # 可选
    port: 22  # 可选，默认22
    description: "服务器描述"  # 可选
    tags: ["标签1", "标签2"]  # 可选
```

### 完整配置示例

```yaml
# SSH服务器配置
ssh_servers:
  # 开发环境服务器
  dev_server:
    hostname: "192.168.1.100"
    username: "developer"
    password: "dev_password"
    port: 22
    description: "开发环境主服务器"
    tags: ["development", "web"]
    
  # 生产环境服务器（使用私钥认证）
  prod_server:
    hostname: "prod.example.com"
    username: "admin"
    private_key_path: "~/.ssh/prod_server_key"
    private_key_password: "key_password"  # 如果私钥有密码
    port: 2222  # 非标准端口
    connect_timeout: 10
    timeout: 60
    compress: true
    keep_alive_interval: 30
    description: "生产环境主服务器"
    tags: ["production", "critical"]
```

### 支持的配置参数

| 参数名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `hostname` | ✅ | - | 服务器地址或IP |
| `username` | ✅ | - | 登录用户名 |
| `password` | ❌ | - | 登录密码 |
| `private_key_path` | ❌ | - | SSH私钥文件路径 |
| `private_key_password` | ❌ | - | 私钥密码（如果有） |
| `port` | ❌ | 22 | SSH端口 |
| `connect_timeout` | ❌ | 10 | 连接超时时间（秒） |
| `timeout` | ❌ | 30 | 操作超时时间（秒） |
| `auto_add_host_keys` | ❌ | true | 是否自动添加主机密钥 |
| `compress` | ❌ | false | 是否启用压缩 |
| `keep_alive_interval` | ❌ | 0 | 保活间隔（秒） |
| `description` | ❌ | - | 服务器描述 |
| `tags` | ❌ | [] | 服务器标签 |

## 使用方法

### 1. 创建配置文件

在项目的`config`目录下创建`ssh_servers.yaml`文件：

```bash
mkdir -p config
cat > config/ssh_servers.yaml << 'EOF'
ssh_servers:
  my_server:
    hostname: "192.168.1.100"
    username: "admin"
    password: "admin123"
    description: "我的测试服务器"
EOF
```

### 2. 在DSL中使用

```python
@name: "SSH配置示例"

# 只需指定服务器名称，其他信息自动从配置加载
连接结果 = [SSH测试连接], 服务器: "my_server"

if ${连接结果.success} do
    # 执行命令
    结果 = [SSH执行命令], 服务器: "my_server", 命令: "ls -la"
    [打印], 内容: "命令输出: ${结果.stdout}"
end
```

### 3. 运行测试

```bash
# 使用配置文件运行
pytest-dsl examples/enhanced_ssh_example.dsl --yaml-vars config/ssh_servers.yaml

# 或者使用pytest方式
pytest test_runner.py --yaml-vars config/ssh_servers.yaml
```

## 高级功能

### 1. 参数覆盖

即使配置了默认值，您仍然可以在使用时覆盖特定参数：

```python
# 使用配置中的默认值
结果1 = [SSH执行命令], 服务器: "my_server", 命令: "whoami"

# 覆盖配置中的端口和用户名
结果2 = [SSH执行命令], 
    服务器: "my_server",
    命令: "whoami",
    端口: 2222,
    用户名: "root"
```

### 2. 多环境配置

您可以为不同环境创建不同的配置文件：

```bash
config/
├── dev_ssh_servers.yaml    # 开发环境
├── test_ssh_servers.yaml   # 测试环境
└── prod_ssh_servers.yaml   # 生产环境
```

然后根据环境选择配置文件：

```bash
# 开发环境
pytest-dsl tests/ --yaml-vars config/dev_ssh_servers.yaml

# 生产环境
pytest-dsl tests/ --yaml-vars config/prod_ssh_servers.yaml
```

### 3. 配置继承

您可以将通用配置和特定配置分开：

```yaml
# config/base_ssh.yaml - 基础配置
ssh_servers:
  base_server: &base_config
    port: 22
    connect_timeout: 10
    timeout: 30
    auto_add_host_keys: true

# config/dev_ssh.yaml - 开发环境配置  
ssh_servers:
  dev_server:
    <<: *base_config
    hostname: "dev.example.com"
    username: "developer"
    password: "dev_pass"
```

### 4. 批量操作

使用配置可以轻松进行批量服务器操作：

```python
@name: "批量服务器检查"

# 定义服务器列表
服务器列表 = ["web_server1", "web_server2", "db_server", "cache_server"]

for 服务器名 in ${服务器列表} do
    # 只需要服务器名，配置自动加载
    连接测试 = [SSH测试连接], 服务器: ${服务器名}
    
    if ${连接测试.success} do
        # 获取系统负载
        负载信息 = [SSH执行命令], 服务器: ${服务器名}, 命令: "uptime"
        [打印], 内容: "${服务器名} 负载: ${负载信息.stdout}"
    else
        [打印], 内容: "${服务器名} 连接失败"
    end
end
```

## 安全最佳实践

### 1. 使用私钥认证

```yaml
ssh_servers:
  secure_server:
    hostname: "secure.example.com"
    username: "admin"
    private_key_path: "~/.ssh/secure_server_key"
    # 不要在配置文件中存储密码
```

### 2. 环境变量

对于敏感信息，可以使用环境变量：

```yaml
ssh_servers:
  prod_server:
    hostname: "${PROD_SERVER_HOST}"
    username: "${PROD_SERVER_USER}"
    private_key_path: "${PROD_SERVER_KEY}"
```

### 3. 文件权限

确保配置文件的权限正确：

```bash
chmod 600 config/ssh_servers.yaml
```

## 故障排除

### 1. 配置未加载

如果配置没有被加载，检查：

- 配置文件路径是否正确
- YAML语法是否正确
- 是否正确使用了`--yaml-vars`参数

### 2. 连接失败

如果连接失败，检查：

- 服务器地址是否正确
- 用户名和密码/私钥是否正确
- 网络连接是否正常
- 防火墙设置

### 3. 调试模式

启用调试日志来查看详细信息：

```bash
# 设置日志级别
export PYTEST_DSL_LOG_LEVEL=DEBUG
pytest-dsl tests/ --yaml-vars config/ssh_servers.yaml
```

## 与旧版本的兼容性

新的配置系统完全向后兼容。您可以：

1. 继续使用旧的方式（手动指定所有参数）
2. 渐进式迁移到新的配置方式
3. 混合使用两种方式

```python
# 旧方式仍然有效
结果1 = [SSH执行命令], 
    服务器: "192.168.1.100",
    用户名: "admin",
    密码: "password",
    命令: "ls"

# 新方式更简洁
结果2 = [SSH执行命令], 服务器: "my_server", 命令: "ls"
```

## 总结

通过SSH配置自动加载功能，您可以：

- ✅ 减少重复配置
- ✅ 提高代码可维护性
- ✅ 简化测试脚本
- ✅ 支持多环境部署
- ✅ 增强安全性

立即开始使用新的SSH配置系统，让您的SSH操作更加高效！ 