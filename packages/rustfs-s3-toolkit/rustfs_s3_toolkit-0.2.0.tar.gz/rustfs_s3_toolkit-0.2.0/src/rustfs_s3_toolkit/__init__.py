"""
RustFS S3 Storage Toolkit
一个专为 RustFS 设计的 S3 兼容对象存储工具包，同时支持其他各种 S3 兼容存储
"""

__version__ = "0.2.0"
__author__ = "mm644706215"
__email__ = "ze.ga@qq.com"

from .s3_client import S3StorageToolkit

__all__ = [
    "S3StorageToolkit",
]
