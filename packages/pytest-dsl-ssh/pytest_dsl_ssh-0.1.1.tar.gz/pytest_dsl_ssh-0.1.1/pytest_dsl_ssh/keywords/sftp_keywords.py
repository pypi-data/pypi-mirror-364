"""
SFTP文件传输关键字

提供SFTP文件上传、下载、目录操作等功能
"""

import logging

from pytest_dsl_ssh.core.connection_pool import get_global_connection_pool
from pytest_dsl_ssh.core.config_manager import get_global_config_manager
from pytest_dsl import keyword_manager


logger = logging.getLogger(__name__)


@keyword_manager.register('SFTP上传文件', [
    {'name': '服务器', 'mapping': 'server', 'description': '服务器配置名称或主机地址'},
    {'name': '本地文件', 'mapping': 'local_path', 'description': '本地文件路径'},
    {'name': '远程文件', 'mapping': 'remote_path', 'description': '远程文件路径'},
    {'name': '端口', 'mapping': 'port', 'description': 'SSH端口', 'default': 22},
    {'name': '用户名', 'mapping': 'username', 'description': '登录用户名', 'default': None},
    {'name': '密码', 'mapping': 'password', 'description': '登录密码', 'default': None},
    {'name': '私钥路径', 'mapping': 'private_key_path',
        'description': '私钥文件路径', 'default': None},
    {'name': '保持时间戳', 'mapping': 'preserve_times',
        'description': '是否保持文件时间戳', 'default': True}
], category='SFTP/文件', tags=['SFTP', '上传', '文件'])
def sftp_upload_file(**kwargs):
    """
    上传文件到远程服务器

    通过SFTP协议将本地文件上传到远程服务器
    """
    server = kwargs.get('server')
    local_path = kwargs.get('local_path')
    remote_path = kwargs.get('remote_path')
    port = kwargs.get('port', 22)
    username = kwargs.get('username')
    password = kwargs.get('password')
    private_key_path = kwargs.get('private_key_path')
    preserve_times = kwargs.get('preserve_times', True)

    if not local_path or not remote_path:
        return {'success': False, 'error': '本地路径和远程路径不能为空'}

    try:
        config_manager = get_global_config_manager()
        connection_pool = get_global_connection_pool()

        # 获取连接参数
        server_config = config_manager.get_server(server)
        if server_config:
            hostname = server_config.hostname
            port = server_config.port
            username = username or server_config.username
            password = password or server_config.password
            private_key_path = private_key_path or server_config.private_key_path
        else:
            hostname = server

        # 获取SFTP客户端
        sftp_client = connection_pool.get_sftp_client(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            private_key_path=private_key_path
        )

        # 上传文件
        result = sftp_client.upload_file(
            local_path=local_path,
            remote_path=remote_path,
            preserve_times=preserve_times
        )

        return {
            'success': result['success'],
            'local_path': result['local_path'],
            'remote_path': result['remote_path'],
            'file_size': result['file_size'],
            'transfer_time': result['transfer_time'],
            'transfer_speed': result['transfer_speed'],
            'message': f"文件上传成功: {local_path} -> {remote_path} ({result['file_size']} 字节)"
        }

    except Exception as e:
        logger.error(f"SFTP文件上传失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'local_path': local_path,
            'remote_path': remote_path,
            'message': f"SFTP文件上传失败: {str(e)}"
        }


