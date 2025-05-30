# 文件系统
**定义**：文件系统是操作系统用于明确磁盘或分区上的文件的方法和数据结构，是在磁盘上组织文件的方法，是操作系统中负责管理和存储文件信息的软件机构。它由三部分组成：与文件管理有关的软件、被管理的文件以及实施文件管理所需要的数据结构。从系统角度来看，文件系统是对文件存储器空间进行组织和分配，负责文件的存储并对存入的文件进行保护和检索的系统。具体地说，它负责为用户建立文件，存入、读出，修改、转储文件，控制文件的存取，当用户不再使用时撤销文件等。
## 核心功能
- **文件管理**：给文件命名、分配存储空间、记录文件位置。
- **目录结构**：通过文件夹（目录）组织文件，通常是树形结构，近年来为了适应不断膨胀的数据规模，也出现了应用于分布式系统上的图形文件结构。
- **权限控制**：决定哪些用户可以读、写或执行文件。
- **数据存取**：提供快速访问文件内容的方式。
- **空间管理**：追踪存储设备的可用空间和已用空间。
## 工作原理
- **分区**：存储设备通常会被分成多个分区，每个分区可以有自己的文件系统。
- **元数据**：文件系统用元数据（如文件名、大小、创建时间）来描述文件，存储在特定的表格中（例如FAT表的“文件分配表”或NTFS的“主文件表”）。
- **数据块**：文件内容被分成小块存储在磁盘上，文件系统负责追踪这些块的位置。
- **索引**：通过目录和索引，快速定位文件。
## 分布式文件系统
**定义**:分布式文件系统（Distributed File System, DFS）是一种允许多个计算机通过网络共享和管理文件的文件系统。它将文件存储在多个物理位置（节点或服务器）上，但对用户来说，看起来像是在访问一个统一的本地文件系统。分布式文件系统的核心目标是高可用性、可扩展性和容错性，广泛应用于云计算、大数据处理和分布式计算领域。
### 主要结构
![HDFS分布式系统图示](pics/HDFS_Structure.png)
- **客户端（Client）**：用户通过客户端访问文件，客户端负责与系统通信。
- **元数据服务器（Metadata Server）**：存储文件的元数据（如文件名、位置、权限），也叫“名字节点”（NameNode）。
- **数据服务器（Data Server）**：存储文件内容的实际节点，也叫“数据节点”（DataNode）。
- **网络协议**：用于客户端与服务器、服务器之间的通信（如TCP/IP、HTTP、IPFS/filecoin）。
### 核心目标
- **分散存储**：文件数据分布在多个节点上，而不是集中在一个设备。
- **统一命名空间**：用户通过一个全局路径访问文件，无需关心具体存储位置。
- **数据复制**：文件通常有多个副本，存储在不同节点，以提高可靠性和容错性。
- **负载均衡**：通过分散读写请求，提升性能。
### 主流类型
- **集中式元数据架构（Master-Slave结构）**：该架构使用一个或多个专门的元数据服务器（Master）来管理文件的元数据，而数据存储在多个数据节点（Slave）上。代表性系统有HDFS和JuiceFS
- **对等结构（P2P结构）**：该架构没有单一的中心元数据服务器，所有节点既存储数据也管理元数据。代表性系统有IPFS，也是我们项目计划采用的分布式文件系统。
- **对象存储架构**：该架构的对象存储系统通常基于分布式存储架构，使用唯一的ID而不是传统的文件路径来访问数据。
- **共享存储架构（NAS结构）**：该架构的多个服务器共享同一存储设备，通常通过网络文件协议进行访问。