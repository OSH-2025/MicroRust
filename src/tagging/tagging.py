# 文件与路径操作
import os

# 日志记录
import logging

# MIME类型识别
from mimetypes import guess_type

# 配置日志
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

def file_to_tag(file_path) -> list[str]:
    """
    自动检测文件类型并生成标签
    支持的文件类型：
    - 文本文件(.txt, .md, .py, 等)
    - Word文档(.docx)
    - 图片文件(.png, .jpg, .jpeg, 等)
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
        (mime_type, _) = guess_type(file_path)
        
        if mime_type and mime_type.startswith("text/"):
            return get_tags_from_text(raw_to_text(file_path))
        
        elif file_path.endswith(".docx"):
            return get_tags_from_text(docx_to_text(file_path))
        
        elif mime_type and mime_type.startswith("image/"):
            return get_tags_from_data_url(image_to_base64(file_path))
        
        # elif mime_type == "application/pdf":
        #     return pdf_to_tag(file_path)
        
        else:
            logger.warning(f"Unsupported file type: {file_path}")
            return get_tags_from_text(file_path)
    
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return []

def message_to_tag(message) -> list[str]:
    """
    根据用户的提示词生成用于查找文件的标签
    
    参数:
        message(str): 用户提示词
    
    返回:
        list[str]: 生成的标签列表
    
    使用示例:
        tags = message_to_tag("帮我找到与泰山有关的文件")
    """

    try:
        return get_tags_from_message(message)
    
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return []

if __name__ == "__main__":
    # 基础文件内容提取
    from basic import raw_to_text, docx_to_text, image_to_base64

    # AI打标函数
    from deepseek import get_tags_from_text, get_tags_from_message
    from XFyun import get_tags_from_data_url

    # 测试代码
    base_dir = os.path.dirname(os.path.abspath(__file__))

    txt = "..\\..\\test\\txt\\MicroRust_Introduction.txt"
    txt = os.path.join(base_dir, txt)
    txt = os.path.normpath(txt)
    tags = get_tags_from_text(raw_to_text(txt))
    print("获取的标签:", tags)

    docx = "..\\..\\test\\docx\\MicroRust_Introduction.docx"
    docx = os.path.join(base_dir, docx)
    docx = os.path.normpath(docx)
    tags = get_tags_from_text(docx_to_text(docx))
    print("获取的标签:", tags)

    pic = "..\\..\\test\\pic\\MicroRust.png"
    pic = os.path.join(base_dir, pic)
    pic = os.path.normpath(pic)
    tags = get_tags_from_data_url(image_to_base64(pic))
    print("获取的标签:", tags)

    tags = message_to_tag("帮我找到与泰山有关的文件")
    print("获取的标签:", tags)
else:
    # 基础文件内容提取
    from tagging.basic import raw_to_text, docx_to_text, image_to_base64

    # AI打标函数
    from tagging.deepseek import get_tags_from_text, get_tags_from_message
    from tagging.XFyun import get_tags_from_data_url