@keyword_manager.register('SFTP下载文件', [
    {'name': '服务器', 'mapping': 'server', 'description': '服务器配置名称或主机地址'},
    {'name': '远程文件', 'mapping': 'remote_path', 'description': '远程文件路径'},
    {'name': '本地文件', 'mapping': 'local_path', 'description': '本地文件路径'},
    {'name': '端口', 'mapping': 'port', 'description': 'SSH端口', 'default': 22},
    {'name': '用户名', 'mapping': 'username', 'description': '登录用户名', 'default': None},
    {'name': '密码', 'mapping': 'password', 'description': '登录密码', 'default': None},
    {'name': '私钥路径', 'mapping': 'private_key_path',
        'description': '私钥文件路径', 'default': None},
    {'name': '保持时间戳', 'mapping': 'preserve_times',
        'description': '是否保持文件时间戳', 'default': True}
], category='SFTP/文件', tags=['SFTP', '下载', '文件'])
def sftp_download_file(**kwargs):
    """
    从远程服务器下载文件

    通过SFTP协议从远程服务器下载文件到本地
    """
    server = kwargs.get('server')
    remote_path = kwargs.get('remote_path')
    local_path = kwargs.get('local_path')
    port = kwargs.get('port', 22)
    username = kwargs.get('username')
    password = kwargs.get('password')
    private_key_path = kwargs.get('private_key_path')
    preserve_times = kwargs.get('preserve_times', True)

    if not remote_path or not local_path:
        return {'success': False, 'error': '远程路径和本地路径不能为空'}

    try:
        config_manager = get_global_config_manager()
        connection_pool = get_global_connection_pool()

        # 获取连接参数
        server_config = config_manager.get_server(server)
        if server_config:
            hostname = server_config.hostname
            port = server_config.port
            username = username or server_config.username
            password = password or server_config.password
            private_key_path = private_key_path or server_config.private_key_path
        else:
            hostname = server

        # 获取SFTP客户端
        sftp_client = connection_pool.get_sftp_client(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            private_key_path=private_key_path
        )

        # 下载文件
        result = sftp_client.download_file(
            remote_path=remote_path,
            local_path=local_path,
            preserve_times=preserve_times
        )

        return {
            'success': result['success'],
            'remote_path': result['remote_path'],
            'local_path': result['local_path'],
            'file_size': result['file_size'],
            'transfer_time': result['transfer_time'],
            'transfer_speed': result['transfer_speed'],
            'message': f"文件下载成功: {remote_path} -> {local_path} ({result['file_size']} 字节)"
        }

    except Exception as e:
        logger.error(f"SFTP文件下载失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'remote_path': remote_path,
            'local_path': local_path,
            'message': f"SFTP文件下载失败: {str(e)}"
        }


@keyword_manager.register('SFTP上传目录', [
    {'name': '服务器', 'mapping': 'server', 'description': '服务器配置名称或主机地址'},
    {'name': '本地目录', 'mapping': 'local_dir', 'description': '本地目录路径'},
    {'name': '远程目录', 'mapping': 'remote_dir', 'description': '远程目录路径'},
    {'name': '端口', 'mapping': 'port', 'description': 'SSH端口', 'default': 22},
    {'name': '用户名', 'mapping': 'username', 'description': '登录用户名', 'default': None},
    {'name': '密码', 'mapping': 'password', 'description': '登录密码', 'default': None},
    {'name': '私钥路径', 'mapping': 'private_key_path',
        'description': '私钥文件路径', 'default': None},
    {'name': '排除模式', 'mapping': 'exclude_patterns',
        'description': '排除的文件模式列表', 'default': []},
    {'name': '保持时间戳', 'mapping': 'preserve_times',
        'description': '是否保持文件时间戳', 'default': True}
], category='SFTP/目录', tags=['SFTP', '上传', '目录'])
def sftp_upload_directory(**kwargs):
    """
    上传目录到远程服务器

    递归上传本地目录及其所有内容到远程服务器
    """
    server = kwargs.get('server')
    local_dir = kwargs.get('local_dir')
    remote_dir = kwargs.get('remote_dir')
    port = kwargs.get('port', 22)
    username = kwargs.get('username')
    password = kwargs.get('password')
    private_key_path = kwargs.get('private_key_path')
    exclude_patterns = kwargs.get('exclude_patterns', [])
    preserve_times = kwargs.get('preserve_times', True)

    if not local_dir or not remote_dir:
        return {'success': False, 'error': '本地目录和远程目录不能为空'}

    try:
        config_manager = get_global_config_manager()
        connection_pool = get_global_connection_pool()

        # 获取连接参数
        server_config = config_manager.get_server(server)
        if server_config:
            hostname = server_config.hostname
            port = server_config.port
            username = username or server_config.username
            password = password or server_config.password
            private_key_path = private_key_path or server_config.private_key_path
        else:
            hostname = server

        # 获取SFTP客户端
        sftp_client = connection_pool.get_sftp_client(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            private_key_path=private_key_path
        )

        # 上传目录
        result = sftp_client.upload_directory(
            local_dir=local_dir,
            remote_dir=remote_dir,
            exclude_patterns=exclude_patterns,
            preserve_times=preserve_times
        )

        return {
            'success': result['success'],
            'local_dir': result['local_dir'],
            'remote_dir': result['remote_dir'],
            'total_files': result['total_files'],
            'uploaded_files': result['uploaded_files'],
            'failed_files': result['failed_files'],
            'total_size': result['total_size'],
            'transfer_time': result['transfer_time'],
            'failed_file_list': result['failed_file_list'],
            'message': f"目录上传完成: 成功 {result['uploaded_files']}/{result['total_files']} 个文件"
        }

    except Exception as e:
        logger.error(f"SFTP目录上传失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'local_dir': local_dir,
            'remote_dir': remote_dir,
            'message': f"SFTP目录上传失败: {str(e)}"
        }


