"""
SSH连接和命令执行关键字

提供SSH连接管理和远程命令执行功能
"""

import logging

from pytest_dsl_ssh.core.connection_pool import get_global_connection_pool
from pytest_dsl_ssh.core.unified_config import get_ssh_connection_config
from pytest_dsl_ssh.exceptions import SSHConnectionError
from pytest_dsl import keyword_manager

logger = logging.getLogger(__name__)


# 使用统一配置管理器，简化配置获取逻辑


@keyword_manager.register('SSH连接', [
    {'name': '服务器', 'mapping': 'server', 'description': '服务器配置名称（从YAML配置加载）或直接主机地址'},
    {'name': '端口', 'mapping': 'port',
        'description': 'SSH端口（可选，优先使用配置中的值）', 'default': None},
    {'name': '用户名', 'mapping': 'username',
        'description': '登录用户名（可选，优先使用配置中的值）', 'default': None},
    {'name': '密码', 'mapping': 'password',
        'description': '登录密码（可选，优先使用配置中的值）', 'default': None},
    {'name': '私钥路径', 'mapping': 'private_key_path',
        'description': '私钥文件路径（可选，优先使用配置中的值）', 'default': None},
    {'name': '私钥密码', 'mapping': 'private_key_password',
        'description': '私钥密码（可选，优先使用配置中的值）', 'default': None},
    {'name': '连接超时', 'mapping': 'connect_timeout',
        'description': '连接超时时间（秒）（可选，优先使用配置中的值）', 'default': None},
    {'name': '使用连接池', 'mapping': 'use_pool',
        'description': '是否使用连接池', 'default': True}
], category='SSH/连接', tags=['SSH', '连接', '登录'])
def ssh_connect(context, **kwargs):
    """
    建立SSH连接

    支持通过服务器配置名称或直接指定连接参数来建立SSH连接
    """
    server = kwargs.get('server')
    port = kwargs.get('port')
    username = kwargs.get('username')
    password = kwargs.get('password')
    private_key_path = kwargs.get('private_key_path')
    private_key_password = kwargs.get('private_key_password')
    connect_timeout = kwargs.get('connect_timeout')
    use_pool = kwargs.get('use_pool', True)

    # 添加调试信息，检查SSH服务器配置是否可用
    print(f"🔗 SSH连接 - 服务器: {server}")

    try:
        connection_pool = get_global_connection_pool()

        # 使用统一配置管理器获取服务器配置
        config = get_ssh_connection_config(
            context, server, port=port, username=username, password=password,
            private_key_path=private_key_path, connect_timeout=connect_timeout
        )
        hostname = config.hostname
        port = config.port
        username = config.username
        password = config.password
        private_key_path = config.private_key_path
        connect_timeout = config.connect_timeout

        # 处理私钥密码（这个参数在辅助函数中没有处理）
        if private_key_password is None and hasattr(context, 'get'):
            ssh_servers_config = context.get("ssh_servers")
            if ssh_servers_config and server in ssh_servers_config:
                private_key_password = ssh_servers_config[server].get('private_key_password')

        if not hostname:
            raise SSHConnectionError("服务器地址不能为空")

        if not username:
            raise SSHConnectionError("用户名不能为空")

        # 建立连接
        if use_pool:
            ssh_client = connection_pool.get_ssh_client(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                private_key_path=private_key_path,
                private_key_password=private_key_password,
                connect_timeout=connect_timeout
            )
        else:
            from ..core.ssh_client import SSHClient
            ssh_client = SSHClient(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                private_key_path=private_key_path,
                private_key_password=private_key_password,
                connect_timeout=connect_timeout
            )
            ssh_client.connect()

        connection_info = ssh_client.get_connection_info()

        return {
            'success': True,
            'connection_info': connection_info,
            'message': f"SSH连接成功: {username}@{hostname}:{port}",
            'hostname': hostname,
            'port': port,
            'username': username
        }

    except Exception as e:
        logger.error(f"SSH连接失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"SSH连接失败: {str(e)}"
        }


