# 文件与路径操作
import os

# 数据格式处理
import json

# AI接口服务
from openai import OpenAI

DEEPSEEK_API_KEY = "sk-5c343e8522ef4787bcd862aa005af5b4"

def get_tags_from_text(text: str) -> list:
    """
    使用deepseek获取文本标签
    输入: 文本
    输出: 标签列表
    例子:
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
    Which is the highest mountain in the world? Mount Everest.
    
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
    
def get_tags_from_message(text: str) -> list:
    """
    使用deepseek从用户的自然语言中获取需要查找的标签并保证上下文关系
    输入: 文本
    输出：标签列表
    
    例子:
        text = "我需要查找python相关的文件"
        tags = get_deepseek_tags_from_text(text)
        print(tags)
    """
    client = OpenAI(
        api_key = DEEPSEEK_API_KEY,
        base_url = "https://api.deepseek.com",
    )

    system_prompt = """
    You are an AI assistant designed to help users find files based on their input.
    When the user provides some text, your task is to generate 5 tags that will help locate the most relevant content in the file system.
    The tags should be relevant to the user's request and reflect the main topics or keywords that would aid in file search.
    
    EXAMPLE INPUT:
    Help me find files related to Mount Tai.
    
    EXAMPLE JSON OUTPUT:
    {
        "tag": ["geography", "mountains", "world", "tourism"]
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