@keyword_manager.register('SFTP下载目录', [
    {'name': '服务器', 'mapping': 'server', 'description': '服务器配置名称或主机地址'},
    {'name': '远程目录', 'mapping': 'remote_dir', 'description': '远程目录路径'},
    {'name': '本地目录', 'mapping': 'local_dir', 'description': '本地目录路径'},
    {'name': '端口', 'mapping': 'port', 'description': 'SSH端口', 'default': 22},
    {'name': '用户名', 'mapping': 'username', 'description': '登录用户名', 'default': None},
    {'name': '密码', 'mapping': 'password', 'description': '登录密码', 'default': None},
    {'name': '私钥路径', 'mapping': 'private_key_path',
        'description': '私钥文件路径', 'default': None},
    {'name': '保持时间戳', 'mapping': 'preserve_times',
        'description': '是否保持文件时间戳', 'default': True}
], category='SFTP/目录', tags=['SFTP', '下载', '目录'])
def sftp_download_directory(**kwargs):
    """
    从远程服务器下载目录

    递归下载远程目录及其所有内容到本地
    """
    server = kwargs.get('server')
    remote_dir = kwargs.get('remote_dir')
    local_dir = kwargs.get('local_dir')
    port = kwargs.get('port', 22)
    username = kwargs.get('username')
    password = kwargs.get('password')
    private_key_path = kwargs.get('private_key_path')
    preserve_times = kwargs.get('preserve_times', True)

    if not remote_dir or not local_dir:
        return {'success': False, 'error': '远程目录和本地目录不能为空'}

    try:
        config_manager = get_global_config_manager()
        connection_pool = get_global_connection_pool()

        # 获取连接参数
        server_config = config_manager.get_server(server)
        if server_config:
            hostname = server_config.hostname
            port = server_config.port
            username = username or server_config.username
            password = password or server_config.password
            private_key_path = private_key_path or server_config.private_key_path
        else:
            hostname = server

        # 获取SFTP客户端
        sftp_client = connection_pool.get_sftp_client(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            private_key_path=private_key_path
        )

        # 下载目录
        result = sftp_client.download_directory(
            remote_dir=remote_dir,
            local_dir=local_dir,
            preserve_times=preserve_times
        )

        return {
            'success': result['success'],
            'remote_dir': result['remote_dir'],
            'local_dir': result['local_dir'],
            'total_files': result['total_files'],
            'downloaded_files': result['downloaded_files'],
            'failed_files': result['failed_files'],
            'total_size': result['total_size'],
            'transfer_time': result['transfer_time'],
            'failed_file_list': result['failed_file_list'],
            'message': f"目录下载完成: 成功 {result['downloaded_files']}/{result['total_files']} 个文件"
        }

    except Exception as e:
        logger.error(f"SFTP目录下载失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'remote_dir': remote_dir,
            'local_dir': local_dir,
            'message': f"SFTP目录下载失败: {str(e)}"
        }


