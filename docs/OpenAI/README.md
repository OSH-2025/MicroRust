## 使用Azure OpenAI进行多模态打标

### 多模态的需求

由于我们的工作需要处理大量的图像和文本数据，因此需要一个能够同时处理这两种数据类型的模型。Azure OpenAI提供了多模态模型，可以同时处理图像和文本。

### 使用Azure OpenAI的多模态模型

前段时间我已经完成Azure OpenAI模型额度的申请，目前可以使用A`gpt-4o`和`gpt-4o-mini`模型进行多模态打标。

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