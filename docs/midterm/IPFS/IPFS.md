### 1. 安装 `ipfshttpclient` 库
可以通过以下命令安装：
```bash
pip install ipfshttpclient
```

### 2. 启动 IPFS 守护进程
通过以下命令启动：
```bash
ipfs daemon
```

### 3. Python 示例代码

#### 3.1 上传文件到 IPFS
以下代码展示了如何将本地文件上传到 IPFS，并获取其 CID（内容标识符）。
```python
import ipfshttpclient

# 连接到本地 IPFS 守护进程
client = ipfshttpclient.connect()

# 上传文件到 IPFS
def upload_file(file_path):
    try:
        # 添加文件到 IPFS
        result = client.add(file_path)
        print(f"File uploaded successfully! CID: {result['Hash']}")
        return result['Hash']
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

# 示例：上传文件
file_path = "example.txt"
cid = upload_file(file_path)
```

#### 3.2 下载文件从 IPFS
以下代码展示了如何通过 CID 从 IPFS 下载文件。
```python
import ipfshttpclient

# 连接到本地 IPFS 守护进程
client = ipfshttpclient.connect()

# 下载文件从 IPFS
def download_file(cid, output_path):
    try:
        # 从 IPFS 下载文件
        client.get(cid, target=output_path)
        print(f"File downloaded successfully to {output_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")

# 示例：下载文件
cid = "QmSomeCID"  # 替换为实际的 CID
output_path = "downloaded_file.txt"
download_file(cid, output_path)
```

#### 3.3 获取文件信息
以下代码展示了如何通过 CID 获取文件的详细信息。
```python
import ipfshttpclient

# 连接到本地 IPFS 守护进程
client = ipfshttpclient.connect()

# 获取文件信息
def get_file_info(cid):
    try:
        # 获取文件信息
        info = client.object.stat(cid)
        print(f"File info: {info}")
        return info
    except Exception as e:
        print(f"Error getting file info: {e}")
        return None

# 示例：获取文件信息
cid = "QmSomeCID"  # 替换为实际的 CID
file_info = get_file_info(cid)
```

参考网页：https://www.cnblogs.com/yoyo1216/p/13489699.html
https://github.com/ipfs-shipyard/py-ipfs-http-client
