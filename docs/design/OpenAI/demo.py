from openai import AzureOpenAI
import os
import base64
from pydantic import BaseModel
from mimetypes import guess_type

# Function to encode a local image into data URL 
def local_image_to_data_url(image_path):
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY_JPE"), #使用Japan East服务节点
    api_version="2024-12-01-preview",
    azure_endpoint = "https://"+os.getenv("AZURE_OPENAI_ENDPOINT_JPE")+".services.ai.azure.com/"
)

# FileTag model to represent the tags
class FileTag(BaseModel):
    tags: list[str]

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
                    "url": local_image_to_data_url("lake.jpg")
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