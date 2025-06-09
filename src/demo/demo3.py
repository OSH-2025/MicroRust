import re
import requests
import gradio as gr
import time
from typing import Optional, Tuple
from datetime import datetime
import json
from openai import OpenAI
import neo4j

# ==================== 配置 ====================
IPFS_API_URL = "http://127.0.0.1:5001"
DEEPSEEK_API_KEY = "sk-5c343e8522ef4787bcd862aa005af5b4"
MAX_FILE_SIZE = 10 * 1024 * 1024
NEO4J_URI = "bolt://117.68.10.96:27734"
NEO4J_AUTH = ("neo4j", "Microrust")

# 存储已上传文件 {CID: (文件名, 上传时间)}
uploaded_files = {}

# 防抖相关变量
last_input_time = 0

# ==================== 增强版CID匹配 ====================
def match_cid(msg: str) -> Tuple[Optional[str], str]:
    """改进的CID匹配，支持更多格式"""
    if not msg:
        return None, "🟡 未检测到文件引用"
    
    # 匹配更广泛的CID格式（包括v1和v0）
    cid_pattern = r"\b(Qm[1-9A-HJ-NP-Za-km-z]{44}|bafy[0-9A-Za-z]{44,})\b"
    matches = re.findall(cid_pattern, msg)
    
    if matches:
        for cid in matches:
            if cid in uploaded_files:
                filename = uploaded_files[cid][0]
                return cid, f"✅ 已关联文件: {filename[:15]}..."
        return matches[0], f"🟠 检测到CID但未上传: {matches[0][:6]}..."
    
    return None, "🟡 未检测到文件引用"

# ==================== 防抖函数 ====================
def debounced_match_cid(message):
    global last_input_time
    current_time = time.time() * 1000  # 转换为毫秒
    
    # 如果距离上次输入不足500毫秒，不处理
    if current_time - last_input_time < 500:
        return "🟡 正在输入..."
    
    last_input_time = current_time
    return match_cid(message)[1]

# ==================== 文件上传处理 ====================
def handle_upload(file) -> str:
    """处理文件上传，确保更新全局状态"""
    if not file:
        return "⚠️ 请先选择文件"
    
    try:
        with open(file.name, "rb") as f:
            response = requests.post(
                f"{IPFS_API_URL}/api/v0/add",
                files={"file": f},
                timeout=30
            )
        response.raise_for_status()
        result = response.json()
        cid = result["Hash"]
        uploaded_files[cid] = (file.name, datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        # 获取文件预览（限制在1000字符内）
        preview = ""
        try:
            content_res = requests.post(
                f"{IPFS_API_URL}/api/v0/cat?arg={cid}",
                timeout=15
            )
            preview = content_res.text[:10]
            if len(preview) == 10:
                preview += "\n...[预览截断]"
        except:
            preview = "🔒 无法预览二进制文件"

        # 获取 tag
        file_content = convert_file_to_text(file.name)
        tags = get_tags_from_text(f"File name: {file.name}\nFile content: {file_content}")

        # 更新Neo4j数据库    
        add_new_file_on_neo4j(cid, tags)
        
        return f"✅ 上传成功！\nCID: {cid}\n文件名: {file.name}\n标签:\n{tags}"
    except Exception as e:
        return f"❌ 上传失败: {str(e)}"

# ==================== Neo4j ====================
def add_new_file_on_neo4j(cid, tags) -> None:
    try:
        driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        with driver.session() as session:
             # 更新Neo4j数据库, 文件和 cid 视为点，tag 视为点，关联关系视为边
            session.run(
                    "MERGE (f:File {name: $cid})",  # 用 MERGE，避免重复插入
                    cid=cid
                )
            for tag in tags:
                session.run(
                    "MERGE (t:Tag {name: $tag})",  # 用 MERGE，避免重复插入
                    tag=tag
                )
                session.run(
                    "MATCH (f:File {name: $cid}), (t:Tag {name: $tag}) "
                    "MERGE (f)-[:TAGGED_WITH]->(t)",
                    cid=cid, tag=tag
                )

    except Exception as e:
        return f"❌ Neo4j ERROR: {str(e)}"
    finally:
        driver.close()

# ==================== deepseek AI 打标处理 ====================
def convert_file_to_text(file_path: str) -> str:
    """将文件内容转换为文本，支持txt、pdf和docx格式"""
    try:
        if file_path.endswith('.pdf'):
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        elif file_path.endswith('.docx'):
            from docx import Document
            doc = Document(file_path)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        return f"文件读取错误: {str(e)}"

def get_tags_from_text(text: str) -> list:
    """使用DeepSeek AI获取文本标签"""
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
    )
    
    system_prompt = """
    The user will provide some text. Please output 4-7 tags for the text in JSON format. 

    EXAMPLE INPUT: 
    File name : example.txt
    File content : Which is the highest mountain in the world? Mount Everest.

    EXAMPLE JSON OUTPUT:
    {
        "tag": ["geography", "mountains", "world", "txt"]
    }
    """
    
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": text}]
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )
    
    return json.loads(response.choices[0].message.content).get("tag", [])

# ==================== 消息处理核心逻辑 ====================
def process_message(message: str, chat_history: list) -> Tuple[str, list, str]:
    """统一处理消息和CID替换"""
    if not message:
        return "", chat_history, "⚠️ 请输入消息"
    
    cid, status_msg = match_cid(message)
    display_message = message
    
    if cid and cid in uploaded_files:
        # 只替换第一个出现的CID
        display_message = message.replace(cid, "上述文件", 1)
        status_msg = f"✅ 正在分析: {uploaded_files[cid][0][:15]}..."
        
        # 获取文件内容（限制大小）
        try:
            response = requests.post(
                f"{IPFS_API_URL}/api/v0/cat?arg={cid}",
                timeout=30,
                stream=True
            )
            file_content = response.text[:5000]
            api_message = f"文件内容：\n{file_content}\n\n用户问题：{message}"
        except Exception as e:
            return "", chat_history, f"⚠️ 文件读取失败: {str(e)}"
    else:
        api_message = message
    
    # 调用API
    try:
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": api_message}],
            "temperature": 0.7
        }
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        ai_response = response.json()["choices"][0]["message"]["content"]
        chat_history.append((display_message, ai_response))
    except Exception as e:
        chat_history.append((display_message, f"⚠️ API错误: {str(e)}"))
    
    return "", chat_history, status_msg

# ==================== 简化版界面 ====================
with gr.Blocks(title="IPFS文件分析") as app:
    gr.Markdown("## 📡 IPFS文件分析系统")
    
    # 文件上传区
    with gr.Row():
        file_upload = gr.UploadButton("📤 上传文件", file_types=[".txt", ".pdf", ".docx", ".cpp", ".csv"])
        upload_status = gr.Markdown("等待文件上传...")
    
    # 聊天区
    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(label="输入消息", placeholder="输入问题或CID...")
    status_display = gr.Markdown("🟡 等待输入...")
    
    # 操作按钮
    with gr.Row():
        submit_btn = gr.Button("🚀 发送")
        clear_btn = gr.ClearButton([msg, chatbot, upload_status])

    # 事件绑定
    file_upload.upload(
        handle_upload,
        inputs=file_upload,
        outputs=upload_status
    )
    
    submit_btn.click(
        process_message,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot, status_display]
    )
    
    # 使用自定义防抖函数替代debounce
    msg.change(
        fn=debounced_match_cid,
        inputs=msg,
        outputs=status_display
    )

if __name__ == "__main__":
    app.launch(server_port=7860)