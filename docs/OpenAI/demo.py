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