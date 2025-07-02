具体如何搭建：IPFS系统

```
# 安装依赖
sudo apt update && sudo apt install -y wget

# 下载并安装IPFS
wget https://dist.ipfs.tech/kubo/v0.23.0/kubo_v0.23.0_linux-amd64.tar.gz
tar -xvzf kubo_v0.23.0_linux-amd64.tar.gz
cd kubo
sudo ./install.sh

# 初始化
ipfs init --profile server
```

安装go环境

```
wget https://go.dev/dl/go1.22.4.linux-amd64.tar.gz
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.22.4.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc

# 验证安装
go version

##这后面你们可以不用做，这是具体生成了ipfs节点，进行测试时创建也可以
 go env -w GOPROXY=https://goproxy.cn,direct
  go install github.com/Kubuxu/go-ipfs-swarm-key-gen/ipfs-swarm-key-gen@latest
 chmod +x go/bin/ipfs-swarm-key-gen
 chmod +x go/bin/ipfs-swarm-key-gen
 sudo mv go/bin/ipfs-swarm-key-gen /usr/local/bin/#加权限并移动到合适的位置
 
```

[](/key/swarm/psk/1.0.0/
/base16/
592e83bfe64083bb4dd3063c2c12fc86db1fb7ccaf12481325bab0c8e16651[d4)//这是swarm-key的形式



```
sudo apt install net-tools#网络工具
ifconfig | grep "inet 192.168"#查看自己的局域网ip
inet 192.168.220.128  netmask 255.255.255.0  broadcast 192.168.220.255#这样的返回是正常的
你的局域网ip为192.168.220.128
# 开放API端口
ipfs config Addresses.API "/ip4/0.0.0.0/tcp/5001"

# 禁用安全限制（仅测试环境用）
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Origin '["*"]'
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Methods '["PUT", "GET", "POST"]'
ipfs daemon
```

在测试前注意在主机上先尝试和虚拟机上网络是否正常互通

```
ping 192.168.220.128#这里改为自己的虚拟机局域网ip
正在 Ping 192.168.220.128 具有 32 字节的数据:
来自 192.168.220.128 的回复: 字节=32 时间<1ms TTL=64
来自 192.168.220.128 的回复: 字节=32 时间<1ms TTL=64
来自 192.168.220.128 的回复: 字节=32 时间<1ms TTL=64
来自 192.168.220.128 的回复: 字节=32 时间<1ms TTL=64

    数据包: 已发送 = 4，已接收 = 4，丢失 = 0 (0% 丢失)，
往返行程的估计时间(以毫秒为单位):
    最短 = 0ms，最长 = 0ms，平均 = 0ms
```
注意：	ERROR	cmd/ipfs	ipfs/daemon.go:614	failed to bootstrap (no peers found): consider updating Bootstrap or Peering section of your config是没有关系的，
但另一个ERROR	cmd/ipfs	ipfs/daemon.go:408	Private networking (swarm.key / LIBP2P_FORCE_PNET) does not work with public HTTP IPNIs enabled by Routing.Type=auto. Kubo will use Routing.Type=dht instead. Update config to remove this message.需要处理，具体方式为：
`ipfs config Routing.Type dht`
重启ipfs
```
killall ipfs
ipfs daemon
```


