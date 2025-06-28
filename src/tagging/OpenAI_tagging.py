"""
AI模块 - 基于Azure OpenAI和Mistral的文件标签生成器

主要功能：
1. 自动为各种文件类型生成标签(文本、图片、PDF、DOCX等)
2. 提供AI聊天功能
3. 支持多种文件格式的文本提取和OCR

使用前需要设置环境变量：
- AZURE_OPENAI_API_KEY_JPE: Azure OpenAI API密钥
- AZURE_OPENAI_ENDPOINT_JPE: Azure OpenAI服务端点
- MISTRAL_API_KEY: Mistral API密钥

示例用法：
    # 自动为文件生成标签
    tags = auto_to_tag("example.pdf")
    
    # 为文本生成标签
    tags = text_to_tag("这是一段示例文本")
    
    # 为图片生成标签
    tags = image_to_tag("example.jpg")
    
    # AI聊天
    response = chat_message([{"role": "user", "content": "你好"}])
"""

import os
import base64
import logging
from pydantic import BaseModel
from mimetypes import guess_type
from openai import AzureOpenAI
from mistralai import Mistral

# 配置日志
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

# 启动Azure OpenAI客户端
try:
    AzureOpenAI_client = AzureOpenAI(
        api_key = os.getenv("AZURE_OPENAI_API_KEY_JPE"), # 使用Japan East服务节点
        api_version = "2024-12-01-preview",
        azure_endpoint = "https://"+os.getenv("AZURE_OPENAI_ENDPOINT_JPE")+".services.ai.azure.com/"
    )

except Exception as e:
    logger.error(f"Failed to initialize Azure OpenAI client: {e}")
    AzureOpenAI_client = None

# 启动Mistral客户端
try:
    Mistral_client = Mistral(
        api_key=os.getenv("MISTRAL_API_KEY")
    )

except Exception as e:
    logger.error(f"Failed to initialize Mistral client: {e}")
    Mistral_client = None

# Azure OpenAI的系统message
SYSTEM_MESSAGE = {
    "role": "system",
    "content": """
    The user will provide some text or images. Please output 4-7 tags for the text in JSON format. 
    """
}

# 用于记录标签数据
class FileTag(BaseModel):
    """
    文件标签模型
    用于定义AI返回的标签格式
    """

    tags: list[str]

# 从纯文本文件中提取文本
def raw_to_text(file_path):
    """
    读取纯文本文件内容
    支持UTF-8和GBK编码
    
    参数:
        file_path (str): 文本文件路径
    
    返回:
        str: 文件内容
    
    使用示例:
        text = raw_to_text("document.txt")
        print(text)
    """

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 尝试使用utf-8编码
        with open(file_path, "r", encoding = "utf-8") as f:
            return f.read()
    
    except UnicodeDecodeError:
        try:
            # 尝试使用gbk编码
            with open(file_path, "r", encoding = "gbk") as f:
                return f.read()
        
        except UnicodeDecodeError:
            logger.error(f"Unable to decode file {file_path} with utf-8 or gbk encoding")
            return ""
    
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""

# 从DOCX中提取文本
def docx_to_text(file_path):
    """
    从DOCX文件中提取文本内容
    
    参数:
        file_path (str): DOCX文件路径
    
    返回:
        str: 提取的文本内容
    
    注意:
        需要安装python-docx库: pip install python-docx
    
    使用示例:
        text = docx_to_text("document.docx")
        print(text)
    """

    try:
        from docx import Document
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        doc = Document(file_path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    
    except ImportError:
        logger.error("python-docx library not installed. Install with: pip install python-docx")
        return ""
    
    except Exception as e:
        logger.error(f"Error processing DOCX {file_path}: {e}")
        return ""

# 为文本内容生成标签
def text_to_tag(text):
    """
    使用Azure OpenAI为文本内容生成标签
    
    参数:
        text(str): 需要生成标签的文本内容
        
    返回:
        list[str]: 生成的标签列表(4-7个标签)
        
    使用示例:
        text = "这是一篇关于机器学习的技术文章"
        tags = text_to_tag(text)
        print(tags)  # ["机器学习", "技术", "人工智能", "算法"]
    """

    try:
        if not AzureOpenAI_client:
            raise RuntimeError("OpenAI client not initialized")
            
        if not text or not text.strip():
            logger.warning("Empty text provided for tagging")
            return []
            
        # 创建一个包含文本内容信息的message
        messages = [
            SYSTEM_MESSAGE,
            {
                "role": "user",
                "content": text
            }
        ]

        # 获取响应结果response
        response = AzureOpenAI_client.beta.chat.completions.parse(
            model="gpt-4o-mini", 
            messages=messages,
            response_format=FileTag
        )
        return response.choices[0].message.parsed.tags
    
    except Exception as e:
        logger.error(f"Error generating tags for text: {e}")
        return []

# 将本地图片文件编码为data URL格式
def local_image_to_data_url(file_path):
    """
    将本地图片文件编码为data URL格式
    
    参数:
        file_path (str): 图片文件路径
    
    返回:
        str: base64编码的data URL
    
    异常:
        FileNotFoundError: 文件不存在
    
    使用示例:
        data_url = local_image_to_data_url("image.jpg")
    """

    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 根据文件扩展名猜测图片的MIME类型
        (mime_type, _) = guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"  # 使用默认的MIME类型
        
        # 读取并编码图片文件
        with open(file_path, "rb") as image_file:
            base64_encoded_data = base64.b64encode(image_file.read()).decode("utf-8")
        
        # 生成data URL
        return f"data:{mime_type};base64,{base64_encoded_data}"
    
    except Exception as e:
        logger.error(f"Error encoding file {file_path}: {e}")
        raise

# 为图片生成标签
def image_to_tag(file_path):
    """
    使用Azure OpenAI的视觉模型为图片生成标签
    
    参数:
        file_path (str): 图片文件路径
        
    返回:
        list[str]: 生成的标签列表（4-7个标签）
        
    使用示例:
        tags = image_to_tag("photo.jpg")
        print(tags)  # ["风景", "山脉", "日落", "自然", "户外"]
    """

    try:
        if not AzureOpenAI_client:
            raise RuntimeError("OpenAI client not initialized")
        
        # 创建一个包含图片信息的message
        messages = [
            SYSTEM_MESSAGE,
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": local_image_to_data_url(file_path)
                        }
                    }
                ]
            }
        ]

        # 获取响应结果response
        response = AzureOpenAI_client.beta.chat.completions.parse(
            model = "gpt-4o-mini", 
            messages = messages,
            response_format = FileTag
        )
        return response.choices[0].message.parsed.tags
    
    except Exception as e:
        logger.error(f"Error generating tags for image {file_path}: {e}")
        return []





