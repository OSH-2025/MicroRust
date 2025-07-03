# 环境配置
1. 安装python3.11。
2. 安装IPFS服务，在管理员权限下运行`src/MR_IPFS/IPFS_install.py`即可；手动配置IPFS的可执行文件所在路径为环境变量，Windows默认在用户目录.ipfs_bin，Linux默认在目录/usr/local/bin。

# 项目运行
运行`src/main.py`便可通过回环地址`http://127.0.0.1:5000/`访问项目。由于并未获得公网域名，我们的项目仍需本地的`main.py`提供服务，但我们计划在后续通过服务器为不同用户提供网页服务。