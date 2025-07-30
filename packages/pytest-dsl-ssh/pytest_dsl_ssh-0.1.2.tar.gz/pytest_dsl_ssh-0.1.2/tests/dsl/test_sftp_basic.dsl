@name: "SFTP基本功能测试"
@description: "测试SFTP文件上传、下载、目录操作等功能"
@tags: ["sftp", "file_transfer", "basic"]

# 测试变量
local_test_file = "test_data/upload/test_file.txt"
remote_test_file = "upload/test_file.txt"
local_chinese_file = "test_data/upload/chinese_test.txt"
remote_chinese_file = "upload/chinese_test.txt"
local_download_file = "test_data/download/downloaded_file.txt"
remote_directory = "upload/test_directory"
local_directory = "test_data/upload/subfolder"
download_directory = "test_data/download/subfolder"

# 测试SFTP连接
[打印], 内容: "🔗 开始测试SFTP连接..."
连接结果 = [SSH测试连接], 服务器: "test_server"

# SFTP服务器只支持SFTP协议，SSH命令会失败，但连接测试应该成功
if ${连接结果.test_results.connect_test} do
    [打印], 内容: "✅ SFTP连接测试成功"
else
    [打印], 内容: "❌ SFTP连接测试失败: ${连接结果.message}"
end

# 测试文件上传
[打印], 内容: "📤 测试文件上传..."
上传结果 = [SFTP上传文件],
    服务器: "test_server",
    本地文件: ${local_test_file},
    远程文件: ${remote_test_file}

if ${上传结果.success} do
    [打印], 内容: "✅ 文件上传成功"
    [打印], 内容: "上传信息: ${上传结果.message}"
else
    [打印], 内容: "❌ 文件上传失败: ${上传结果.error}"
end

# 测试中文文件上传
[打印], 内容: "🇨🇳 测试中文文件上传..."
中文上传结果 = [SFTP上传文件],
    服务器: "test_server",
    本地文件: ${local_chinese_file},
    远程文件: ${remote_chinese_file}

if ${中文上传结果.success} do
    [打印], 内容: "✅ 中文文件上传成功"
else
    [打印], 内容: "❌ 中文文件上传失败: ${中文上传结果.error}"
end

# 测试文件下载
[打印], 内容: "📥 测试文件下载..."
下载结果 = [SFTP下载文件],
    服务器: "test_server",
    远程文件: ${remote_test_file},
    本地文件: ${local_download_file}

if ${下载结果.success} do
    [打印], 内容: "✅ 文件下载成功"
    [打印], 内容: "下载信息: ${下载结果.message}"
else
    [打印], 内容: "❌ 文件下载失败: ${下载结果.error}"
end

# 测试目录创建
[打印], 内容: "📁 测试目录创建..."
创建目录结果 = [SFTP创建目录], 
    服务器: "test_server",
    远程目录: ${remote_directory}

if ${创建目录结果.success} do
    [打印], 内容: "✅ 目录创建成功"
else
    [打印], 内容: "❌ 目录创建失败: ${创建目录结果.error}"
end

# 测试目录上传
[打印], 内容: "📂 测试目录上传..."
目录上传结果 = [SFTP上传目录], 
    服务器: "test_server",
    本地目录: ${local_directory},
    远程目录: ${remote_directory}

if ${目录上传结果.success} do
    [打印], 内容: "✅ 目录上传成功"
    [打印], 内容: "上传了 ${目录上传结果.uploaded_files} 个文件"
else
    [打印], 内容: "❌ 目录上传失败: ${目录上传结果.message}"
end

# 测试目录列表
[打印], 内容: "📋 测试目录列表..."
列表结果 = [SFTP列出目录],
    服务器: "test_server",
    远程目录: "upload"

if ${列表结果.success} do
    [打印], 内容: "✅ 目录列表获取成功"
    [打印], 内容: "目录内容: ${列表结果.total_items} 项 (${列表结果.file_count} 文件, ${列表结果.directory_count} 目录)"
else
    [打印], 内容: "❌ 目录列表获取失败: ${列表结果.error}"
end

# 测试文件信息获取
[打印], 内容: "ℹ️ 测试文件信息获取..."
文件信息结果 = [SFTP文件信息], 
    服务器: "test_server",
    远程文件: ${remote_test_file}

if ${文件信息结果.success} do
    [打印], 内容: "✅ 文件信息获取成功"
    [打印], 内容: "文件大小: ${文件信息结果.file_info.size} bytes"
    [打印], 内容: "修改时间: ${文件信息结果.file_info.mtime}"
    [打印], 内容: "文件权限: ${文件信息结果.file_info.mode}"
else
    [打印], 内容: "❌ 文件信息获取失败: ${文件信息结果.error}"
end

# 测试目录下载
[打印], 内容: "📥 测试目录下载..."
目录下载结果 = [SFTP下载目录], 
    服务器: "test_server",
    远程目录: ${remote_directory},
    本地目录: ${download_directory}

if ${目录下载结果.success} do
    [打印], 内容: "✅ 目录下载成功"
    [打印], 内容: "下载了 ${目录下载结果.downloaded_files} 个文件"
else
    [打印], 内容: "❌ 目录下载失败: ${目录下载结果.error}"
end

# 测试文件删除
[打印], 内容: "🗑️ 测试文件删除..."
删除结果 = [SFTP删除文件], 
    服务器: "test_server",
    远程文件: ${remote_chinese_file}

if ${删除结果.success} do
    [打印], 内容: "✅ 文件删除成功"
else
    [打印], 内容: "❌ 文件删除失败: ${删除结果.message}"
end

# 测试错误处理 - 下载不存在的文件
[打印], 内容: "⚠️ 测试错误处理..."
错误下载结果 = [SFTP下载文件], 
    服务器: "test_server",
    远程文件: "/nonexistent/file.txt",
    本地文件: "test_data/download/nonexistent.txt"

if ${错误下载结果.success} do
    [打印], 内容: "⚠️ 下载不存在文件意外成功"
else
    [打印], 内容: "✅ 下载不存在文件正确失败"
    [打印], 内容: "错误信息: ${错误下载结果.error}"
end

# 最终目录列表检查
[打印], 内容: "🔍 最终目录检查..."
最终列表结果 = [SFTP列出目录],
    服务器: "test_server",
    远程目录: "upload"

if ${最终列表结果.success} do
    [打印], 内容: "✅ 最终目录列表: ${最终列表结果.total_items} 项 (${最终列表结果.file_count} 文件, ${最终列表结果.directory_count} 目录)"
else
    [打印], 内容: "❌ 最终目录列表获取失败: ${最终列表结果.error}"
end

[打印], 内容: "🎉 SFTP基本功能测试完成！" 