# 从PDF文件中提取文本
def pdf_to_text(file_path):
    return ""
# def pdf_to_text(file_path):
#     """
#     使用Mistral的OCR模块从PDF文件中提取文本
    
#     参数:
#         file_path (str): PDF文件路径
        
#     返回:
#         str: 提取的文本内容
        
#     使用示例:
#         text = pdf_to_text("document.pdf")
#         print(text)
#     """

#     try:
#         # 检查Mistral是否可用
#         if not Mistral_client:
#             raise RuntimeError("Mistral client not initialized")
            
#         # Extract text from PDF
#         ocr_response = Mistral_client.ocr.process(
#             model="mistral-ocr-latest",
#             document={
#                 "type": "document_url",
#                 "document_url": local_image_to_data_url(file_path)
#             },
#             include_image_base64=False
#         )

#         text_content = "\n".join(page.markdown for page in ocr_response.pages)
#         return text_content
    
#     except Exception as e:
#         logger.error(f"Error processing PDF {file_path}: {e}")
#         return ""



def pdf_to_tag(file_path):
    """
    为PDF文件生成标签
    先使用OCR提取文本，再生成标签
    
    参数:
        file_path (str): PDF文件路径
        
    返回:
        list[str]: 生成的标签列表
        
    使用示例:
        tags = pdf_to_tag("research_paper.pdf")
        print(tags)
    """
    try:
        # Do document OCR
        extracted_text = pdf_to_text(file_path)
        if not extracted_text:
            logger.warning(f"No text extracted from PDF {file_path}")
            return []
        return text_to_tag(extracted_text)
    except Exception as e:
        logger.error(f"Error processing PDF to tags {file_path}: {e}")
        return []

def auto_to_tag(file_path):
    """
    自动检测文件类型并生成标签
    支持的文件类型：
    - 文本文件(.txt, .md, .py, 等)
    - Word文档(.docx)
    - 图片文件( .png, .jpg, .jpeg, 等)
    - PDF文件(.pdf)
    
    参数:
        file_path(str): 文件路径
        
    返回:
        list[str]: 生成的标签列表
        
    使用示例:
        # 自动处理不同类型的文件
        tags1 = auto_to_tag("text.txt")
        tags2 = auto_to_tag("document.docx")
        tags3 = auto_to_tag("image.jpg")
        tags4 = auto_to_tag("document.pdf")
    """

    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return []
        
        # 猜测文件类型
        mime_type, _ = guess_type(file_path)
        
        if mime_type and mime_type.startswith("text/"):
            return text_to_tag(raw_to_text(file_path))
        
        elif file_path.endswith(".docx"):
            return text_to_tag(docx_to_text(file_path))
        
        elif mime_type and mime_type.startswith("image/"):
            return image_to_tag(file_path)
        
        elif mime_type == "application/pdf":
            return pdf_to_tag(file_path)
        
        else:
            logger.warning(f"Unsupported file type: {file_path}")
            return text_to_tag(file_path)
    
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return []

# 与AI进行对话
def chat_message(messages):
    """
    与Azure OpenAI进行对话
    
    参数:
        messages (list): 消息列表，格式为OpenAI API标准格式
                       [{"role": "user", "content": "消息内容"}]
    
    返回:
        str: AI的回复内容
    
    使用示例:
        messages = [
            {"role": "system", "content": "你是一个有用的助手"},
            {"role": "user", "content": "你好，请介绍一下Python"}
        ]
        response = chat_message(messages)
        print(response)
        
        # 简单对话
        response = chat_message([{"role": "user", "content": "今天天气怎么样？"}])
    """

    try:
        if not AzureOpenAI_client:
            raise RuntimeError("OpenAI client not initialized")
        
        # 获取响应结果response
        response = AzureOpenAI_client.beta.chat.completions.parse(
            model="gpt-4o-mini", 
            messages=messages
        )
        return response.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Error during AI query: {e}")
        return ""