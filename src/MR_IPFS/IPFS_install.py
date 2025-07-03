# 文件与路径操作
import os
import shutil
from pathlib import Path

# 系统信息与交互
import sys
import platform
import subprocess

# 压缩与归档处理
import zipfile
import tarfile

# 网络请求
import urllib.request

IPFS_API_URL = "http://127.0.0.1:5001"
IPFS_GATEWAY_URL = "http://127.0.0.1:8080"
TIME_OUT = (10, 300)

def get_ipfs_download_info():
    version = "v0.23.0"  # 使用0.23.0版本的IPFS
    system = platform.system().lower()
    arch = platform.machine().lower()

    if system == "windows" and arch in ("amd64", "x86_64"):
        filename = f"go-ipfs_{version}_windows-amd64.zip"
        url = f"https://dist.ipfs.io/go-ipfs/{version}/{filename}"
        return (url, filename, "windows")
    
    elif system == "linux" and arch in ("x86_64", "amd64"):
        filename = f"go-ipfs_{version}_linux-amd64.tar.gz"
        url = f"https://dist.ipfs.io/go-ipfs/{version}/{filename}"
        return (url, filename, "linux")
    
    else:
        raise Exception(f"不支持的平台: {system} {arch}")

def download_file(url, dest):
    print(f"正在下载{url}")
    urllib.request.urlretrieve(url, dest)
    print("下载完成")

def extract_windows_zip(file_path, extract_path):
    print(f"正在解压{file_path}到{extract_path}")
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(path = extract_path)
    print("解压完成")

def extract_linux_tar_gz(file_path, extract_path):
    print(f"正在解压{file_path}到{extract_path}")
    with tarfile.open(file_path, "r:gz") as tar:
        tar.extractall(path = extract_path)
    print("解压完成")

def install_ipfs_windows(extract_path, install_path):
    ipfs_exe_path = os.path.join(extract_path, "go-ipfs", "ipfs.exe")
    if not os.path.isfile(ipfs_exe_path):
        raise Exception("解压后未找到ipfs.exe文件")
    
    os.makedirs(install_path, exist_ok = True)
    target_path = os.path.join(install_path, "ipfs.exe")
    print(f"正在安装ipfs.exe到{install_path}")

    shutil.copy(ipfs_exe_path, target_path)
    print("安装完成")
    return target_path

def install_ipfs_linux(extract_path, install_path):
    ipfs_bin_path = os.path.join(extract_path, "go-ipfs", "ipfs")
    if not os.path.isfile(ipfs_bin_path):
        raise Exception("解压后未找到ipfs文件")
    
    target_path = os.path.join(install_path, "ipfs")
    print(f"正在安装ipfs到{install_path}")

    shutil.copy(ipfs_bin_path, install_path)
    os.chmod(target_path, 0o755)
    print("安装完成")

def ipfs_init(ipfs_path):
    print("正在初始化IPFS节点")
    res = subprocess.run([ipfs_path, "init"], capture_output = True, text = True)
    print(res.stdout)
    
    if res.returncode != 0:
        print("警告: ", res.stderr)

    else:
        print("IPFS节点初始化成功")

def main():
    try:
        (url, filename, system) = get_ipfs_download_info()
    
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

    download_path = os.path.join(os.getcwd(), filename)
    extract_path = os.path.join(os.getcwd(), "ipfs_temp")

    # Windows放在用户目录下.ipfs_bin
    # Linux默认安装目录/usr/local/bin需要管理员权限
    user_bin_dir = os.path.join(Path.home(), ".ipfs_bin") if system == "windows" else "/usr/local/bin"

    try:
        download_file(url, download_path)

        if system == "windows":
            extract_windows_zip(download_path, extract_path)
            ipfs_path = install_ipfs_windows(extract_path, user_bin_dir)
        
        else:
            extract_linux_tar_gz(download_path, extract_path)
            install_ipfs_linux(extract_path, user_bin_dir)
            ipfs_path = os.path.join(user_bin_dir, "ipfs")
        
        ipfs_init(ipfs_path)
        print(f"请确保{user_bin_dir}在你的系统PATH环境变量中, 以便直接使用ipfs命令")
    
    finally:
        if os.path.exists(download_path):
            os.remove(download_path)
        
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        
        print("清理临时文件完成")

if __name__ == "__main__":
    main()