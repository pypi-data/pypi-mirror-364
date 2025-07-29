#!/usr/bin/env python3
"""
S3 Storage Toolkit
一个易于使用的 S3 兼容对象存储工具包，支持 RustFS 等各种 S3 兼容存储
"""

import os
import shutil
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, NoCredentialsError


class S3StorageToolkit:
    """S3 兼容对象存储工具包

    支持以下功能：
    1. 连接测试
    2. 文件上传
    3. 文件夹创建
    4. 目录上传
    5. 文件下载
    6. 目录下载
    7. 文件列表
    8. 文件删除
    9. 目录删除
    """

    def __init__(
        self,
        endpoint_url: str,
        access_key_id: str,
        secret_access_key: str,
        bucket_name: str,
        region_name: str = "us-east-1"
    ):
        """
        初始化 S3 存储工具包

        Args:
            endpoint_url: S3 服务端点 URL
            access_key_id: 访问密钥 ID
            secret_access_key: 访问密钥
            bucket_name: 存储桶名称
            region_name: 区域名称，默认 us-east-1
        """
        self.endpoint_url = endpoint_url
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.bucket_name = bucket_name
        self.region_name = region_name

        # 存储不同操作类型的客户端
        self._clients = {}

    def _create_s3_client(self, operation_type: str = "general"):
        """创建 S3 客户端，根据操作类型选择最佳配置"""
        if operation_type in self._clients:
            return self._clients[operation_type]

        try:
            if operation_type == "upload":
                # 对于上传操作，使用 V2 签名（避免 SHA256 问题）
                configs_to_try = [
                    {
                        'signature_version': 's3',  # V2 签名
                        's3': {'addressing_style': 'path'}
                    },
                    {
                        'signature_version': 's3v4',
                        's3': {
                            'addressing_style': 'path',
                            'payload_signing_enabled': False
                        }
                    }
                ]
            else:
                # 对于列表、删除等操作，使用 V4 签名
                configs_to_try = [
                    {
                        'signature_version': 's3v4',
                        's3': {
                            'addressing_style': 'path',
                            'payload_signing_enabled': False
                        }
                    },
                    {
                        'signature_version': 's3',  # V2 签名作为备选
                        's3': {'addressing_style': 'path'}
                    }
                ]

            for config in configs_to_try:
                try:
                    s3_client = boto3.client(
                        's3',
                        endpoint_url=self.endpoint_url,
                        aws_access_key_id=self.access_key_id,
                        aws_secret_access_key=self.secret_access_key,
                        region_name=self.region_name,
                        config=Config(**config)
                    )

                    # 测试连接
                    s3_client.list_buckets()
                    self._clients[operation_type] = s3_client
                    return s3_client

                except Exception:
                    continue

            raise Exception("所有配置都失败了")

        except Exception as e:
            raise RuntimeError(f"创建 S3 客户端失败: {str(e)}")

    def test_connection(self) -> Dict[str, Union[bool, str, List[str]]]:
        """测试 S3 连接

        Returns:
            包含连接测试结果的字典
        """
        try:
            s3_client = self._create_s3_client()

            # 尝试列出存储桶
            response = s3_client.list_buckets()
            buckets = response.get('Buckets', [])
            bucket_names = [bucket['Name'] for bucket in buckets]

            # 检查目标存储桶是否存在
            bucket_exists = self.bucket_name in bucket_names

            return {
                "success": True,
                "bucket_count": len(buckets),
                "bucket_names": bucket_names,
                "target_bucket_exists": bucket_exists,
                "message": f"连接成功！找到 {len(buckets)} 个存储桶"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"连接测试失败: {str(e)}"
            }
    
    def upload_file(
        self,
        local_file_path: str,
        remote_key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Union[bool, str, int]]:
        """
        上传文件到 S3

        Args:
            local_file_path: 本地文件路径
            remote_key: 远程对象键
            metadata: 可选的元数据

        Returns:
            包含上传信息的字典
        """
        try:
            local_path = Path(local_file_path)
            if not local_path.exists():
                return {
                    "success": False,
                    "error": f"本地文件不存在: {local_file_path}"
                }

            s3_client = self._create_s3_client("upload")

            # 读取文件内容
            with open(local_path, 'rb') as f:
                file_content = f.read()

            # 上传文件
            upload_args = {
                'Bucket': self.bucket_name,
                'Key': remote_key,
                'Body': file_content,
                'ContentType': 'application/octet-stream'
            }

            if metadata:
                upload_args['Metadata'] = metadata

            s3_client.put_object(**upload_args)

            # 生成公开访问 URL
            public_url = f"{self.endpoint_url}/{self.bucket_name}/{remote_key}"

            return {
                "success": True,
                "bucket": self.bucket_name,
                "key": remote_key,
                "public_url": public_url,
                "file_size": local_path.stat().st_size,
                "upload_time": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"上传文件失败: {str(e)}"
            }

    def create_folder(self, folder_path: str) -> Dict[str, Union[bool, str]]:
        """
        创建文件夹（通过上传空对象）

        Args:
            folder_path: 文件夹路径，会自动添加 '/' 后缀

        Returns:
            包含创建结果的字典
        """
        try:
            s3_client = self._create_s3_client("upload")

            # 确保文件夹路径以 '/' 结尾
            if not folder_path.endswith('/'):
                folder_path += '/'

            # S3 中通过上传空对象来创建"文件夹"
            s3_client.put_object(
                Bucket=self.bucket_name,
                Key=folder_path,
                Body=b''
            )

            return {
                "success": True,
                "bucket": self.bucket_name,
                "folder_path": folder_path,
                "create_time": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"创建文件夹失败: {str(e)}"
            }
    
    def upload_directory(
        self,
        local_dir: str,
        remote_prefix: str = ""
    ) -> Dict[str, Union[bool, str, int, List[str]]]:
        """
        上传整个目录到 S3

        Args:
            local_dir: 本地目录路径
            remote_prefix: 远程路径前缀

        Returns:
            包含上传结果的字典
        """
        try:
            local_path = Path(local_dir)
            if not local_path.exists() or not local_path.is_dir():
                return {
                    "success": False,
                    "error": f"本地目录不存在或不是目录: {local_dir}"
                }

            s3_client = self._create_s3_client("upload")
            uploaded_files = []

            # 递归上传目录中的所有文件
            for root, dirs, files in os.walk(local_path):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file_path, local_path)

                    # 构建远程键
                    if remote_prefix:
                        remote_key = f"{remote_prefix.rstrip('/')}/{relative_path.replace(os.sep, '/')}"
                    else:
                        remote_key = relative_path.replace(os.sep, '/')

                    # 上传文件
                    s3_client.upload_file(local_file_path, self.bucket_name, remote_key)
                    uploaded_files.append(remote_key)

            return {
                "success": True,
                "bucket": self.bucket_name,
                "local_directory": str(local_path),
                "remote_prefix": remote_prefix,
                "uploaded_files": uploaded_files,
                "file_count": len(uploaded_files),
                "upload_time": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"上传目录失败: {str(e)}"
            }

    def download_file(
        self,
        remote_key: str,
        local_file_path: str
    ) -> Dict[str, Union[bool, str, int]]:
        """
        从 S3 下载文件

        Args:
            remote_key: 远程对象键
            local_file_path: 本地保存路径

        Returns:
            包含下载信息的字典
        """
        try:
            s3_client = self._create_s3_client("upload")  # 使用上传客户端进行下载
            local_path = Path(local_file_path)

            # 确保本地目录存在
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # 下载文件
            s3_client.download_file(
                self.bucket_name,
                remote_key,
                str(local_path)
            )

            return {
                "success": True,
                "bucket": self.bucket_name,
                "key": remote_key,
                "local_path": str(local_path),
                "file_size": local_path.stat().st_size,
                "download_time": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"下载文件失败: {str(e)}"
            }
    
    def download_directory(
        self,
        remote_prefix: str,
        local_dir: str
    ) -> Dict[str, Union[bool, str, int, List[str]]]:
        """
        从 S3 下载整个目录

        Args:
            remote_prefix: 远程路径前缀
            local_dir: 本地保存目录

        Returns:
            包含下载结果的字典
        """
        try:
            s3_client = self._create_s3_client("list")
            local_path = Path(local_dir)
            local_path.mkdir(parents=True, exist_ok=True)

            # 列出远程目录中的所有文件
            response = s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=remote_prefix
            )

            downloaded_files = []
            for obj in response.get('Contents', []):
                key = obj['Key']

                # 跳过文件夹对象
                if key.endswith('/'):
                    continue

                # 计算本地文件路径
                relative_path = key[len(remote_prefix):].lstrip('/')
                if not relative_path:
                    continue

                local_file_path = local_path / relative_path
                local_file_path.parent.mkdir(parents=True, exist_ok=True)

                # 下载文件
                s3_client.download_file(self.bucket_name, key, str(local_file_path))
                downloaded_files.append(str(local_file_path))

            return {
                "success": True,
                "bucket": self.bucket_name,
                "remote_prefix": remote_prefix,
                "local_directory": str(local_path),
                "downloaded_files": downloaded_files,
                "file_count": len(downloaded_files),
                "download_time": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"下载目录失败: {str(e)}"
            }

    def list_files(
        self,
        prefix: str = "",
        max_keys: int = 1000
    ) -> Dict[str, Union[bool, str, int, List[Dict]]]:
        """
        列出 S3 中的文件

        Args:
            prefix: 文件前缀过滤
            max_keys: 最大返回数量

        Returns:
            包含文件列表的字典
        """
        try:
            s3_client = self._create_s3_client("list")

            # 尝试多种列表方法
            list_methods = [
                lambda: s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=prefix,
                    MaxKeys=max_keys
                ),
                lambda: s3_client.list_objects(
                    Bucket=self.bucket_name,
                    Prefix=prefix,
                    MaxKeys=max_keys
                )
            ]

            response = None
            for method in list_methods:
                try:
                    response = method()
                    break
                except Exception:
                    continue

            if response is None:
                return {
                    "success": False,
                    "error": "所有列表方法都失败了"
                }

            files = []
            for obj in response.get('Contents', []):
                files.append({
                    "key": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat(),
                    "public_url": f"{self.endpoint_url}/{self.bucket_name}/{obj['Key']}"
                })

            return {
                "success": True,
                "bucket": self.bucket_name,
                "prefix": prefix,
                "files": files,
                "file_count": len(files),
                "list_time": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"列出文件失败: {str(e)}"
            }
    
    def delete_file(self, remote_key: str) -> Dict[str, Union[bool, str]]:
        """
        删除 S3 中的文件

        Args:
            remote_key: 远程对象键

        Returns:
            包含删除结果的字典
        """
        try:
            s3_client = self._create_s3_client("delete")

            # 删除文件
            s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=remote_key
            )

            # 验证文件已被删除
            try:
                s3_client.head_object(Bucket=self.bucket_name, Key=remote_key)
                return {
                    "success": False,
                    "error": "文件删除验证失败：文件仍然存在"
                }
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    return {
                        "success": True,
                        "bucket": self.bucket_name,
                        "key": remote_key,
                        "delete_time": datetime.now().isoformat()
                    }
                else:
                    raise e

        except Exception as e:
            return {
                "success": False,
                "error": f"删除文件失败: {str(e)}"
            }

    def delete_directory(self, remote_prefix: str) -> Dict[str, Union[bool, str, int, List[str]]]:
        """
        删除 S3 中的整个目录

        Args:
            remote_prefix: 远程路径前缀

        Returns:
            包含删除结果的字典
        """
        try:
            s3_client = self._create_s3_client("delete")

            # 首先列出目录中的所有文件
            response = s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=remote_prefix
            )

            objects = response.get('Contents', [])
            if not objects:
                return {
                    "success": True,
                    "message": "目录为空或不存在",
                    "deleted_count": 0
                }

            # 尝试批量删除
            try:
                delete_response = s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': [{'Key': obj['Key']} for obj in objects]}
                )

                deleted_count = len(delete_response.get('Deleted', []))
                errors = delete_response.get('Errors', [])

                if errors:
                    error_messages = [f"{error['Key']}: {error['Message']}" for error in errors]
                    return {
                        "success": False,
                        "error": f"批量删除部分失败: {error_messages}",
                        "deleted_count": deleted_count,
                        "failed_count": len(errors)
                    }

                return {
                    "success": True,
                    "bucket": self.bucket_name,
                    "remote_prefix": remote_prefix,
                    "deleted_count": deleted_count,
                    "delete_time": datetime.now().isoformat()
                }

            except Exception:
                # 如果批量删除失败，尝试逐个删除
                deleted_count = 0
                failed_files = []

                for obj in objects:
                    try:
                        s3_client.delete_object(Bucket=self.bucket_name, Key=obj['Key'])
                        deleted_count += 1
                    except Exception as e:
                        failed_files.append(f"{obj['Key']}: {str(e)}")

                if failed_files:
                    return {
                        "success": False,
                        "error": f"逐个删除部分失败: {failed_files}",
                        "deleted_count": deleted_count,
                        "failed_count": len(failed_files)
                    }

                return {
                    "success": True,
                    "bucket": self.bucket_name,
                    "remote_prefix": remote_prefix,
                    "deleted_count": deleted_count,
                    "delete_time": datetime.now().isoformat()
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"删除目录失败: {str(e)}"
            }
