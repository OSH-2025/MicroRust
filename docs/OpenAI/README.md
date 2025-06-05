## 使用Azure OpenAI进行多模态打标

### 多模态的需求

由于我们的工作需要处理大量的图像和文本数据，因此需要一个能够同时处理这两种数据类型的模型。Azure OpenAI提供了多模态模型，可以同时处理图像和文本。

### 使用Azure OpenAI的多模态模型

前段时间我已经完成Azure OpenAI模型额度的申请，目前可以使用Azure `gpt-4o`和`gpt-4o-mini`模型进行多模态打标。

Azure OpenAI的Python接口包含在OpenAI库中，因此可以直接使用`pip install openai`安装。（参见[Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)）

### 初步实践多模态

使用`lake.jpg`作为示例图像，以下是一个简单的多模态打标示例。为了更好的准确性，使用Structured Output功能，确保JSON格式输出：

```python
from openai import AzureOpenAI
import os
import base64
from pydantic import BaseModel

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY_JPE"), #使用Japan East服务节点
    api_version="2024-10-21",
    azure_endpoint = "https://"+os.getenv("AZURE_OPENAI_ENDPOINT_JPE")+".services.ai.azure.com/"
)

# FileTag model to represent the tags
class FileTag(BaseModel):
    tags: list[str]

# Read and encode the image
with open("lake.jpg", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

# Create message with the image
messages = [
    {
        "role": "system",
        "content": """
        The user will provide some text or images. Please output 4-7 tags for the text in JSON format. 
        """
    },
    {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                }
            }
        ]
    }
]

# Get completion from OpenAI
response = client.beta.chat.completions.parse(
    model="gpt-4o-mini", 
    messages=messages,
    response_format=FileTag
)

print(response.choices[0].message.content)
```

输出结果（模型gpt-4o-mini）：

```
{"tags":["mountains","reflection","landscape","nature","snow","sky","serenity"]}
```

这是Azure OpenAI多模态打标的初步实践。

### 处理PDF文档类型

PDF文档目前不直接被Azure OpenAI API所接受，因此需要先将PDF转换为受接受的格式。

目前总共有以下几种思路：

1. 使用已有库将PDF转为图片再传入AI模型。缺点：开销大，成本高，识别不一定精准（PDF中的文字将变得非常模糊） 优点：实现较为简单
2. 使用Mistral OCR将PDF转化为文本和插图的组合。 缺点：使用两次AI解决问题，或许不够优雅 优点：精准度高，可以将文本和插图精准提取出来（包括手写体等）

我们按照思路2继续实现。

`ocr.py`为PDF文档OCR的示例，对相当模糊的手写体`handwritten.pdf`也能准确提取出大部分文本。

现在我们将两个程序结合起来，实现PDF文档的打标。为了处理方便，我们对PDF中含有的插图不做处理。（大部分PDF文档的核心内容应当是文本而不是插图）