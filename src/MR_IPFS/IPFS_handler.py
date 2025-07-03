# 网络请求
import requests

IPFS_API_URL = "http://127.0.0.1:5001"
IPFS_GATEWAY_URL = "http://127.0.0.1:8080"
TIME_OUT = (10, 300)

def upload_file_to_ipfs(file_path: str):
    """
    上传文件到IPFS并返回CID
    输入: 文件路径
    输出: CID字符串
    """
    
    try:
        with open(file_path, "rb") as f:
            response = requests.post(f"{IPFS_API_URL}/api/v0/add", params={"pin": "true"}, files = {"file": f}, timeout = TIME_OUT)
        response.raise_for_status()
        result = response.json()
        return result["Hash"]
    
    except Exception as e:
        raise RuntimeError(f"上传IPFS文件失败: {e}") from e

def download_file_from_ipfs(cid: str):
    """
    从IPFS检测文件是否存在并返回下载地址
    输入: CID字符串
    输出: 下载地址
    """
    
    try:
        download_url = f"{IPFS_GATEWAY_URL}/ipfs/{cid}"
        response = requests.get(download_url, timeout = TIME_OUT)
        response.raise_for_status()
        return download_url
    
    except Exception as e:
        raise RuntimeError(f"下载IPFS文件失败: {e}") from e

def get_file_content_from_ipfs(cid: str):
    """
    从IPFS获取文本文件内容
    输入: CID字符串
    输出: 文件内容字符串
    """
    
    try:
        response = requests.post(f"{IPFS_API_URL}/api/v0/cat?arg={cid}", timeout = TIME_OUT)
        response.raise_for_status()
        return response.content.decode("utf-8")[:5000]  # 限制返回内容大小
    
    except Exception as e:
        raise RuntimeError(f"下载IPFS文件失败: {e}") from e