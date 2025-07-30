"""
SSH/SFTP相关的自定义异常类
"""


class SSHException(Exception):
    """SSH操作异常基类"""

    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            return f"{self.message} | 详细信息: {self.details}"
        return self.message


class SSHConnectionError(SSHException):
    """SSH连接错误"""
    pass


class SSHAuthenticationError(SSHException):
    """SSH认证错误"""
    pass


class SSHCommandError(SSHException):
    """SSH命令执行错误"""

    def __init__(self, message: str, command: str = None, exit_code: int = None, stderr: str = None):
        self.command = command
        self.exit_code = exit_code
        self.stderr = stderr
        details = []
        if command:
            details.append(f"命令: {command}")
        if exit_code is not None:
            details.append(f"退出码: {exit_code}")
        if stderr:
            details.append(f"错误输出: {stderr}")
        super().__init__(message, " | ".join(details))


class SFTPException(Exception):
    """SFTP操作异常基类"""

    def __init__(self, message: str, local_path: str = None, remote_path: str = None):
        self.message = message
        self.local_path = local_path
        self.remote_path = remote_path
        super().__init__(self.message)

    def __str__(self):
        details = []
        if self.local_path:
            details.append(f"本地路径: {self.local_path}")
        if self.remote_path:
            details.append(f"远程路径: {self.remote_path}")

        if details:
            return f"{self.message} | {' | '.join(details)}"
        return self.message


class SFTPTransferError(SFTPException):
    """SFTP传输错误"""
    pass


class SFTPPermissionError(SFTPException):
    """SFTP权限错误"""
    pass


class SSHTunnelError(SSHException):
    """SSH隧道错误"""

    def __init__(self, message: str, local_port: int = None, remote_host: str = None, remote_port: int = None):
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        details = []
        if local_port:
            details.append(f"本地端口: {local_port}")
        if remote_host and remote_port:
            details.append(f"远程地址: {remote_host}:{remote_port}")
        super().__init__(message, " | ".join(details))


class SSHConfigError(SSHException):
    """SSH配置错误"""
    pass


__all__ = [
    "SSHException",
    "SSHConnectionError",
    "SSHAuthenticationError",
    "SSHCommandError",
    "SFTPException",
    "SFTPTransferError",
    "SFTPPermissionError",
    "SSHTunnelError",
    "SSHConfigError",
]
