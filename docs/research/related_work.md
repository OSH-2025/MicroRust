# 相关工作
## 基于大语言模型的文件系统

### AIOS
AIOS 是人工智能代理操作系统，它将大型语言模型 (LLM) 嵌入到操作系统中，并促进基于 LLM 的人工智能代理的开发和部署。AIOS 旨在解决基于 LLM 的代理在开发和部署过程中遇到的问题（例如调度、上下文切换、内存管理、存储管理、工具管理、代理 SDK 管理等），从而为代理开发人员和代理用户提供更好的 AIOS-Agent 生态系统。[ref]
AIOS 系统由两个关键组件组成：AIOS 内核和 AIOS SDK。AIOS 内核充当操作系统内核的抽象层，管理代理所需的各种资源，例如 LLM、内存、存储和工具。AIOS SDK 专为代理用户和开发人员设计，使他们能够通过与 AIOS 内核交互来构建和运行代理应用程序。[ref]
### ArkFS
ArkFS 是受 AIOS 项目启发的人工智能文件系统，将大模型嵌入到文件系统中，利用大模型理解用户的文本语义，实现文件增删改查等操作。该文件系统利用大模型理解用户需求，形成文件操作的任务队列，无需人工干预。大模型部署在本地，学习本地文件，实现向量化检索。[ref]
## 分布式存储系统
1. HDFS（Hadoop Distributed File System）：用于Hadoop生态系统，适合大数据处理。
2. NFS（Network File System）：传统分布式文件系统，基于客户端-服务器模型。
3. GFS（Google File System）：Google开发的私有系统，启发了HDFS。
4. Ceph：开源分布式存储系统，支持文件、块和对象存储。
5. GlusterFS：开源分布式文件系统，易于扩展。
6. My-Glow（Graph File System，23年科大OSH项目）：一个带有图结构的、高鲁棒性的、体验优秀的分布式文件系统。
### IPFS

### Ceph

### HDFS

### Stratos

## 图文件系统

### GFS2

### GraphFS
