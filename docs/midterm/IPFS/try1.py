import requests

class IPFSClient:
    def __init__(self, node_ip="192.168.220.128", port=5001):
        self.api_url = f"http://{node_ip}:{port}/api/v0"
        
    def add_text(self, text):
        """上传文本到IPFS"""
        res = requests.post(f"{self.api_url}/add", files={"file": ("test.txt", text)})
        return res.json()["Hash"]
    
    def get_text(self, cid):
        """从IPFS下载文本"""
        res = requests.post(f"{self.api_url}/cat?arg={cid}")
        return res.text
    
    def check_connection(self):
        """检查与节点的连接"""
        try:
            res = requests.post(f"{self.api_url}/id", timeout=5)
            return f"✅ 已连接到节点 | PeerID: {res.json()['ID']}"
        except Exception as e:
            return f"❌ 连接失败: {str(e)}"

# 使用示例
if __name__ == "__main__":
    client = IPFSClient()
    
    # 测试连接
    print(client.check_connection())
    
    # 测试上传/下载
    cid = client.add_text("Hello from 纯客户端!")
    print(f"📤 上传成功 | CID: {cid}")
    
    text = client.get_text(cid)
    print(f"📥 下载内容: {text}")