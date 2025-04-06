# 可行性报告（ArkFS）

## 目录
[TOC]
## 需求分析
改写ArkFS以实现AI打标服务和CID-标签的存储和索引。
## 技术可行性
### AI打标服务
通过调用大模型API，实现对图片、文本和音频的标记服务，可通过调用python的`openai`库实现。
以下为ArkFS中的一个代码片段，展示如何使用`openai`库进行用户命令解析：
```python
from openai import OpenAI
client = OpenAI(   # 此处以Google Gemini API为例
    api_key="Replace with your Google Gemini API Key",
    base_url="https://gemini-api.google.com/v1"  
)
completion = client.generate_response(
	model='gemini-model-v1',
	messages=[
		{
			"role": "user",
			"content": (
				f'"{prompt}",对于这句话请提取他的“时间(昨天、前天或其他)”“文件类型(仅包含image或者txt)”“有关文件内容的一个名词(阳光、草地或人名等其他名词，翻译成英文)”，如果有缺失的信息，用NULL表示。现在你有“增、删、改、查”四种文件功能(对于任务调度你只能返回“增、删、改、查”这四个字的组合作为任务序列)，请你给出这句话对应的任务调度序列，如“增删”这样的序列（请注意在增一个文件时，如果不是增空文件夹，那么需要先查再增），如果不涉及具体动作，只查即可，但如果有“移动”“转移”“放置”之类的要求，你就需要添加增删改查的其他功能。按照顺序，以[[时间],[文件类型],[内容名词],[调度序列]]的格式返回给我。'
			)
		}
	]
)
```
### 实现CID-标签索引存储数据库
从IPFS节点集群同步文件和CID，对新的文件进行打标，再将CID-标签存入独立数据库。
```python
import ipfshttpclient
import MySQLdb
client = ipfshttpclient.connect('ipfs-host') # 连接到IPFS节点
db = MySQLdb.connect("localhost", user_name, user_password, database_name, charset='utf8' ) # 连接到MySQL数据库
# 存储文件至ipfs，返回文件的CID
def store_file(file_path):
	res = client.add(file_path)
	cid = res['Hash']
	return cid

# 与ipfs数据库进行同步，对未打标的文件进行打标并存入本地数据库
def sync_ipfs():
	# 获取IPFS节点上的所有文件
	files = client.ls()
	for file in files:
		cid = file['Hash']
		# 检查CID是否已存在于本地数据库
		cursor = db.cursor()
		cursor.execute("SELECT * FROM cid_table WHERE cid = %s", (cid,))
		if cursor.fetchone() is None:
			# 对文件进行打标
			label = mark_file(file)
			# 将CID和标签存入本地数据库
			cursor.execute("INSERT INTO cid_table (cid, label) VALUES (%s, %s)", (cid, label))
			db.commit()

# 从IPFS节点获取文件CID
def get_file(cid):
	res = client.cat(cid)
	return res

# 从CID获取标签
def get_label(cid):
	cursor = db.cursor()
	cursor.execute("SELECT label FROM cid_table WHERE cid = %s", (cid,))
	label = cursor.fetchone()
	return label
```
