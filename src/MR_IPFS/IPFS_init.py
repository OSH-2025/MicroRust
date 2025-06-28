# 文件与路径操作
import os

# 系统信息与交互
import platform
import subprocess

# 时间处理
import time

# 网络请求
import requests

IPFS_API_URL = "http://127.0.0.1:5001"
IPFS_GATEWAY_URL = "http://127.0.0.1:8080"
TIME_OUT = (10, 300)

def start_ipfs():
    """启动IPFS节点"""
    
    try:
        # 检查IPFS仓库是否存在
        system = platform.system()
        
        if system == "Windows":
            ipfs_path = os.path.join(os.environ.get("USERPROFILE") or "{}", ".ipfs")
        
        else:
            ipfs_path = os.path.expanduser("~/.ipfs")
        
        # 初始化IPFS仓库
        if not os.path.exists(ipfs_path):
            print("初始化IPFS仓库")
            subprocess.run(["ipfs", "init"], check = True)
        
        # 启动IPFS节点
        print("启动IPFS节点")
        # ipfsexe_paths = (subprocess.run(["where", "ipfs"],capture_output = True, text = True, check = True)).stdout.strip().splitlines()
        ipfsexe_path = r"C:\Users\hswilliam2023\.ipfs_bin\ipfs.exe"
        daemon = subprocess.Popen([ipfsexe_path, "daemon"], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
        time.sleep(5)
        return daemon
    
    except Exception as e:
        print(f"IPFS节点启动失败: {str(e)}")
        return None

def terminate_ipfs(daemon: subprocess.Popen):
    """关闭IPFS节点"""
    
    try:
        print("关闭IPFS节点")
        daemon.terminate()
        daemon.wait()
    
    except Exception as e:
        print(f"IPFS节点关闭失败: {str(e)}")

def connect_ipfs():
    """连接本地IPFS节点"""
    
    try:
        print("连接本地IPFS节点")
        response = requests.post(f"{IPFS_API_URL}/api/v0/id", timeout = TIME_OUT)
        response.raise_for_status()
        
        info = response.json()
        addresses = info.get("Addresses", [])
        
        if not isinstance(addresses, (list, tuple)):
            print("Addresses字段格式异常")
            return None
        
        if not addresses:
            print("Addresses为空")
            return None
        
        # 优先选择公网IPv4和DNS地址，排除局域网地址
        for addr in addresses:
            if addr.startswith("/ip4/") and not any(addr.startswith(prefix) for prefix in ["/ip4/127.", "/ip4/192.", "/ip4/10."]):
                return addr
            
            if addr.startswith("/dns/"):
                return addr
        
        # 未找到合适地址，返回地址列表中的第一个地址
        return addresses[0]
    
    except Exception as e:
        print(f"IPFS节点启动失败: {str(e)}")
        return None