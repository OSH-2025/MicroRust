import requests

IPFS_API_URL = "http://127.0.0.1:5001"

def upload_file_to_ipfs(file_path: str) -> str:
    """
    上传文件到IPFS并返回CID
    输入：文件路径
    输出：CID字符串
    """
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{IPFS_API_URL}/api/v0/add",
                files={"file": f},
                timeout=30
            )
        response.raise_for_status()
        result = response.json()
        return result["Hash"]
    except Exception as e:
        return f"上传失败: {str(e)}"

def get_file_content_from_ipfs(cid: str) -> str:
    """
    从IPFS获取文本文件内容
    输入：CID字符串
    输出：文件内容字符串
    """
    try:
        response = requests.post(
            f"{IPFS_API_URL}/api/v0/cat?arg={cid}",
            timeout=30,
            stream=True
        )
        response.raise_for_status()
        return response.text[:5000]  # 限制返回内容大小
    except Exception as e:
        return f"读取失败: {str(e)}"

def download_file_from_ipfs(cid: str, save_path: str) -> str:
    """
    从IPFS下载文件到本地
    输入：CID字符串，保存路径
    输出：保存的文件路径或错误信息
    """
    raise NotImplementedError("IPFS 下载功能尚未实现")