import json
import os
from openai import OpenAI

DEEPSEEK_API_KEY = "sk-5c343e8522ef4787bcd862aa005af5b4"

def convert_file_to_text(file_path: str) -> str:
    """
    将文件内容转换为文本, 支持pdf, docx和txt格式
    输入：文件路径
    输出：文件内容文本
    """
    
    text = ""
    
    try:
        if file_path.endswith(".pdf"):
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        
        elif file_path.endswith(".docx"):
            from docx import Document
            doc = Document(file_path)
            text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
    
    except Exception as e:
        return f"文件读取错误: {str(e)}"
    
    filename = os.path.basename(file_path)
    
    return f"File name: {filename}\nFile content: {text}"

def get_tags_from_text(text: str) -> list:
    """
    使用DeepSeek AI获取文本标签
    输入：文本
    输出：标签列表
    例子：
        输入: "File name: example.txt
              File content: Which is the highest mountain in the world? Mount Everest."
        输出: ["geography", "mountains", "world", "txt"]
    """

    client = OpenAI(
        api_key = DEEPSEEK_API_KEY,
        base_url = "https://api.deepseek.com",
    )
    
    system_prompt = """
    The user will provide some text. Please output 4-7 tags for the text in JSON format. 
    
    EXAMPLE INPUT: 
    File name: example.txt
    File content: Which is the highest mountain in the world? Mount Everest.
    
    EXAMPLE JSON OUTPUT:
    {
        "tag": ["geography", "mountains", "world", "txt"]
    }
    """
    
    response = client.chat.completions.create(
        model = "deepseek-chat",
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": text
            }
        ],
        response_format = {"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content or "{}").get("tag", [])

if __name__ == "__main__":
    # 测试代码
    sample_text = "Which is the highest mountain in the world? Mount Everest."
    tags = get_tags_from_text(sample_text)
    print("获取的标签:", tags)