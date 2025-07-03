# 文件与路径操作
import os

# 编码与解码处理
import base64

# 日志记录
import logging

# MIME类型识别
from mimetypes import guess_type

# 配置日志
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

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


# 将图片文件编码为base64格式
def image_to_base64(file_path):
    """
    将图片文件编码为base64格式
    
    参数:
        file_path(str): 图片文件路径
    
    返回:
        str: base64编码的data URL
    
    异常:
        FileNotFoundError: 文件不存在
    
    使用示例:
        base64 = image_to_base64("image.jpg")
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
            base64_encoded_data = str(base64.b64encode(image_file.read()), "utf-8")
        
        # 生成data URL
        return base64_encoded_data
    
    except Exception as e:
        logger.error(f"Error encoding file {file_path}: {e}")
        raise

# 将图片文件编码为data URL格式
def image_to_data_url(file_path):
    """
    将图片文件编码为data URL格式
    
    参数:
        file_path(str): 图片文件路径
    
    返回:
        str: base64编码的data URL
    
    异常:
        FileNotFoundError: 文件不存在
    
    使用示例:
        data_url = image_to_data_url("image.jpg")
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