@keyword_manager.register('SSH执行命令', [
    {'name': '服务器', 'mapping': 'server', 'description': '服务器配置名称（从YAML配置加载）或主机地址'},
    {'name': '命令', 'mapping': 'command', 'description': '要执行的命令'},
    {'name': '端口', 'mapping': 'port',
        'description': 'SSH端口（可选，优先使用配置中的值）', 'default': None},
    {'name': '用户名', 'mapping': 'username',
        'description': '登录用户名（可选，优先使用配置中的值）', 'default': None},
    {'name': '密码', 'mapping': 'password',
        'description': '登录密码（可选，优先使用配置中的值）', 'default': None},
    {'name': '私钥路径', 'mapping': 'private_key_path',
        'description': '私钥文件路径（可选，优先使用配置中的值）', 'default': None},
    {'name': '超时时间', 'mapping': 'timeout',
        'description': '命令超时时间（秒）', 'default': 30},
    {'name': '获取伪终端', 'mapping': 'get_pty',
        'description': '是否请求伪终端', 'default': False},
    {'name': '合并错误输出', 'mapping': 'combine_stderr',
        'description': '是否合并stderr到stdout', 'default': True}
], category='SSH/命令', tags=['SSH', '命令', '执行'])
def ssh_execute_command(context, **kwargs):
    """
    执行SSH命令

    在远程服务器上执行指定命令并返回结果
    """
    server = kwargs.get('server')
    command = kwargs.get('command')
    port = kwargs.get('port')
    username = kwargs.get('username')
    password = kwargs.get('password')
    private_key_path = kwargs.get('private_key_path')
    timeout = kwargs.get('timeout', 30)
    get_pty = kwargs.get('get_pty', False)
    combine_stderr = kwargs.get('combine_stderr', True)

    if not command:
        return {'success': False, 'error': '命令不能为空'}

    # 添加调试信息，检查SSH服务器配置是否可用
    print(f"⚡ SSH执行命令 - 服务器: {server}, 命令: {command}")

    try:
        connection_pool = get_global_connection_pool()

        # 使用统一配置管理器获取服务器配置
        config = get_ssh_connection_config(
            context, server, port=port, username=username, password=password,
            private_key_path=private_key_path
        )
        hostname = config.hostname
        port = config.port
        username = config.username
        password = config.password
        private_key_path = config.private_key_path

        # 获取SSH客户端
        ssh_client = connection_pool.get_ssh_client(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            private_key_path=private_key_path
        )

        # 执行命令
        result = ssh_client.execute_command(
            command=command,
            timeout=timeout,
            get_pty=get_pty,
            combine_stderr=combine_stderr
        )

        # 释放连接
        connection_pool.release_connection(hostname, port, username)

        return {
            'success': True,
            'command': result['command'],
            'exit_code': result['exit_code'],
            'stdout': result['stdout'],
            'stderr': result['stderr'],
            'execution_time': result['execution_time'],
            'message': f"命令执行完成，退出码: {result['exit_code']}"
        }

    except Exception as e:
        logger.error(f"SSH命令执行失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'command': command,
            'message': f"SSH命令执行失败: {str(e)}"
        }


@keyword_manager.register('SSH批量执行命令', [
    {'name': '服务器', 'mapping': 'server', 'description': '服务器配置名称或主机地址'},
    {'name': '命令列表', 'mapping': 'commands', 'description': '要执行的命令列表'},
    {'name': '端口', 'mapping': 'port', 'description': 'SSH端口', 'default': None},
    {'name': '用户名', 'mapping': 'username', 'description': '登录用户名', 'default': None},
    {'name': '密码', 'mapping': 'password', 'description': '登录密码', 'default': None},
    {'name': '私钥路径', 'mapping': 'private_key_path',
        'description': '私钥文件路径', 'default': None},
    {'name': '超时时间', 'mapping': 'timeout',
        'description': '每个命令的超时时间（秒）', 'default': 30},
    {'name': '遇错停止', 'mapping': 'stop_on_error',
        'description': '遇到错误是否停止执行', 'default': True}
], category='SSH/命令', tags=['SSH', '批量', '命令'])
def ssh_execute_commands(context, **kwargs):
    """
    批量执行SSH命令

    依次执行多个命令，可选择遇到错误时是否停止
    """
    server = kwargs.get('server')
    commands = kwargs.get('commands')
    port = kwargs.get('port')  # 不设置默认值，让辅助函数处理
    username = kwargs.get('username')
    password = kwargs.get('password')
    private_key_path = kwargs.get('private_key_path')
    timeout = kwargs.get('timeout', 30)
    stop_on_error = kwargs.get('stop_on_error', True)

    if not commands:
        return {'success': False, 'error': '命令列表不能为空'}

    if isinstance(commands, str):
        commands = [commands]

    # 添加调试信息，检查SSH服务器配置是否可用
    print(f"📋 SSH批量执行命令 - 服务器: {server}, 命令数量: {len(commands)}")

    try:
        connection_pool = get_global_connection_pool()

        # 使用统一配置管理器获取服务器配置
        config = get_ssh_connection_config(
            context, server, port=port, username=username, password=password,
            private_key_path=private_key_path
        )
        hostname = config.hostname
        port = config.port
        username = config.username
        password = config.password
        private_key_path = config.private_key_path

        # 获取SSH客户端
        ssh_client = connection_pool.get_ssh_client(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            private_key_path=private_key_path
        )

        # 批量执行命令
        results = ssh_client.execute_commands(
            commands=commands,
            stop_on_error=stop_on_error,
            timeout=timeout
        )

        # 释放连接
        connection_pool.release_connection(hostname, port, username)

        # 统计结果
        success_count = sum(1 for r in results if r.get('exit_code') == 0)
        failed_count = len(results) - success_count

        return {
            'success': failed_count == 0,
            'total_commands': len(commands),
            'success_count': success_count,
            'failed_count': failed_count,
            'results': results,
            'message': f"批量命令执行完成: 成功 {success_count}, 失败 {failed_count}"
        }

    except Exception as e:
        logger.error(f"SSH批量命令执行失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"SSH批量命令执行失败: {str(e)}"
        }


