# 下载并初始化IPFS节点（以Linux平台为例）
```shell
# 安装下载工具wget
sudo apt update && sudo apt install -y wget

# 下载并安装IPFS
wget https://dist.ipfs.tech/kubo/v0.23.0/kubo_v0.23.0_linux-amd64.tar.gz
tar -xvzf kubo_v0.23.0_linux-amd64.tar.gz
cd kubo
sudo ./install.sh

# 初始化
ipfs init --profile server

# 启动
ipfs daemon
```

# IPFS节点的关键信息
`ipfs id`命令用于查看本地IPFS节点的关键信息, 其示例输出如下所示. 其中, `ID`表示该节点的唯一Peer ID, 是节点在IPFS网络中的身份标识; `Addresses`列出了该节点在网络上的接入地址, 即其他IPFS节点访问本地节点所使用的地址. IPFS的接入地址在不同IPFS的网络通信中起着重要作用, 由于这些地址一般有多个, 在后文中我们称这些地址为IPFS节点的multiaddr.
```shell
{
    "ID": "12D3KooW...",                # Peer ID生成
    "PublicKey": "...",                 # 节点的公钥
    "Addresses": [                      # 节点的multiaddr列表
        ...
    ],
    "AgentVersion": "kubo/0.23.0/",     # 节点运行的软件版本
    "Protocols": [                      # 节点支持的传输协议列表
        ...
    ]
}
```

# 连接IPFS节点
`ipfs swarm connect <multiaddr>`用于连接本地IPFS节点与multiaddr指向的IPFS节点, 该命令使得本地的IPFS节点能够下载multiaddr指向的IPFS节点所上传的文件.

# IPFS节点的文件上传和下载
在IPFS节点彼此相连后, 我们可通过下述命令向IPFS网络中上传和下载命令.
```shell
ipfs add <file>	        # 添加文件到IPFS, 并返回CID
ipfs cat <CID>	        # 查看CID对应的文本文件内容
ipfs get <CID>	        # 下载CID对应的文件
ipfs pin add <CID>	    # 将CID对应的文件固定在本地, 防止被自动删除
ipfs pin rm <CID>       # 解除CID对应的文件在本地的固定.
ipfs pin ls	            # 查看本地固定的CID文件
```

# IPFS节点的关闭
`ipfs shutdown`用于关闭正在运行的ipfs节点