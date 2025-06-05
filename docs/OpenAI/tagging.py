import os
import base64
import logging
from pydantic import BaseModel
from mimetypes import guess_type
from openai import AzureOpenAI
from mistralai import Mistral

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY_JPE"), #使用Japan East服务节点
        api_version="2024-12-01-preview",
        azure_endpoint = "https://"+os.getenv("AZURE_OPENAI_ENDPOINT_JPE")+".services.ai.azure.com/"
    )
except Exception as e:
    logger.error(f"Failed to initialize Azure OpenAI client: {e}")
    client = None

try:
    ocr_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
except Exception as e:
    logger.error(f"Failed to initialize Mistral client: {e}")
    ocr_client = None

# FileTag model to represent the tags
class FileTag(BaseModel):
    tags: list[str]

system_message = {
    "role": "system",
    "content": """
    The user will provide some text or images. Please output 4-7 tags for the text in JSON format. 
    """
}

# Function to encode a local image into data URL 
def local_image_to_data_url(file_path):
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Guess the MIME type of the image based on the file extension
        mime_type, _ = guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'  # Default MIME type if none is found

        # Read and encode the image file
        with open(file_path, "rb") as image_file:
            base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

        # Construct the data URL
        return f"data:{mime_type};base64,{base64_encoded_data}"
    except Exception as e:
        logger.error(f"Error encoding file {file_path}: {e}")
        raise

def pdf_to_text(file_path):
    try:
        if not ocr_client:
            raise RuntimeError("OCR client not initialized")
            
        # Extract text from PDF
        ocr_response = ocr_client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": local_image_to_data_url(file_path)
            },
            include_image_base64=False
        )

        text_content = "\n".join(page.markdown for page in ocr_response.pages)
        return text_content
    except Exception as e:
        logger.error(f"Error processing PDF {file_path}: {e}")
        return ""

def docx_to_text(file_path):
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

def raw_to_text(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        except UnicodeDecodeError:
            logger.error(f"Unable to decode file {file_path} with utf-8 or gbk encoding")
            return ""
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""

def image_to_tag(file_path):
    try:
        if not client:
            raise RuntimeError("OpenAI client not initialized")
            
        # Create message with the image
        messages = [
            system_message,
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

        # Get completion from OpenAI
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini", 
            messages=messages,
            response_format=FileTag
        )
        return response.choices[0].message.parsed.tags
    except Exception as e:
        logger.error(f"Error generating tags for image {file_path}: {e}")
        return []

def text_to_tag(text):
    try:
        if not client:
            raise RuntimeError("OpenAI client not initialized")
            
        if not text or not text.strip():
            logger.warning("Empty text provided for tagging")
            return []
            
        # Create message with the text
        messages = [
            system_message,
            {
                "role": "user",
                "content": text
            }
        ]

        # Get completion from OpenAI
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini", 
            messages=messages,
            response_format=FileTag
        )
        return response.choices[0].message.parsed.tags
    except Exception as e:
        logger.error(f"Error generating tags for text: {e}")
        return []

def pdf_to_tag(file_path):
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
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return []
            
        # Get MIME Type
        mime_type, _ = guess_type(file_path)
        
        if mime_type and mime_type.startswith('text/'):
            return text_to_tag(raw_to_text(file_path))
        elif mime_type == 'application/pdf':
            return pdf_to_tag(file_path)
        elif mime_type and mime_type.startswith('image/'):
            return image_to_tag(file_path)
        elif file_path.endswith('.docx'):
            return text_to_tag(docx_to_text(file_path))
        else:
            logger.warning(f"Unsupported file type: {file_path}")
            return []
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return []

if __name__ == "__main__":
    try:
        print("Processing lake.jpg:")
        tags1 = auto_to_tag("lake.jpg")
        print(f"Tags: {tags1}")
        
        print("\nProcessing handwritten.pdf:")
        tags2 = auto_to_tag("handwritten.pdf")
        print(f"Tags: {tags2}")
    except Exception as e:
        logger.error(f"Main execution error: {e}")