@keyword_manager.register('SSH断开连接', [
    {'name': '服务器', 'mapping': 'server', 'description': '服务器配置名称或主机地址'},
    {'name': '端口', 'mapping': 'port', 'description': 'SSH端口', 'default': None},
    {'name': '用户名', 'mapping': 'username', 'description': '登录用户名', 'default': None},
    {'name': '强制关闭', 'mapping': 'force_close',
        'description': '是否强制关闭连接', 'default': False}
], category='SSH/连接', tags=['SSH', '断开', '关闭'])
def ssh_disconnect(context, **kwargs):
    """
    断开SSH连接

    关闭指定的SSH连接，可选择是否强制关闭
    """
    server = kwargs.get('server')
    port = kwargs.get('port')  # 不设置默认值，让辅助函数处理
    username = kwargs.get('username')
    force_close = kwargs.get('force_close', False)

    # 添加调试信息，检查SSH服务器配置是否可用
    print(f"🔌 SSH断开连接 - 服务器: {server}")

    try:
        connection_pool = get_global_connection_pool()

        # 使用统一配置管理器获取服务器配置
        config = get_ssh_connection_config(context, server, port=port, username=username)
        hostname = config.hostname
        port = config.port
        username = config.username

        if force_close:
            connection_pool.close_connection(hostname, port, username)
            message = f"强制关闭SSH连接: {username}@{hostname}:{port}"
        else:
            connection_pool.release_connection(hostname, port, username)
            message = f"释放SSH连接: {username}@{hostname}:{port}"

        return {
            'success': True,
            'message': message,
            'hostname': hostname,
            'port': port,
            'username': username
        }

    except Exception as e:
        logger.error(f"SSH断开连接失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"SSH断开连接失败: {str(e)}"
        }


@keyword_manager.register('SSH连接状态', [
    {'name': '服务器', 'mapping': 'server',
        'description': '服务器配置名称或主机地址', 'default': None},
    {'name': '端口', 'mapping': 'port', 'description': 'SSH端口', 'default': None},
    {'name': '用户名', 'mapping': 'username', 'description': '登录用户名', 'default': None}
], category='SSH/信息', tags=['SSH', '状态', '查询'])
def ssh_connection_status(context, **kwargs):
    """
    查询SSH连接状态

    查询指定连接的状态信息，或查询所有连接的状态
    """
    server = kwargs.get('server')
    port = kwargs.get('port')  # 不设置默认值，让辅助函数处理
    username = kwargs.get('username')

    # 添加调试信息，检查SSH服务器配置是否可用
    print(f"📊 SSH连接状态 - 服务器: {server}")

    try:
        connection_pool = get_global_connection_pool()

        if server:
            # 查询特定连接状态
            # 使用统一配置管理器获取服务器配置
            config = get_ssh_connection_config(context, server, port=port, username=username)
            hostname = config.hostname
            port = config.port
            username = config.username

            connections = connection_pool.list_connections()
            connection_key = f"{username}@{hostname}:{port}"

            if connection_key in connections:
                connection_info = connections[connection_key]
                return {
                    'success': True,
                    'connection_key': connection_key,
                    'connection_info': connection_info,
                    'message': f"连接状态: {'已连接' if connection_info['is_connected'] else '未连接'}"
                }
            else:
                return {
                    'success': True,
                    'connection_key': connection_key,
                    'connection_info': None,
                    'message': "连接不存在"
                }
        else:
            # 查询所有连接状态
            connections = connection_pool.list_connections()
            stats = connection_pool.get_connection_stats()

            return {
                'success': True,
                'all_connections': connections,
                'stats': stats,
                'message': f"当前连接池状态: 总连接 {stats['total_connections']}, 活跃 {stats['active_connections']}"
            }

    except Exception as e:
        logger.error(f"查询SSH连接状态失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"查询SSH连接状态失败: {str(e)}"
        }


