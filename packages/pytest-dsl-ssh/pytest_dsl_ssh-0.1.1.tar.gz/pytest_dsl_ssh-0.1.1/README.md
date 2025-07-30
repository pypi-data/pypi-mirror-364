# pytest-dsl-ssh

基于 pytest-dsl 框架的 SSH/SFTP 自动化测试关键字插件。提供SSH远程命令执行、SFTP文件传输等功能。

## 特性

- 🔐 支持密码和密钥认证 
- 🌐 灵活的服务器配置管理
- 📦 连接池复用连接
- 🔄 支持SFTP文件传输
- 📝 中文路径/文件名支持
- 🎯 自动配置加载
- 💡 丰富的错误处理

## 安装

### 使用 uv 进行包管理和依赖安装

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或者 .venv\Scripts\activate  # Windows

# 安装包
uv pip install .
```

### 使用 pip 安装

```bash
pip install .
```

## 快速开始

1. 创建服务器配置文件 `config/ssh_servers.yaml`:

```yaml
ssh_servers:
  test_server:  # 测试服务器（支持SSH和SFTP）
    hostname: "localhost"
    username: "testuser"
    password: "testpass123"
    port: 2222
    description: "SSH/SFTP测试服务器"
    tags: ["ssh", "sftp", "test"]

  prod_server:  # 生产服务器示例（使用私钥认证）
    hostname: "prod.example.com"
    username: "admin"
    private_key_path: "~/.ssh/id_rsa"
    port: 22
    description: "生产环境服务器"
    tags: ["production", "ssh", "sftp"]
```

2. 创建测试用例 `tests/dsl/test_ssh.dsl`:

```dsl
@name: "SSH/SFTP基本功能测试"
@description: "测试SSH连接、命令执行和SFTP文件传输功能"
@tags: ["ssh", "sftp", "basic", "connection"]

# SSH基本操作
连接结果 = [SSH测试连接], 服务器: "test_server"
命令结果 = [SSH执行命令], 服务器: "test_server", 命令: "echo 'Hello from SSH!'"

# SFTP文件传输（使用同一个服务器）
上传结果 = [SFTP上传文件], 服务器: "test_server", 本地文件: "test.txt", 远程文件: "/upload/test.txt"
```

注意: DSL语法中参数之间使用逗号和空格分隔。

3. 运行测试:

```bash
pytest-dsl tests/dsl/test_ssh.dsl
```

## 支持的关键字

### SSH 关键字

- `SSH连接` - 建立SSH连接
- `SSH测试连接` - 测试SSH连接和基本命令  
- `SSH执行命令` - 执行单条SSH命令
- `SSH批量执行命令` - 执行多条SSH命令
- `SSH连接状态` - 查询SSH连接状态
- `SSH断开连接` - 断开SSH连接

### SFTP 关键字

- `SFTP上传文件` - 上传单个文件
- `SFTP下载文件` - 下载单个文件
- `SFTP上传目录` - 递归上传目录
- `SFTP下载目录` - 递归下载目录  
- `SFTP创建目录` - 创建远程目录
- `SFTP删除文件` - 删除远程文件
- `SFTP删除目录` - 删除远程目录
- `SFTP列出目录` - 获取目录列表
- `SFTP文件信息` - 获取文件属性

## DSL示例

### SSH命令执行

```dsl
# 创建目录并写入文件
创建结果 = [SSH执行命令], 服务器: "test_server", 命令: "mkdir -p /tmp/test && echo 'hello' > /tmp/test/hello.txt"

# 读取文件内容
读取结果 = [SSH执行命令], 服务器: "test_server", 命令: "cat /tmp/test/hello.txt"
```

### SFTP文件传输

```dsl
# 上传目录
上传结果 = [SFTP上传目录], 服务器: "test_server", 本地目录: "test_data", 远程目录: "/upload/test", 保持时间戳: true

# 下载并检查文件
下载结果 = [SFTP下载文件], 服务器: "test_server", 远程文件: "/upload/test.txt", 本地文件: "download/test.txt"
```

## 服务器配置说明

**重要提示**：SSH和SFTP通常使用同一个连接和端口，因此一个服务器配置可以同时用于SSH命令执行和SFTP文件传输操作。

服务器配置支持以下字段:

- `hostname` - 服务器地址
- `port` - SSH端口(默认22)
- `username` - 登录用户名
- `password` - 登录密码
- `private_key_path` - 私钥路径
- `private_key_password` - 私钥密码
- `connect_timeout` - 连接超时时间(默认10s)
- `timeout` - 命令超时时间(默认30s)
- `compress` - 是否启用压缩
- `description` - 服务器描述
- `tags` - 服务器标签

## 开发环境

### 使用 uv 进行项目依赖管理

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或者 .venv\Scripts\activate  # Windows

# 开发模式安装
uv pip install -e .

# 安装开发依赖
uv pip install -e ".[dev,test]"
```

### 启动测试环境

项目提供了Docker测试环境，可以快速启动SSH/SFTP测试服务器：

```bash
# 启动测试服务器
docker-compose up -d

# 查看服务状态
docker-compose ps

# 停止测试服务器
docker-compose down
```

测试服务器信息：
- SSH/SFTP服务器：`localhost:2222` (用户名: testuser, 密码: testpass123)
- 备用SSH服务器：`localhost:2223` (用户名: testuser, 密码: testpass123)

### 运行测试

```bash
# 运行单元测试
pytest tests/unit/

# 运行集成测试（需要Docker环境）
pytest tests/integration/

# 运行DSL测试
pytest-dsl tests/dsl/
```

## 更多文档

- [SSH配置指南](docs/SSH_CONFIG_GUIDE.md)

## 许可证

MIT