@keyword_manager.register('SFTP列出目录', [
    {'name': '服务器', 'mapping': 'server', 'description': '服务器配置名称或主机地址'},
    {'name': '远程目录', 'mapping': 'remote_path', 'description': '远程目录路径'},
    {'name': '端口', 'mapping': 'port', 'description': 'SSH端口', 'default': 22},
    {'name': '用户名', 'mapping': 'username', 'description': '登录用户名', 'default': None},
    {'name': '密码', 'mapping': 'password', 'description': '登录密码', 'default': None},
    {'name': '私钥路径', 'mapping': 'private_key_path',
        'description': '私钥文件路径', 'default': None},
    {'name': '详细信息', 'mapping': 'detailed',
        'description': '是否显示详细信息', 'default': False}
], category='SFTP/目录', tags=['SFTP', '列表', '目录'])
def sftp_list_directory(**kwargs):
    """
    列出远程目录内容

    获取远程目录中的文件和子目录列表
    """
    server = kwargs.get('server')
    remote_path = kwargs.get('remote_path')
    port = kwargs.get('port', 22)
    username = kwargs.get('username')
    password = kwargs.get('password')
    private_key_path = kwargs.get('private_key_path')
    detailed = kwargs.get('detailed', False)

    if not remote_path:
        return {'success': False, 'error': '远程路径不能为空'}

    try:
        config_manager = get_global_config_manager()
        connection_pool = get_global_connection_pool()

        # 获取连接参数
        server_config = config_manager.get_server(server)
        if server_config:
            hostname = server_config.hostname
            port = server_config.port
            username = username or server_config.username
            password = password or server_config.password
            private_key_path = private_key_path or server_config.private_key_path
        else:
            hostname = server

        # 获取SFTP客户端
        sftp_client = connection_pool.get_sftp_client(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            private_key_path=private_key_path
        )

        # 列出目录内容
        items = sftp_client.list_directory(remote_path, detailed=detailed)

        # 统计信息
        file_count = sum(1 for item in items if item['type'] == 'file')
        dir_count = sum(1 for item in items if item['type'] == 'directory')

        return {
            'success': True,
            'remote_path': remote_path,
            'items': items,
            'total_items': len(items),
            'file_count': file_count,
            'directory_count': dir_count,
            'message': f"目录列表: {len(items)} 项 ({file_count} 文件, {dir_count} 目录)"
        }

    except Exception as e:
        logger.error(f"SFTP列出目录失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'remote_path': remote_path,
            'message': f"SFTP列出目录失败: {str(e)}"
        }


