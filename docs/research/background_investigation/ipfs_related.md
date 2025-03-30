# 关于 IPFS/Filecoin 技术原理和使用方法的调研
# IPFS 原理与架构

## IPFS 原理演示
<img width="400" alt="image" src="https://github.com/user-attachments/assets/799ee30a-02d9-4670-9724-69ef810cb79c" />



## IPFS 数据块结构
<img width="268" alt="image" src="https://github.com/user-attachments/assets/ea64acde-0842-4c1c-8655-895c2ff4e501" />



## 相关工具和资源

以下是一些有用的 IPFS 和 Filecoin 相关工具和资源链接：

- [IPFS 官方文档](https://docs.ipfs.tech/)
- [Filecoin 官方文档](https://filecoin.io/)
- [IPFS-FUSE](https://github.com/ipfs-shipyard/ipfs-fuse)
- [Pinata](https://www.pinata.cloud/)（IPFS 托管服务）
- [Lotus 客户端](https://lotus.filecoin.io/)（Filecoin 官方客户端）

## 一、初识 IPFS

IPFS 是 InterPlanetary File System 的缩写。它是一个分布式的网络传输协议，可以把文件分成很多小块放到服务器的不同地方，然后用一种特别的方式来寻找和传输这些小块。这样，我们就可以更快、更安全、更抗容错地存储文件了。

可能你会问，像腾讯云、阿里云这样的 OSS 文件存储系统，和这个有什么区别呢？

举个例子，当阿里云被攻击的时候，你的 OSS 还能访问吗？是不是不能？这就是中心化系统带来的弊端。还有当你在阿里云上传一张图片，你觉得你有所有权吗？人家管理员是不是也可以对你的图片为所欲为呢？这也是中心化的一大弊端。图片所有者权限少于系统管理者。

接下来重点说一下 IPFS 吧。

## 二、IPFS 原理

1. **分布式哈希表（DHT）**  
   IPFS 使用分布式哈希表来实现内容寻址。每个文件都由其内容的哈希值唯一标识。DHT 允许节点根据内容的哈希值快速定位文件，而不需要中心化的服务器。

2. **内容寻址**  
   IPFS 使用内容寻址来定位文件，而不是基于位置的寻址。这意味着文件的位置由其内容决定，而不是存储它的物理位置。只要文件内容不变，其地址就保持一致。

3. **点对点通信**  
   IPFS 节点通过点对点通信协议相互连接。节点可以请求文件、发布文件、转发请求等。这种点对点通信模型有助于提高网络的可扩展性和抗攻击性。

4. **内容缓存**  
   IPFS 节点可以缓存他们访问过的文件内容，以便在将来请求时更快地提供文件。这种缓存机制有助于减少重复传输和提高网络性能。

5. **数据块**  
   IPFS 将文件分割为数据块，并使用 Merkle DAG（有向无环图）来组织这些数据块。文件被分割成多个小块，每个块都有一个唯一的哈希值。这些块通过 Merkle DAG 连接起来，形成一个树状结构。这种结构不仅便于数据的快速检索和验证，还支持高效的版本控制和增量更新。例如，当文件发生局部修改时，只需要更新修改部分的块及其相关的哈希值，而无需重新计算整个文件的哈希。

6. **内容生产者和消费者**  
   IPFS 允许任何节点成为内容的生产者和消费者。节点可以发布自己的内容，并为其他节点提供访问。同时，节点也可以请求并检索其他节点发布的内容。

## 三、激励机制与 Filecoin

Filecoin 是建立在 IPFS 之上的激励层，它通过区块链技术为存储提供者和用户创建了一个去中心化的存储市场。在 Filecoin 网络中，存储提供者（矿工）通过提供存储空间和带宽来获取 Filecoin 代币作为奖励。用户则需要支付 Filecoin 代币来购买存储服务。

## 四、IPFS 的使用方法

### （一）安装 IPFS

1. 从 [IPFS 官方网站](https://docs.ipfs.tech/install/ipfs-desktop/#windows)下载并安装 IPFS 客户端。
2. 在终端运行 `ipfs init` 初始化 IPFS 节点，这会生成一个唯一的节点密钥。
3. 启动 IPFS 守护进程：`ipfs daemon`，这样你的电脑就加入了 IPFS 网络。

### （二）上传文件

1. 创建一个文件：`echo "测试内容" > test.txt`
2. 将文件添加到 IPFS：`ipfs add test.txt`，这会返回一个哈希值，这就是文件的地址。

### （三）查看文件

1. 使用 `ipfs cat <哈希值>` 查看文件内容。
2. 也可以通过浏览器访问 `http://127.0.0.1:8080/ipfs/<哈希值>` 来查看文件。

### （四）固定文件（Pin）

1. 使用 `ipfs pin add <哈希值>` 将文件固定到本地节点，这样即使其他节点离线，你也可以访问该文件。
2. 查看已固定的文件：`ipfs pin ls`。

### （五）使用 IPNS

1. IPNS（InterPlanetary Name System）是 IPFS 的命名系统，可以为文件创建一个易于记忆的名称。
2. 创建一个 IPNS 记录：`ipfs name publish <哈希值>`，然后可以通过这个名称访问文件。

## 五、让 IPFS 和本地文件系统结合

为了让 IPFS 和本地文件系统能够交互，需要使用 FUSE（Filesystem in Userspace）这个工具。简单来说，FUSE 就像是一个“翻译官”，它能把 IPFS 的分布式文件系统“翻译”成本地文件系统能理解的样子。
# IPFS文件上传和下载过程

在图中的项目中，IPFS文件上传和下载的过程可以通过以下步骤实现：

## 上传文件

1. 将IPFS的依赖引入到项目工程中，并进行配置。
2. 编写控制类，写出上传接口。例如，使用Java编写的控制类，通过`@Autowired`注解注入`IpfsService`服务，并编写`@PostMapping("/upload")`注解的方法来处理上传请求。
3. 实现上传方法，例如`uploadIpfs`方法，该方法接收一个`MultipartFile`对象，代表要上传的文件。
4. 使用`IPFS`客户端实例，调用`add`方法将文件添加到IPFS网络中，该方法会返回一个包含文件哈希值的`MerkleNode`对象。
5. 从`MerkleNode`对象中获取文件的CID（Content Identifier），这是文件在IPFS网络中的唯一标识符。
6. 将文件CID返回给用户，用户可以通过这个CID来访问或分享文件。

## 下载文件

1. 用户通过CID访问或分享文件时，可以使用`ipfs cat <CID>`命令来访问文件内容。
2. IPFS网络会通过CID找到存储该文件的节点，并直接从这些节点下载数据。
3. 如果安装了下载软件，也可以使用这些软件接管下载，例如使用FDM等。
4. 除了P2P下载方式，IPFS还可以采用公共网关创建分享链接的方式分享文件。公共网关本身也是一个IPFS节点，但拥有公网IP，连接速度较快，可以帮助其他节点下载。



用于在 Java 项目中引入 java-ipfs-http-client 库。这个库是一个 Java 客户端，允许开发者通过 HTTP 协议与 IPFS 节点进行交互。

详细说明
1. 依赖的作用
java-ipfs-http-client 是一个轻量级的 Java 库，封装了 IPFS 的 HTTP API。
使用该库，你可以通过 Java 程序调用 IPFS 的功能，例如：
添加文件到 IPFS。
获取文件内容。
列出目录。
执行其他 IPFS 操作（如 Pin、Unpin、版本控制等）。
2. Maven 依赖解析
以下是依赖配置的各部分含义：

xml
深色版本
<dependency>
    <groupId>com.github.ipfs</groupId> <!-- 组 ID，标识库的组织或作者 -->
    <artifactId>java-ipfs-http-client</artifactId> <!-- 库的名称 -->
    <version>1.3.3</version> <!-- 版本号 -->
</dependency>
groupId: com.github.ipfs 表示该库托管在 GitHub 上，并且由 IPFS 社区维护。
artifactId: java-ipfs-http-client 是库的名称，表示它是一个 Java 实现的 IPFS HTTP 客户端。
version: 1.3.3 是库的具体版本号，建议使用最新稳定版本以获得更好的兼容性和功能支持。
3. 如何使用
要使用这个库，你需要确保以下几点：

IPFS 节点运行：
在本地或远程运行一个 IPFS 节点（可以通过官方 IPFS 安装包启动）。
默认情况下，IPFS 的 HTTP API 监听地址为 http://localhost:5001。
添加依赖：
将上述 <dependency> 配置添加到你的 Maven 项目的 pom.xml 文件中。
示例代码：
下面是一个简单的示例代码，演示如何使用 java-ipfs-http-client 添加文件到 IPFS 并获取其哈希值：
java
深色版本
import io.ipfs.api.IPFS;
import io.ipfs.api.MerkleNode;
import io.ipfs.api.NamedStreamable;

import java.io.File;
import java.io.IOException;

public class IpfsExample {
    public static void main(String[] args) throws IOException {
        // 连接到本地 IPFS 节点
        IPFS ipfs = new IPFS("/ip4/127.0.0.1/tcp/5001");

        // 创建一个文件对象
        File file = new File("example.txt");

        // 将文件包装为 NamedStreamable 对象
        NamedStreamable.FileWrapper fileWrapper = new NamedStreamable.FileWrapper(file);

        // 将文件添加到 IPFS
        MerkleNode addResult = ipfs.add(fileWrapper).get(0);

        // 输出文件的哈希值
        System.out.println("File added to IPFS with hash: " + addResult.hash);
    }
}
4. 运行环境要求
Java 版本: 确保你的项目使用的是 Java 8 或更高版本。
IPFS 节点: 确保 IPFS 节点正在运行并监听 HTTP API 接口（默认端口是 5001）。
5. 常见问题
IPFS 节点未启动：如果 IPFS 节点没有运行，客户端会抛出连接错误。请确保 IPFS 节点已启动并可用。
网络问题：如果 IPFS 节点运行在远程服务器上，请确保防火墙允许访问 HTTP API 端口（默认 5001）。
版本兼容性：如果你使用的是较新版本的 IPFS 节点，请检查 java-ipfs-http-client 是否支持该版本的 API。
6. 更新依赖
如果你想使用最新版本的 java-ipfs-http-client，可以查看其 GitHub 仓库 或 Maven Central 页面，获取最新的版本号并更新 pom.xml 中的 <version> 字段。
