# RustFS S3 Storage Toolkit

一个专为 RustFS 设计的 S3 兼容对象存储工具包，同时支持其他各种 S3 兼容存储服务。提供完整的文件和目录操作功能，具有高度的可复用性和工具性。

## 🧪 测试环境

本工具包已在以下 RustFS 版本上完成全面测试：

```
rustfs 1.0.0-alpha.34
build time   : 2025-07-21 08:13:28 +00:00
build profile: release
build os     : linux-x86_64
rust version : rustc 1.88.0 (6b00bc388 2025-06-23)
rust channel : stable-x86_64-unknown-linux-gnu
git commit   : 3f095e75cb1276adf47a05472c8cc608eaa51504
git tag      : 1.0.0-alpha.34
```

**注意**: 虽然理论上兼容其他 S3 兼容服务，但建议在使用前进行自行测试以确保兼容性。

## 🚀 核心功能

本工具包提供以下 9 个核心功能，全部测试通过：

- ✅ **Connection (连接测试)**: 验证 S3 服务连接和存储桶访问权限
- ✅ **Upload File (上传文件)**: 上传单个文件到 S3 存储
- ✅ **Create Folder (创建文件夹)**: 在 S3 中创建文件夹结构
- ✅ **Upload Directory (上传目录)**: 递归上传整个目录及其子目录
- ✅ **Download File (下载文件)**: 从 S3 下载单个文件
- ✅ **Download Directory (下载目录)**: 下载整个目录及其所有文件
- ✅ **List Files (列出文件)**: 列出存储桶中的文件和目录
- ✅ **Delete File (删除文件)**: 删除 S3 中的单个文件
- ✅ **Delete Directory (删除目录)**: 删除整个目录及其所有文件

## 🎯 设计特点

- **易于使用**: 简单的类实例化和方法调用
- **高度可复用**: 一次配置，多次使用
- **工具性强**: 专注于核心功能，无冗余依赖
- **兼容性好**: 支持各种 S3 兼容存储服务
- **错误处理**: 完善的异常处理和错误信息返回
- **灵活配置**: 自动适配不同 S3 服务的签名要求

## 📦 安装

### 从 PyPI 安装 (推荐)

```bash
pip install rustfs-s3-toolkit
```

### 开发版本安装

```bash
# 克隆项目
git clone https://github.com/mm644706215/rustfs-s3-toolkit.git
cd rustfs-s3-toolkit

# 安装开发版本
pip install -e .
```

## 🔧 支持的存储服务

### 已测试服务
- **RustFS 1.0.0-alpha.34**: 主要测试目标，所有功能完全兼容 ✅

### 理论兼容服务（需自行测试）
- **AWS S3**: 亚马逊云存储服务
- **MinIO**: 开源对象存储服务
- **Alibaba Cloud OSS**: 阿里云对象存储
- **Tencent Cloud COS**: 腾讯云对象存储
- **其他 S3 兼容服务**: 任何支持 S3 API 的存储服务

**重要提示**: 除 RustFS 1.0.0-alpha.34 外，其他服务虽然理论上兼容，但建议在生产环境使用前进行充分测试。

## 📖 快速开始

### 基本使用

```python
from rustfs_s3_toolkit import S3StorageToolkit

# 初始化工具包（以 RustFS 为例）
toolkit = S3StorageToolkit(
    endpoint_url="https://your-rustfs-endpoint.com",
    access_key_id="your-access-key-id",
    secret_access_key="your-secret-access-key",
    bucket_name="your-bucket-name",
    region_name="us-east-1"  # 可选，默认 us-east-1
)

# 测试连接
result = toolkit.test_connection()
if result['success']:
    print(f"连接成功: {result['message']}")
else:
    print(f"连接失败: {result['error']}")
```

## 📚 详细使用方法

### 1. 连接测试 (Connection)

```python
# 测试 S3 连接和存储桶访问权限
result = toolkit.test_connection()

# 返回结果
{
    "success": True,
    "bucket_count": 5,
    "bucket_names": ["bucket1", "bucket2", ...],
    "target_bucket_exists": True,
    "message": "连接成功！找到 5 个存储桶"
}
```

### 2. 上传文件 (Upload File)

```python
# 上传单个文件
result = toolkit.upload_file(
    local_file_path="/path/to/local/file.txt",
    remote_key="remote/path/file.txt",
    metadata={"author": "user", "type": "document"}  # 可选
)

# 返回结果
{
    "success": True,
    "bucket": "your-bucket",
    "key": "remote/path/file.txt",
    "public_url": "https://endpoint/bucket/remote/path/file.txt",
    "file_size": 1024,
    "upload_time": "2024-01-01T12:00:00"
}
```

### 3. 创建文件夹 (Create Folder)

```python
# 创建文件夹（S3 中通过空对象实现）
result = toolkit.create_folder("my-folder/sub-folder/")

# 返回结果
{
    "success": True,
    "bucket": "your-bucket",
    "folder_path": "my-folder/sub-folder/",
    "create_time": "2024-01-01T12:00:00"
}
```

### 4. 上传目录 (Upload Directory)

