关于ragflow的使用与他是什么

1.ragflow本身是类似于一个中介的，它是一个现有的可以结合api进行知识图谱搜寻的应用

2.他可以先通过向量数据库（如 Milvus、Weaviate）检索相关文档片段，再交给大模型生成答案，提升回答的准确性和可解释性。

3.支持多种文件格式（PDF、Word、Excel 等）的解析和向量化。

提供预构建的 API 和 Web 界面，无需从零开发。

4.ragflow提供现成的接口，直接链接到api

更加简单的来说：他就是一个搭好的平台，它自己可以解析文本内容和图片内容，然后将片段与文件以及问题发送给大模型，你告诉它用什么模型，他用什么大模型回答

1. **用户上传文件**
   → RAGFlow 用 **本地解析器** 提取文本。
2. **文本切片+向量化**
   → 存入向量数据库（如 Milvus）。
3. **用户提问**
   → 检索相关文档片段 → **发送片段+问题** 给大模型生成答案。

具体的话是要本地搭建一个ragflow知识库，并连接外部的api

我尝试搭建了ragflow，但是出现了网络端口问题，目前我成功拉取了ragflow并配置了相应环境，并开放了端口，但访问时始终显示404

![image-20250503112238087](C:\Users\hyyx1\AppData\Roaming\Typora\typora-user-images\image-20250503112238087.png)

但是我仍然推荐本地部署，因为云端部署可能需要申请api，很麻烦

配置大致顺序

1.WSL环境配置

2.dockerdesktop下载与环境配置

3.ragflow拉取

4.本地进入并配置大模型

大致的顺序可以按我下面这个教程，但是它是本地配置的大模型，我绝对不建议那么做，除非我们中有人有一张16gb（市面上至少10000+）（至少8gb）的显卡，或是有人明确会擅长使用gpu服务器的连接，我尝试部署过6g的chatglm-6b，他是13g的chatglm的缩小版，它的性能大致只能比上chatgpt-3，远远不如api连接

[DeepSeek+RAGflow纯本地化知识库搭建全教程作者在搭建私有知识库部署ragflow过程中踩了很多坑，在此分享 - 掘金](https://juejin.cn/post/7475973902657814539)

我需要另一个人进行尝试，如果实在搭载不起来我们看看有没有别的不那么涉及网络的类似应用