#!/usr/bin/env python3
"""
RustFS S3 Storage Toolkit 测试文件
基于成功的 test_s3_flexible.py 创建的测试套件
已在 RustFS 1.0.0-alpha.34 上完成测试
"""

import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from rustfs_s3_toolkit import S3StorageToolkit


# 测试配置 - 请根据实际情况修改
TEST_CONFIG = {
    "endpoint_url": "https://rfs.jmsu.top",
    "access_key_id": "lingyuzeng",
    "secret_access_key": "rustAdminlingyuzeng",
    "bucket_name": "test",
    "region_name": "us-east-1"
}


def create_test_files():
    """创建测试文件和目录"""
    test_dir = tempfile.mkdtemp(prefix='s3_toolkit_test_')
    
    # 创建测试文件
    test_files = {
        "test.txt": "这是一个测试文件\n时间: " + datetime.now().isoformat(),
        "data.json": '{"name": "test", "value": 123, "timestamp": "' + datetime.now().isoformat() + '"}',
        "readme.md": "# 测试文件\n\n这是一个测试用的 Markdown 文件。\n\n- 项目: S3 存储测试\n- 时间: " + datetime.now().isoformat(),
    }
    
    # 创建子目录和文件
    sub_dir = Path(test_dir) / "subdir"
    sub_dir.mkdir()
    
    for filename, content in test_files.items():
        file_path = Path(test_dir) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # 在子目录中创建文件
    sub_file = sub_dir / "sub_test.txt"
    with open(sub_file, 'w', encoding='utf-8') as f:
        f.write("子目录中的测试文件\n时间: " + datetime.now().isoformat())
    
    return test_dir