```python
# 递归上传整个目录
result = toolkit.upload_directory(
    local_dir="/path/to/local/directory",
    remote_prefix="remote/directory/"
)

# 返回结果
{
    "success": True,
    "bucket": "your-bucket",
    "local_directory": "/path/to/local/directory",
    "remote_prefix": "remote/directory/",
    "uploaded_files": ["remote/directory/file1.txt", "remote/directory/sub/file2.txt"],
    "file_count": 2,
    "upload_time": "2024-01-01T12:00:00"
}
```

### 5. 下载文件 (Download File)

```python
# 下载单个文件
result = toolkit.download_file(
    remote_key="remote/path/file.txt",
    local_file_path="/path/to/save/file.txt"
)

# 返回结果
{
    "success": True,
    "bucket": "your-bucket",
    "key": "remote/path/file.txt",
    "local_path": "/path/to/save/file.txt",
    "file_size": 1024,
    "download_time": "2024-01-01T12:00:00"
}
```

### 6. 下载目录 (Download Directory)

```python
# 下载整个目录
result = toolkit.download_directory(
    remote_prefix="remote/directory/",
    local_dir="/path/to/save/directory"
)

# 返回结果
{
    "success": True,
    "bucket": "your-bucket",
    "remote_prefix": "remote/directory/",
    "local_directory": "/path/to/save/directory",
    "downloaded_files": ["/path/to/save/directory/file1.txt", ...],
    "file_count": 2,
    "download_time": "2024-01-01T12:00:00"
}
```

### 7. 列出文件 (List Files)

```python
# 列出存储桶中的文件
result = toolkit.list_files(
    prefix="my-folder/",  # 可选，过滤前缀
    max_keys=100         # 可选，最大返回数量
)

# 返回结果
{
    "success": True,
    "bucket": "your-bucket",
    "prefix": "my-folder/",
    "files": [
        {
            "key": "my-folder/file1.txt",
            "size": 1024,
            "last_modified": "2024-01-01T12:00:00",
            "public_url": "https://endpoint/bucket/my-folder/file1.txt"
        }
    ],
    "file_count": 1,
    "list_time": "2024-01-01T12:00:00"
}
```

### 8. 删除文件 (Delete File)

```python
# 删除单个文件
result = toolkit.delete_file("remote/path/file.txt")

# 返回结果
{
    "success": True,
    "bucket": "your-bucket",
    "key": "remote/path/file.txt",
    "delete_time": "2024-01-01T12:00:00"
}
```

### 9. 删除目录 (Delete Directory)

```python
# 删除整个目录及其所有文件
result = toolkit.delete_directory("remote/directory/")

# 返回结果
{
    "success": True,
    "bucket": "your-bucket",
    "remote_prefix": "remote/directory/",
    "deleted_count": 5,
    "delete_time": "2024-01-01T12:00:00"
}
```

## 🔧 配置说明

### 基本配置参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `endpoint_url` | str | ✅ | S3 服务端点 URL |
| `access_key_id` | str | ✅ | 访问密钥 ID |
| `secret_access_key` | str | ✅ | 访问密钥 |
| `bucket_name` | str | ✅ | 存储桶名称 |
| `region_name` | str | ❌ | 区域名称，默认 "us-east-1" |

### 常见配置示例

#### AWS S3
```python
toolkit = S3StorageToolkit(
    endpoint_url="https://s3.amazonaws.com",
    access_key_id="AKIAIOSFODNN7EXAMPLE",
    secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    bucket_name="my-bucket",
    region_name="us-west-2"
)
```

#### MinIO
```python
toolkit = S3StorageToolkit(
    endpoint_url="http://localhost:9000",
    access_key_id="minioadmin",
    secret_access_key="minioadmin",
    bucket_name="my-bucket"
)
```

#### RustFS (已测试版本 1.0.0-alpha.34)
```python
toolkit = S3StorageToolkit(
    endpoint_url="https://your-rustfs-endpoint.com",
    access_key_id="your-access-key",
    secret_access_key="your-secret-key",
    bucket_name="your-bucket-name"
)
```

## 🧪 测试

运行完整的功能测试：

```bash
# 运行测试套件
python tests/test_toolkit.py

# 运行基本使用示例
python examples/basic_usage.py
```

测试将验证所有 9 个核心功能是否正常工作。

## 📁 项目结构

```
rustfs-s3-toolkit/
├── README.md                 # 项目文档
├── pyproject.toml           # 项目配置
├── LICENSE                  # MIT 许可证
├── install.py               # 安装脚本
├── build.py                 # 构建脚本
├── src/
│   └── rustfs_s3_toolkit/
│       ├── __init__.py      # 包初始化
│       └── s3_client.py     # 核心工具类
├── tests/
│   └── test_toolkit.py      # 测试套件
└── examples/
    └── basic_usage.py       # 使用示例
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [GitHub 仓库](https://github.com/mm644706215/rustfs-s3-toolkit)
- [PyPI 包](https://pypi.org/project/rustfs-s3-toolkit/)
- [问题反馈](https://github.com/mm644706215/rustfs-s3-toolkit/issues)

---

**RustFS S3 Storage Toolkit** - 专为 RustFS 设计，让 S3 对象存储操作变得简单高效！