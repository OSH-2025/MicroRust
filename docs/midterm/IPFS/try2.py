import requests
import os

class IPFSFileClient:
    def __init__(self, node_ip="192.168.220.128", port=5001):
        self.api_url = f"http://{node_ip}:{port}/api/v0"
    
    def upload_file(self, file_path):
        """上传本地文件到IPFS"""
        try:
            with open(file_path, "rb") as f:
                # 使用文件流上传，避免内存爆炸
                res = requests.post(
                    f"{self.api_url}/add",
                    files={"file": (os.path.basename(file_path), f)},
                    timeout=30
                )
            cid = res.json()["Hash"]
            return {"status": "success", "cid": cid}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def download_file(self, cid, save_path):
        """从IPFS下载文件到本地"""
        try:
            res = requests.post(
                f"{self.api_url}/cat?arg={cid}",
                stream=True,  # 启用流式下载
                timeout=30
            )
            with open(save_path, "wb") as f:
                for chunk in res.iter_content(chunk_size=8192):
                    f.write(chunk)
            return {"status": "success", "saved_to": save_path}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# 使用示例
if __name__ == "__main__":
    client = IPFSFileClient()
    
    # 测试上传
    upload_result = client.upload_file("./try1.py")
    if upload_result["status"] == "success":
        print(f"📤 上传成功 | CID: {upload_result['cid']}")
        
        # 测试下载
        download_result = client.download_file(
            upload_result["cid"],
            "./try1_downloaded.py"
        )
        if download_result["status"] == "success":
            print(f"📥 下载成功 | 保存路径: {download_result['saved_to']}")
        else:
            print(f"❌ 下载失败: {download_result['message']}")
    else:
        print(f"❌ 上传失败: {upload_result['message']}")