def test_all_functions():
    """测试所有 9 个核心功能"""
    print("🚀 RustFS S3 Storage Toolkit 完整功能测试")
    print("🧪 测试环境: RustFS 1.0.0-alpha.34")
    print("=" * 60)
    
    # 初始化工具包
    try:
        toolkit = S3StorageToolkit(**TEST_CONFIG)
        print("✅ 工具包初始化成功")
    except Exception as e:
        print(f"❌ 工具包初始化失败: {e}")
        return False
    
    test_results = {}
    
    # 1. 测试连接
    print("\n1. 测试连接...")
    result = toolkit.test_connection()
    test_results['connection'] = result['success']
    if result['success']:
        print(f"✅ 连接成功: {result['message']}")
    else:
        print(f"❌ 连接失败: {result['error']}")
        return test_results
    
    # 2. 测试上传文件
    print("\n2. 测试上传文件...")
    test_content = f"测试文件内容\n时间: {datetime.now().isoformat()}"
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
        f.write(test_content)
        test_file = f.name
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    remote_key = f"test_files/single_file_{timestamp}.txt"
    
    result = toolkit.upload_file(test_file, remote_key)
    test_results['upload_file'] = result['success']
    if result['success']:
        print(f"✅ 文件上传成功: {remote_key}")
        uploaded_file_key = remote_key
    else:
        print(f"❌ 文件上传失败: {result['error']}")
        uploaded_file_key = None
    
    os.unlink(test_file)
    
    # 3. 测试创建文件夹
    print("\n3. 测试创建文件夹...")
    folder_path = f"test_folders/folder_{timestamp}/"
    result = toolkit.create_folder(folder_path)
    test_results['create_folder'] = result['success']
    if result['success']:
        print(f"✅ 文件夹创建成功: {folder_path}")
    else:
        print(f"❌ 文件夹创建失败: {result['error']}")
    
    # 4. 测试上传目录
    print("\n4. 测试上传目录...")
    test_dir = create_test_files()
    remote_prefix = f"test_directories/dir_{timestamp}/"
    
    result = toolkit.upload_directory(test_dir, remote_prefix)
    test_results['upload_directory'] = result['success']
    if result['success']:
        print(f"✅ 目录上传成功: 上传了 {result['file_count']} 个文件")
        uploaded_dir_prefix = remote_prefix
    else:
        print(f"❌ 目录上传失败: {result['error']}")
        uploaded_dir_prefix = None
    
    shutil.rmtree(test_dir)
    
    # 5. 测试下载文件
    print("\n5. 测试下载文件...")
    if uploaded_file_key:
        download_path = tempfile.mktemp(suffix='_downloaded.txt')
        result = toolkit.download_file(uploaded_file_key, download_path)
        test_results['download_file'] = result['success']
        if result['success']:
            print(f"✅ 文件下载成功: {download_path}")
            # 验证内容
            with open(download_path, 'r', encoding='utf-8') as f:
                downloaded_content = f.read()
            if test_content == downloaded_content:
                print("✅ 文件内容验证成功")
            else:
                print("❌ 文件内容验证失败")
            os.unlink(download_path)
        else:
            print(f"❌ 文件下载失败: {result['error']}")
    else:
        test_results['download_file'] = False
        print("❌ 跳过文件下载测试（没有可下载的文件）")
    
    # 6. 测试下载目录
    print("\n6. 测试下载目录...")
    if uploaded_dir_prefix:
        download_dir = tempfile.mkdtemp(prefix='s3_download_')
        result = toolkit.download_directory(uploaded_dir_prefix, download_dir)
        test_results['download_directory'] = result['success']
        if result['success']:
            print(f"✅ 目录下载成功: 下载了 {result['file_count']} 个文件")
        else:
            print(f"❌ 目录下载失败: {result['error']}")
        shutil.rmtree(download_dir)
    else:
        test_results['download_directory'] = False
        print("❌ 跳过目录下载测试（没有可下载的目录）")
    
    # 7. 测试列出文件
    print("\n7. 测试列出文件...")
    result = toolkit.list_files(max_keys=20)
    test_results['list_files'] = result['success']
    if result['success']:
        print(f"✅ 文件列表获取成功: 找到 {result['file_count']} 个文件")
        if result['files']:
            print("📄 前几个文件:")
            for i, file_info in enumerate(result['files'][:5], 1):
                size_mb = file_info['size'] / (1024 * 1024)
                print(f"   {i}. {file_info['key']} ({size_mb:.2f} MB)")
    else:
        print(f"❌ 文件列表获取失败: {result['error']}")
    
    # 8. 测试删除文件
    print("\n8. 测试删除文件...")
    if uploaded_file_key:
        result = toolkit.delete_file(uploaded_file_key)
        test_results['delete_file'] = result['success']
        if result['success']:
            print(f"✅ 文件删除成功: {uploaded_file_key}")
        else:
            print(f"❌ 文件删除失败: {result['error']}")
    else:
        test_results['delete_file'] = False
        print("❌ 跳过文件删除测试（没有可删除的文件）")
    
    # 9. 测试删除目录
    print("\n9. 测试删除目录...")
    if uploaded_dir_prefix:
        result = toolkit.delete_directory(uploaded_dir_prefix)
        test_results['delete_directory'] = result['success']
        if result['success']:
            print(f"✅ 目录删除成功: 删除了 {result['deleted_count']} 个文件")
        else:
            print(f"❌ 目录删除失败: {result['error']}")
    else:
        test_results['delete_directory'] = False
        print("❌ 跳过目录删除测试（没有可删除的目录）")
    
    # 打印测试摘要
    print("\n" + "="*60)
    print("🎯 测试结果摘要")
    print("="*60)
    
    test_names = {
        'connection': 'Connection',
        'upload_file': 'Upload File',
        'create_folder': 'Create Folder',
        'upload_directory': 'Upload Directory',
        'download_file': 'Download File',
        'download_directory': 'Download Directory',
        'list_files': 'List Files',
        'delete_file': 'Delete File',
        'delete_directory': 'Delete Directory'
    }
    
    passed_tests = 0
    for test_key, test_name in test_names.items():
        status = "✅ 通过" if test_results.get(test_key, False) else "❌ 失败"
        print(f"{test_name:20} : {status}")
        if test_results.get(test_key, False):
            passed_tests += 1
    
    print("-" * 60)
    print(f"总计: {passed_tests}/{len(test_names)} 个测试通过")
    
    if passed_tests == len(test_names):
        print("🎉 所有测试都通过了！RustFS S3 Storage Toolkit 工作正常。")
    elif passed_tests > 0:
        print("⚠️ 部分测试通过。请检查失败的测试项。")
    else:
        print("❌ 所有测试都失败了。请检查 RustFS 配置和网络连接。")
    
    return test_results


if __name__ == "__main__":
    test_all_functions()