@keyword_manager.register('SSH测试连接', [
    {'name': '服务器', 'mapping': 'server', 'description': '服务器配置名称或主机地址'},
    {'name': '端口', 'mapping': 'port', 'description': 'SSH端口', 'default': None},
    {'name': '用户名', 'mapping': 'username', 'description': '登录用户名', 'default': None},
    {'name': '密码', 'mapping': 'password', 'description': '登录密码', 'default': None},
    {'name': '私钥路径', 'mapping': 'private_key_path',
        'description': '私钥文件路径', 'default': None},
    {'name': '连接超时', 'mapping': 'connect_timeout',
        'description': '连接超时时间（秒）', 'default': 10},
    {'name': '测试命令', 'mapping': 'test_command',
        'description': '测试命令', 'default': 'echo "connection test"'}
], category='SSH/测试', tags=['SSH', '测试', '连接'])
def ssh_test_connection(context, **kwargs):
    """
    测试SSH连接

    测试SSH连接是否正常，包括连接和简单命令执行
    """
    server = kwargs.get('server')
    port = kwargs.get('port')  # 不设置默认值，让辅助函数处理
    username = kwargs.get('username')
    password = kwargs.get('password')
    private_key_path = kwargs.get('private_key_path')
    connect_timeout = kwargs.get('connect_timeout', 10)
    test_command = kwargs.get('test_command', 'echo "connection test"')

    # 添加调试信息，检查SSH服务器配置是否可用
    print(f"🧪 SSH测试连接 - 服务器: {server}")

    try:
        # 使用统一配置管理器获取服务器配置
        config = get_ssh_connection_config(
            context, server, port=port, username=username, password=password,
            private_key_path=private_key_path, connect_timeout=connect_timeout
        )
        hostname = config.hostname
        port = config.port
        username = config.username
        password = config.password
        private_key_path = config.private_key_path
        connect_timeout = config.connect_timeout

        # 创建临时连接进行测试
        from ..core.ssh_client import SSHClient
        ssh_client = SSHClient(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            private_key_path=private_key_path,
            connect_timeout=connect_timeout
        )

        test_results = {
            'hostname': hostname,
            'port': port,
            'username': username,
            'connect_test': False,
            'command_test': False,
            'connection_time': 0,
            'command_time': 0,
            'error': None
        }

        import time

        # 测试连接
        start_time = time.time()
        ssh_client.connect()
        test_results['connect_test'] = True
        test_results['connection_time'] = round(time.time() - start_time, 3)

        # 测试命令执行
        start_time = time.time()
        cmd_result = ssh_client.execute_command(test_command)
        test_results['command_test'] = cmd_result['exit_code'] == 0
        test_results['command_time'] = round(time.time() - start_time, 3)
        test_results['command_output'] = cmd_result['stdout']

        # 关闭连接
        ssh_client.disconnect()

        success = test_results['connect_test'] and test_results['command_test']

        return {
            'success': success,
            'test_results': test_results,
            'message': f"SSH连接测试{'成功' if success else '失败'}: {username}@{hostname}:{port}"
        }

    except Exception as e:
        logger.error(f"SSH连接测试失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'test_results': {
                'hostname': hostname if 'hostname' in locals() else server,
                'port': port,
                'username': username,
                'connect_test': False,
                'command_test': False,
                'error': str(e)
            },
            'message': f"SSH连接测试失败: {str(e)}"
        }
