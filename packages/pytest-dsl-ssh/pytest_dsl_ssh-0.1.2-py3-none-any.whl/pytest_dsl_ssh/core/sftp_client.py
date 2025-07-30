"""
SFTP客户端封装

基于paramiko实现的SFTP文件传输功能
"""

import logging
import os
import stat
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Callable


from paramiko.sftp_client import SFTPClient as ParamikoSFTPClient

from pytest_dsl_ssh.exceptions import (
    SFTPException,
    SFTPTransferError,
    SFTPPermissionError,
    SSHConnectionError,
)

logger = logging.getLogger(__name__)


class SFTPClient:
    """SFTP客户端类，封装SFTP文件传输操作"""

    def __init__(self, ssh_client):
        """
        初始化SFTP客户端

        Args:
            ssh_client: SSH客户端实例
        """
        self.ssh_client = ssh_client
        self._sftp_client: Optional[ParamikoSFTPClient] = None

    def connect(self) -> None:
        """建立SFTP连接"""
        if not self.ssh_client.is_connected():
            raise SSHConnectionError("SSH连接未建立，无法创建SFTP连接")

        try:
            self._sftp_client = self.ssh_client._client.open_sftp()
            logger.info("SFTP连接已建立")
        except Exception as e:
            raise SFTPException(f"建立SFTP连接失败: {str(e)}")

    def disconnect(self) -> None:
        """断开SFTP连接"""
        if self._sftp_client:
            try:
                self._sftp_client.close()
                logger.info("SFTP连接已断开")
            except Exception as e:
                logger.warning(f"断开SFTP连接时出现异常: {e}")
            finally:
                self._sftp_client = None

    def is_connected(self) -> bool:
        """检查SFTP连接状态"""
        return self._sftp_client is not None and self.ssh_client.is_connected()

    def upload_file(self,
                    local_path: str,
                    remote_path: str,
                    progress_callback: Optional[Callable[[int, int], None]] = None,
                    preserve_times: bool = True) -> Dict[str, Union[str, int, float]]:
        """
        上传文件

        Args:
            local_path: 本地文件路径
            remote_path: 远程文件路径
            progress_callback: 进度回调函数 (bytes_transferred, total_bytes)
            preserve_times: 是否保持文件时间戳

        Returns:
            上传结果信息
        """
        if not self.is_connected():
            self.connect()

        local_file = Path(local_path)
        if not local_file.exists():
            raise SFTPTransferError("本地文件不存在", local_path, remote_path)

        if not local_file.is_file():
            raise SFTPTransferError("本地路径不是文件", local_path, remote_path)

        try:
            logger.info(f"开始上传文件: {local_path} -> {remote_path}")
            start_time = time.time()

            # 确保远程目录存在
            remote_dir = os.path.dirname(remote_path)
            if remote_dir:
                self.create_directory(remote_dir, recursive=True)

            # 上传文件
            self._sftp_client.put(
                str(local_path),
                remote_path,
                callback=progress_callback
            )

            # 保持时间戳
            if preserve_times:
                local_stat = local_file.stat()
                self._sftp_client.utime(remote_path, (local_stat.st_atime, local_stat.st_mtime))

            transfer_time = time.time() - start_time
            file_size = local_file.stat().st_size

            logger.info(f"文件上传成功: {local_path} -> {remote_path}")

            return {
                'local_path': local_path,
                'remote_path': remote_path,
                'file_size': file_size,
                'transfer_time': round(transfer_time, 3),
                'transfer_speed': round(file_size / transfer_time, 2) if transfer_time > 0 else 0,
                'success': True
            }

        except PermissionError as e:
            raise SFTPPermissionError("上传文件权限不足", local_path, remote_path)
        except Exception as e:
            raise SFTPTransferError(f"上传文件失败: {str(e)}", local_path, remote_path)

    def download_file(self,
                      remote_path: str,
                      local_path: str,
                      progress_callback: Optional[Callable[[int, int], None]] = None,
                      preserve_times: bool = True) -> Dict[str, Union[str, int, float]]:
        """
        下载文件

        Args:
            remote_path: 远程文件路径
            local_path: 本地文件路径
            progress_callback: 进度回调函数
            preserve_times: 是否保持文件时间戳

        Returns:
            下载结果信息
        """
        if not self.is_connected():
            self.connect()

        try:
            # 检查远程文件是否存在
            remote_stat = self._sftp_client.stat(remote_path)
            if not stat.S_ISREG(remote_stat.st_mode):
                raise SFTPTransferError("远程路径不是文件", local_path, remote_path)

            logger.info(f"开始下载文件: {remote_path} -> {local_path}")
            start_time = time.time()

            # 确保本地目录存在
            local_file = Path(local_path)
            local_file.parent.mkdir(parents=True, exist_ok=True)

            # 下载文件
            self._sftp_client.get(
                remote_path,
                local_path,
                callback=progress_callback
            )

            # 保持时间戳
            if preserve_times:
                os.utime(local_path, (remote_stat.st_atime, remote_stat.st_mtime))

            transfer_time = time.time() - start_time
            file_size = remote_stat.st_size

            logger.info(f"文件下载成功: {remote_path} -> {local_path}")

            return {
                'remote_path': remote_path,
                'local_path': local_path,
                'file_size': file_size,
                'transfer_time': round(transfer_time, 3),
                'transfer_speed': round(file_size / transfer_time, 2) if transfer_time > 0 else 0,
                'success': True
            }

        except FileNotFoundError:
            raise SFTPTransferError("远程文件不存在", local_path, remote_path)
        except PermissionError:
            raise SFTPPermissionError("下载文件权限不足", local_path, remote_path)
        except Exception as e:
            raise SFTPTransferError("下载文件失败: {str(e)}", local_path, remote_path)

    def upload_directory(self,
                         local_dir: str,
                         remote_dir: str,
                         progress_callback: Optional[Callable[[str, int, int], None]] = None,
                         preserve_times: bool = True,
                         exclude_patterns: Optional[List[str]] = None) -> Dict[str, Union[int, List, float]]:
        """
        上传目录

        Args:
            local_dir: 本地目录路径
            remote_dir: 远程目录路径
            progress_callback: 进度回调函数 (current_file, current_index, total_files)
            preserve_times: 是否保持文件时间戳
            exclude_patterns: 排除的文件模式列表

        Returns:
            上传结果统计
        """
        if not self.is_connected():
            self.connect()

        local_path = Path(local_dir)
        if not local_path.exists():
            raise SFTPTransferError("本地目录不存在", local_dir, remote_dir)

        if not local_path.is_dir():
            raise SFTPTransferError("本地路径不是目录", local_dir, remote_dir)

        exclude_patterns = exclude_patterns or []

        try:
            logger.info(f"开始上传目录: {local_dir} -> {remote_dir}")
            start_time = time.time()

            # 获取所有需要上传的文件
            files_to_upload = []
            for file_path in local_path.rglob('*'):
                if file_path.is_file():
                    # 检查是否被排除
                    relative_path = file_path.relative_to(local_path)
                    if not any(relative_path.match(pattern) for pattern in exclude_patterns):
                        files_to_upload.append(file_path)

            uploaded_files = []
            failed_files = []
            total_size = 0

            for i, file_path in enumerate(files_to_upload):
                try:
                    if progress_callback:
                        progress_callback(str(file_path), i + 1, len(files_to_upload))

                    # 计算远程文件路径
                    relative_path = file_path.relative_to(local_path)
                    remote_file_path = os.path.join(remote_dir, str(relative_path)).replace('\\', '/')

                    # 上传文件
                    result = self.upload_file(str(file_path), remote_file_path, preserve_times=preserve_times)
                    uploaded_files.append(result)
                    total_size += result['file_size']

                except Exception as e:
                    failed_files.append({'file': str(file_path), 'error': str(e)})
                    logger.error(f"上传文件失败: {file_path} - {e}")

            transfer_time = time.time() - start_time

            logger.info(f"目录上传完成: 成功 {len(uploaded_files)}, 失败 {len(failed_files)}")

            return {
                'local_dir': local_dir,
                'remote_dir': remote_dir,
                'total_files': len(files_to_upload),
                'uploaded_files': len(uploaded_files),
                'failed_files': len(failed_files),
                'total_size': total_size,
                'transfer_time': round(transfer_time, 3),
                'uploaded_file_list': uploaded_files,
                'failed_file_list': failed_files,
                'success': len(failed_files) == 0
            }

        except Exception as e:
            raise SFTPTransferError(f"上传目录失败: {str(e)}", local_dir, remote_dir)

    def download_directory(self,
                           remote_dir: str,
                           local_dir: str,
                           progress_callback: Optional[Callable[[str, int, int], None]] = None,
                           preserve_times: bool = True) -> Dict[str, Union[int, List, float]]:
        """
        下载目录

        Args:
            remote_dir: 远程目录路径
            local_dir: 本地目录路径
            progress_callback: 进度回调函数
            preserve_times: 是否保持文件时间戳

        Returns:
            下载结果统计
        """
        if not self.is_connected():
            self.connect()

        try:
            logger.info(f"开始下载目录: {remote_dir} -> {local_dir}")
            start_time = time.time()

            # 获取远程目录中的所有文件
            files_to_download = self._get_remote_files(remote_dir)

            downloaded_files = []
            failed_files = []
            total_size = 0

            for i, (remote_file, remote_stat) in enumerate(files_to_download):
                try:
                    if progress_callback:
                        progress_callback(remote_file, i + 1, len(files_to_download))

                    # 计算本地文件路径
                    relative_path = os.path.relpath(remote_file, remote_dir)
                    local_file_path = os.path.join(local_dir, relative_path)

                    # 下载文件
                    result = self.download_file(remote_file, local_file_path, preserve_times=preserve_times)
                    downloaded_files.append(result)
                    total_size += result['file_size']

                except Exception as e:
                    failed_files.append({'file': remote_file, 'error': str(e)})
                    logger.error(f"下载文件失败: {remote_file} - {e}")

            transfer_time = time.time() - start_time

            logger.info(f"目录下载完成: 成功 {len(downloaded_files)}, 失败 {len(failed_files)}")

            return {
                'remote_dir': remote_dir,
                'local_dir': local_dir,
                'total_files': len(files_to_download),
                'downloaded_files': len(downloaded_files),
                'failed_files': len(failed_files),
                'total_size': total_size,
                'transfer_time': round(transfer_time, 3),
                'downloaded_file_list': downloaded_files,
                'failed_file_list': failed_files,
                'success': len(failed_files) == 0
            }

        except Exception as e:
            raise SFTPTransferError(f"下载目录失败: {str(e)}", local_dir, remote_dir)

    def list_directory(self, remote_path: str, detailed: bool = False) -> List[Dict[str, Union[str, int]]]:
        """
        列出远程目录内容

        Args:
            remote_path: 远程目录路径
            detailed: 是否返回详细信息

        Returns:
            目录内容列表
        """
        if not self.is_connected():
            self.connect()

        try:
            items = []

            if detailed:
                for item in self._sftp_client.listdir_attr(remote_path):
                    file_type = 'directory' if stat.S_ISDIR(item.st_mode) else 'file'
                    items.append({
                        'name': item.filename,
                        'type': file_type,
                        'size': item.st_size,
                        'mode': oct(item.st_mode),
                        'uid': item.st_uid,
                        'gid': item.st_gid,
                        'atime': item.st_atime,
                        'mtime': item.st_mtime
                    })
            else:
                for item_name in self._sftp_client.listdir(remote_path):
                    item_path = os.path.join(remote_path, item_name)
                    try:
                        item_stat = self._sftp_client.stat(item_path)
                        file_type = 'directory' if stat.S_ISDIR(item_stat.st_mode) else 'file'
                        items.append({
                            'name': item_name,
                            'type': file_type
                        })
                    except:
                        items.append({
                            'name': item_name,
                            'type': 'unknown'
                        })

            return items

        except Exception as e:
            raise SFTPException(f"列出目录失败: {str(e)}", remote_path=remote_path)

    def create_directory(self, remote_path: str, recursive: bool = False) -> bool:
        """
        创建远程目录

        Args:
            remote_path: 远程目录路径
            recursive: 是否递归创建

        Returns:
            是否成功
        """
        if not self.is_connected():
            self.connect()

        try:
            if recursive:
                # 递归创建目录
                path_parts = remote_path.strip('/').split('/')
                current_path = ''

                for part in path_parts:
                    current_path = current_path + '/' + part if current_path else part
                    try:
                        self._sftp_client.stat(current_path)
                    except FileNotFoundError:
                        self._sftp_client.mkdir(current_path)
                        logger.debug(f"创建目录: {current_path}")
            else:
                self._sftp_client.mkdir(remote_path)
                logger.info(f"创建目录: {remote_path}")

            return True

        except Exception as e:
            logger.error(f"创建目录失败: {remote_path} - {e}")
            return False

    def remove_file(self, remote_path: str) -> bool:
        """
        删除远程文件

        Args:
            remote_path: 远程文件路径

        Returns:
            是否成功
        """
        if not self.is_connected():
            self.connect()

        try:
            self._sftp_client.remove(remote_path)
            logger.info(f"删除文件: {remote_path}")
            return True
        except Exception as e:
            logger.error(f"删除文件失败: {remote_path} - {e}")
            return False

    def remove_directory(self, remote_path: str, recursive: bool = False) -> bool:
        """
        删除远程目录

        Args:
            remote_path: 远程目录路径
            recursive: 是否递归删除

        Returns:
            是否成功
        """
        if not self.is_connected():
            self.connect()

        try:
            if recursive:
                # 递归删除目录及其内容
                self._remove_directory_recursive(remote_path)
            else:
                self._sftp_client.rmdir(remote_path)

            logger.info(f"删除目录: {remote_path}")
            return True
        except Exception as e:
            logger.error(f"删除目录失败: {remote_path} - {e}")
            return False

    def file_exists(self, remote_path: str) -> bool:
        """
        检查远程文件是否存在

        Args:
            remote_path: 远程文件路径

        Returns:
            是否存在
        """
        if not self.is_connected():
            self.connect()

        try:
            self._sftp_client.stat(remote_path)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def get_file_info(self, remote_path: str) -> Dict[str, Union[str, int]]:
        """
        获取远程文件信息

        Args:
            remote_path: 远程文件路径

        Returns:
            文件信息
        """
        if not self.is_connected():
            self.connect()

        try:
            file_stat = self._sftp_client.stat(remote_path)

            return {
                'path': remote_path,
                'size': file_stat.st_size,
                'mode': oct(file_stat.st_mode),
                'uid': file_stat.st_uid,
                'gid': file_stat.st_gid,
                'atime': file_stat.st_atime,
                'mtime': file_stat.st_mtime,
                'is_file': stat.S_ISREG(file_stat.st_mode),
                'is_directory': stat.S_ISDIR(file_stat.st_mode)
            }

        except Exception as e:
            raise SFTPException(f"获取文件信息失败: {str(e)}", remote_path=remote_path)

    def _get_remote_files(self, remote_dir: str) -> List[tuple]:
        """递归获取远程目录中的所有文件"""
        files = []

        def walk_remote_dir(dir_path):
            try:
                for item in self._sftp_client.listdir_attr(dir_path):
                    item_path = os.path.join(dir_path, item.filename).replace('\\', '/')

                    if stat.S_ISDIR(item.st_mode):
                        walk_remote_dir(item_path)
                    else:
                        files.append((item_path, item))
            except Exception as e:
                logger.error(f"遍历远程目录失败: {dir_path} - {e}")

        walk_remote_dir(remote_dir)
        return files

    def _remove_directory_recursive(self, remote_path: str):
        """递归删除远程目录"""
        try:
            for item in self._sftp_client.listdir_attr(remote_path):
                item_path = os.path.join(remote_path, item.filename).replace('\\', '/')

                if stat.S_ISDIR(item.st_mode):
                    self._remove_directory_recursive(item_path)
                else:
                    self._sftp_client.remove(item_path)

            self._sftp_client.rmdir(remote_path)

        except Exception as e:
            logger.error(f"递归删除目录失败: {remote_path} - {e}")
            raise

    def __enter__(self):
        """上下文管理器入口"""
        if not self.is_connected():
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.disconnect()

    def __repr__(self):
        status = "连接中" if self.is_connected() else "未连接"
        return f"SFTPClient(host={self.ssh_client.hostname}, status={status})"
