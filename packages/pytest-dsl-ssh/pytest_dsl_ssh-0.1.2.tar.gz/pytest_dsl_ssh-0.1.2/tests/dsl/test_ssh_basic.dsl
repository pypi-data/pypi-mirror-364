@name: "SSH基本功能测试"
@description: "测试SSH连接、命令执行和状态查询功能"
@tags: ["ssh", "basic", "connection", "command"]

# 测试变量
test_command = "echo 'Hello from SSH!'"
test_directory = "/tmp/pytest_dsl_test"
test_file = "test_output.txt"

# 测试SSH连接
[打印], 内容: "🔗 开始测试SSH连接..."
连接结果 = [SSH测试连接], 服务器: "test_server"

if ${连接结果.success} do
    [打印], 内容: "✅ SSH连接测试成功"
    [打印], 内容: "连接信息: ${连接结果.message}"
else
    [打印], 内容: "❌ SSH连接测试失败: ${连接结果.error}"
    [断言], 条件: "False", 消息: "SSH连接失败"
end

# 测试基本命令执行
[打印], 内容: "🚀 测试基本命令执行..."
命令结果 = [SSH执行命令], 服务器: "test_server", 命令: ${test_command}

if ${命令结果.success} do
    [打印], 内容: "✅ 命令执行成功"
    [打印], 内容: "输出: ${命令结果.stdout}"
    [断言], 条件: "${命令结果.stdout} contains Hello from SSH!", 消息: "命令输出不正确"
else
    [打印], 内容: "❌ 命令执行失败: ${命令结果.error}"
    [断言], 条件: "False", 消息: "命令执行失败"
end

# 测试文件系统操作
[打印], 内容: "📁 测试文件系统操作..."
创建目录结果 = [SSH执行命令], 服务器: "test_server", 命令: "mkdir -p ${test_directory}"

if ${创建目录结果.success} do
    [打印], 内容: "✅ 创建目录成功"
else
    [打印], 内容: "❌ 创建目录失败: ${创建目录结果.error}"
end

# 测试文件写入
写入命令 = "echo 'Test content from pytest-dsl' > ${test_directory}/${test_file}"
写入结果 = [SSH执行命令], 服务器: "test_server", 命令: ${写入命令}

if ${写入结果.success} do
    [打印], 内容: "✅ 文件写入成功"
else
    [打印], 内容: "❌ 文件写入失败: ${写入结果.error}"
end

# 测试文件读取
读取结果 = [SSH执行命令], 服务器: "test_server", 命令: "cat ${test_directory}/${test_file}"

if ${读取结果.success} do
    [打印], 内容: "✅ 文件读取成功"
    [打印], 内容: "文件内容: ${读取结果.stdout}"
    [断言], 条件: "${读取结果.stdout} contains 'Test content from pytest-dsl'", 消息: "文件内容不正确"
else
    [打印], 内容: "❌ 文件读取失败: ${读取结果.error}"
end

# 测试批量命令执行
[打印], 内容: "📦 测试批量命令执行..."

# 执行几个简单的命令来测试批量功能
第一个命令结果 = [SSH执行命令], 服务器: "test_server", 命令: "whoami"
[打印], 内容: "命令1 - whoami: ${第一个命令结果.stdout}"

第二个命令结果 = [SSH执行命令], 服务器: "test_server", 命令: "pwd"
[打印], 内容: "命令2 - pwd: ${第二个命令结果.stdout}"

第三个命令结果 = [SSH执行命令], 服务器: "test_server", 命令: "date"
[打印], 内容: "命令3 - date: ${第三个命令结果.stdout}"

[打印], 内容: "✅ 多个命令执行测试完成"

# 测试SSH连接状态查询
[打印], 内容: "📊 测试SSH连接状态查询..."
状态结果 = [SSH连接状态], 服务器: "test_server"

if ${状态结果.success} do
    [打印], 内容: "✅ 连接状态查询成功"
    [打印], 内容: "连接状态: ${状态结果}"
    [打印], 内容: "连接时间: ${状态结果}"
else
    [打印], 内容: "❌ 连接状态查询失败: ${状态结果}"
end

# 测试错误处理
[打印], 内容: "⚠️ 测试错误处理..."
错误命令结果 = [SSH执行命令], 服务器: "test_server", 命令: "nonexistent_command_12345"

if ${错误命令结果.success} do
    [打印], 内容: "⚠️ 错误命令意外成功"
else
    [打印], 内容: "✅ 错误命令正确失败"
    [打印], 内容: "错误信息: ${错误命令结果.error}"
    [断言], 条件: "${错误命令结果.exit_code} != 0", 消息: "错误命令应该返回非零退出码"
end

# 清理测试文件
[打印], 内容: "🧹 清理测试文件..."
清理结果 = [SSH执行命令], 服务器: "test_server", 命令: "rm -rf ${test_directory}"

if ${清理结果.success} do
    [打印], 内容: "✅ 清理完成"
else
    [打印], 内容: "⚠️ 清理失败: ${清理结果.error}"
end

[打印], 内容: "🎉 SSH基本功能测试完成！" 