# 文件与路径操作
import os

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
            response = requests.post(f"{IPFS_API_URL}/api/v0/add", files = {"file": f}, timeout = TIME_OUT)
        response.raise_for_status()
        result = response.json()
        return result["Hash"]
    
    except Exception as e:
        return f"上传失败: {str(e)}"

def download_file_from_ipfs(cid: str, file_dir: str, file_name: str):
    """
    从IPFS下载文件到本地
    输入: CID字符串, 保存路径
    输出: 保存的文件路径或错误信息
    """

    try:
        response = requests.get(f"{IPFS_GATEWAY_URL}/ipfs/{cid}", timeout = TIME_OUT, stream = True)
        response.raise_for_status()
        file_path = os.path.join(file_dir, file_name)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return file_path
    
    except Exception as e:
        return f"下载失败: {str(e)}"

def get_file_content_from_ipfs(cid: str):
    """
    从IPFS获取文本文件内容
    输入: CID字符串
    输出: 文件内容字符串
    """

    try:
        response = requests.post(f"{IPFS_API_URL}/api/v0/cat?arg={cid}", timeout = TIME_OUT, stream=True)
        response.raise_for_status()
        return response.text[:5000]  # 限制返回内容大小
    
    except Exception as e:
        return f"读取失败: {str(e)}"