@keyword_manager.register('SFTP创建目录', [
    {'name': '服务器', 'mapping': 'server', 'description': '服务器配置名称或主机地址'},
    {'name': '远程目录', 'mapping': 'remote_path', 'description': '要创建的远程目录路径'},
    {'name': '端口', 'mapping': 'port', 'description': 'SSH端口', 'default': 22},
    {'name': '用户名', 'mapping': 'username', 'description': '登录用户名', 'default': None},
    {'name': '密码', 'mapping': 'password', 'description': '登录密码', 'default': None},
    {'name': '私钥路径', 'mapping': 'private_key_path',
        'description': '私钥文件路径', 'default': None},
    {'name': '递归创建', 'mapping': 'recursive',
        'description': '是否递归创建父目录', 'default': True}
], category='SFTP/目录', tags=['SFTP', '创建', '目录'])
def sftp_create_directory(**kwargs):
    """
    创建远程目录

    在远程服务器上创建新目录，可选择递归创建
    """
    server = kwargs.get('server')
    remote_path = kwargs.get('remote_path')
    port = kwargs.get('port', 22)
    username = kwargs.get('username')
    password = kwargs.get('password')
    private_key_path = kwargs.get('private_key_path')
    recursive = kwargs.get('recursive', True)

    if not remote_path:
        return {'success': False, 'error': '远程路径不能为空'}

    try:
        config_manager = get_global_config_manager()
        connection_pool = get_global_connection_pool()

        # 获取连接参数
        server_config = config_manager.get_server(server)
        if server_config:
            hostname = server_config.hostname
            port = server_config.port
            username = username or server_config.username
            password = password or server_config.password
            private_key_path = private_key_path or server_config.private_key_path
        else:
            hostname = server

        # 获取SFTP客户端
        sftp_client = connection_pool.get_sftp_client(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            private_key_path=private_key_path
        )

        # 创建目录
        success = sftp_client.create_directory(
            remote_path, recursive=recursive)

        return {
            'success': success,
            'remote_path': remote_path,
            'recursive': recursive,
            'message': f"目录{'创建成功' if success else '创建失败'}: {remote_path}"
        }

    except Exception as e:
        logger.error(f"SFTP创建目录失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'remote_path': remote_path,
            'message': f"SFTP创建目录失败: {str(e)}"
        }


@keyword_manager.register('SFTP删除文件', [
    {'name': '服务器', 'mapping': 'server', 'description': '服务器配置名称或主机地址'},
    {'name': '远程文件', 'mapping': 'remote_path', 'description': '要删除的远程文件路径'},
    {'name': '端口', 'mapping': 'port', 'description': 'SSH端口', 'default': 22},
    {'name': '用户名', 'mapping': 'username', 'description': '登录用户名', 'default': None},
    {'name': '密码', 'mapping': 'password', 'description': '登录密码', 'default': None},
    {'name': '私钥路径', 'mapping': 'private_key_path',
        'description': '私钥文件路径', 'default': None}
], category='SFTP/文件', tags=['SFTP', '删除', '文件'])
def sftp_remove_file(**kwargs):
    """
    删除远程文件

    删除远程服务器上的指定文件
    """
    server = kwargs.get('server')
    remote_path = kwargs.get('remote_path')
    port = kwargs.get('port', 22)
    username = kwargs.get('username')
    password = kwargs.get('password')
    private_key_path = kwargs.get('private_key_path')

    if not remote_path:
        return {'success': False, 'error': '远程路径不能为空'}

    try:
        config_manager = get_global_config_manager()
        connection_pool = get_global_connection_pool()

        # 获取连接参数
        server_config = config_manager.get_server(server)
        if server_config:
            hostname = server_config.hostname
            port = server_config.port
            username = username or server_config.username
            password = password or server_config.password
            private_key_path = private_key_path or server_config.private_key_path
        else:
            hostname = server

        # 获取SFTP客户端
        sftp_client = connection_pool.get_sftp_client(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            private_key_path=private_key_path
        )

        # 删除文件
        success = sftp_client.remove_file(remote_path)

        return {
            'success': success,
            'remote_path': remote_path,
            'message': f"文件{'删除成功' if success else '删除失败'}: {remote_path}"
        }

    except Exception as e:
        logger.error(f"SFTP删除文件失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'remote_path': remote_path,
            'message': f"SFTP删除文件失败: {str(e)}"
        }


