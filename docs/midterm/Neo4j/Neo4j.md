# Neo4j运行
Neo4j具有三种主流的运行方式，分别是通过Neo4j源代码、Neo4j Aura和Neo4j Desktop。

## Neo4j源代码
我们可以通过下载Neo4j源代码，在本地电脑配置Neo4j的运行环境。
1. 目前，Neo4j已更新到了5.26.5版本，可以在[Neo4j官网](https://neo4j.com/deployment-center)下载Neo4j源代码的`neo4j-community-5.26.5-unix.tar.gz`压缩包，将其解压到工作目录。
2. 进入`neo4j-community-5.26.5`目录后，通过`bin/neo4j console`开发测试，通过`bin/neo4j start`在后台运行，通过`bin/neo4j stop`结束运行。
3. 通过浏览器可以在网址`http://localhost:7474`访问Neo4j的默认端口。
4. 可以在浏览器利用Cypher语言进行数据查询的测试。
5. 通过修改配置文件`conf/neo4j.conf`实现个性化需求，Neo4j源代码关键目录结构如下。
```
neo4j-community-5.26.5
├───bin                 启动脚本，如 neo4j
├───conf/neo4j.conf     配置文件，常改端口、地址、认证等    
├───data                存储数据库数据
├───logs                日志输出
├───import              可用于导入 CSV 数据
├───plugins             插件目录（如 APOC 插件）
└licenses               许可说明
```

## Neo4j Aura
Neo4j Aura是Neo4j提供的一个云端完全托管的图数据库服务，可以帮助我们在云端快速创建、管理和扩展图数据库，同时集成了图形数据建模、查询、分析功能。Neo4j Aura可以通过JavaScript被Web应用进行调用和交互，非常适合构建基于图数据库的前后端应用。关于JavaScript的使用方法我还没有完成学习。

## Neo4j Desktop
Neo4j Desktop是Neo4j的图形化客户端工具。

# Neo4j使用
我建议在一台电脑上下载Neo4j源代码，并在本地编写Neo4j配置文件以满足我们的个性化需求。之后，我们可以将配置文件导入到Neo4j Aura中以创建一个云端图数据库，用于我们分布式系统的图数据库。如此，一方面，无需在本地配置Neo4j运行环境便可使用我们项目的Web服务，提高易用性；另一方面，我们可以使用Neo4j Aura自带的监测功能。
我认为Neo4j Desktop与我们的项目无关。