@keyword_manager.register('SFTP删除目录', [
    {'name': '服务器', 'mapping': 'server', 'description': '服务器配置名称或主机地址'},
    {'name': '远程目录', 'mapping': 'remote_path', 'description': '要删除的远程目录路径'},
    {'name': '端口', 'mapping': 'port', 'description': 'SSH端口', 'default': 22},
    {'name': '用户名', 'mapping': 'username', 'description': '登录用户名', 'default': None},
    {'name': '密码', 'mapping': 'password', 'description': '登录密码', 'default': None},
    {'name': '私钥路径', 'mapping': 'private_key_path',
        'description': '私钥文件路径', 'default': None},
    {'name': '递归删除', 'mapping': 'recursive',
        'description': '是否递归删除目录内容', 'default': False}
], category='SFTP/目录', tags=['SFTP', '删除', '目录'])
def sftp_remove_directory(**kwargs):
    """
    删除远程目录

    删除远程服务器上的指定目录，可选择递归删除
    """
    server = kwargs.get('server')
    remote_path = kwargs.get('remote_path')
    port = kwargs.get('port', 22)
    username = kwargs.get('username')
    password = kwargs.get('password')
    private_key_path = kwargs.get('private_key_path')
    recursive = kwargs.get('recursive', False)

    if not remote_path:
        return {'success': False, 'error': '远程路径不能为空'}

    try:
        config_manager = get_global_config_manager()
        connection_pool = get_global_connection_pool()

        # 获取连接参数
        server_config = config_manager.get_server(server)
        if server_config:
            hostname = server_config.hostname
            port = server_config.port
            username = username or server_config.username
            password = password or server_config.password
            private_key_path = private_key_path or server_config.private_key_path
        else:
            hostname = server

        # 获取SFTP客户端
        sftp_client = connection_pool.get_sftp_client(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            private_key_path=private_key_path
        )

        # 删除目录
        success = sftp_client.remove_directory(
            remote_path, recursive=recursive)

        return {
            'success': success,
            'remote_path': remote_path,
            'recursive': recursive,
            'message': f"目录{'删除成功' if success else '删除失败'}: {remote_path}"
        }

    except Exception as e:
        logger.error(f"SFTP删除目录失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'remote_path': remote_path,
            'message': f"SFTP删除目录失败: {str(e)}"
        }


@keyword_manager.register('SFTP文件信息', [
    {'name': '服务器', 'mapping': 'server', 'description': '服务器配置名称或主机地址'},
    {'name': '远程文件', 'mapping': 'remote_path', 'description': '远程文件或目录路径'},
    {'name': '端口', 'mapping': 'port', 'description': 'SSH端口', 'default': 22},
    {'name': '用户名', 'mapping': 'username', 'description': '登录用户名', 'default': None},
    {'name': '密码', 'mapping': 'password', 'description': '登录密码', 'default': None},
    {'name': '私钥路径', 'mapping': 'private_key_path',
        'description': '私钥文件路径', 'default': None}
], category='SFTP/信息', tags=['SFTP', '信息', '文件'])
def sftp_file_info(**kwargs):
    """
    获取远程文件信息

    获取远程文件或目录的详细信息
    """
    server = kwargs.get('server')
    remote_path = kwargs.get('remote_path')
    port = kwargs.get('port', 22)
    username = kwargs.get('username')
    password = kwargs.get('password')
    private_key_path = kwargs.get('private_key_path')

    if not remote_path:
        return {'success': False, 'error': '远程路径不能为空'}

    try:
        config_manager = get_global_config_manager()
        connection_pool = get_global_connection_pool()

        # 获取连接参数
        server_config = config_manager.get_server(server)
        if server_config:
            hostname = server_config.hostname
            port = server_config.port
            username = username or server_config.username
            password = password or server_config.password
            private_key_path = private_key_path or server_config.private_key_path
        else:
            hostname = server

        # 获取SFTP客户端
        sftp_client = connection_pool.get_sftp_client(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            private_key_path=private_key_path
        )

        # 检查文件是否存在
        if not sftp_client.file_exists(remote_path):
            return {
                'success': False,
                'remote_path': remote_path,
                'exists': False,
                'message': f"文件不存在: {remote_path}"
            }

        # 获取文件信息
        file_info = sftp_client.get_file_info(remote_path)

        return {
            'success': True,
            'remote_path': remote_path,
            'exists': True,
            'file_info': file_info,
            'message': f"文件信息获取成功: {remote_path}"
        }

    except Exception as e:
        logger.error(f"SFTP获取文件信息失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'remote_path': remote_path,
            'message': f"SFTP获取文件信息失败: {str(e)}"
        }
