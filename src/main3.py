import re
import time
import json
import requests
from datetime import datetime
from typing import Optional, Tuple

import gradio as gr
from dashscope import MultiModal, Generation
from PyPDF2 import PdfReader
from docx import Document
import neo4j
from PIL import Image

# ==================== 配置 ====================
IPFS_API_URL = "http://127.0.0.1:5001"
DASHSCOPE_API_KEY = "your_dashscope_api_key"  # 替换为DashScope API Key
MAX_FILE_SIZE = 10 * 1024 * 1024  # 最大上传大小10MB
NEO4J_URI = "bolt://117.68.10.96:27734"
NEO4J_AUTH = ("neo4j", "Microrust")

# 存储已上传文件 {CID: (文件名, 上传时间)}
uploaded_files = {}

# 防抖相关变量
last_input_time = 0

# 设置 DashScope API Key
import os
os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY

# ==================== 增强版CID匹配 ====================
def match_cid(msg: str) -> Tuple[Optional[str], str]:
    """改进的CID匹配，支持更多格式"""
    if not msg:
        return None, "🟡 未检测到文件引用"

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

        # 获取文件预览
        preview = ""
        try:
            content_res = requests.get(
                f"https://ipfs.io/ipfs/{cid}",
                timeout=15
            )
            preview = content_res.text[:1000]
            if len(preview) == 1000:
                preview += "\n...[预览截断]"
        except Exception as e:
            preview = "🔒 无法预览二进制文件"

        # 获取 tag
        tags = get_tags_from_file(file.name)

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
            session.run("MERGE (f:File {name: $cid})", cid=cid)
            for tag in tags:
                session.run("MERGE (t:Tag {name: $tag})", tag=tag)
                session.run(
                    "MATCH (f:File {name: $cid}), (t:Tag {name: $tag}) "
                    "MERGE (f)-[:TAGGED_WITH]->(t)",
                    cid=cid, tag=tag
                )

    except Exception as e:
        print(f"❌ Neo4j ERROR: {str(e)}")
    finally:
        driver.close()

# ==================== 文件内容提取 ====================
def convert_file_to_text(file_path: str) -> str:
    """将文件内容转换为文本，支持txt、pdf和docx格式"""
    try:
        if file_path.endswith('.pdf'):
            reader = PdfReader(file_path)
            return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        return f"文件读取错误: {str(e)}"

# ==================== 多模态打标处理 ====================
def get_tags_from_file(file_path: str) -> list:
    """根据文件类型调用不同模型获取标签"""
    if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        return analyze_image(file_path)
    elif file_path.lower().endswith(('.mp4', '.avi')):
        return analyze_video(file_path)
    else:
        text = convert_file_to_text(file_path)
        return get_tags_from_text(text)

def analyze_image(file_path: str) -> list:
    """使用通义千问API分析图片"""
    client = MultiModal(api_key=DASHSCOPE_API_KEY)
    with open(file_path, "rb") as img_file:
        response = client.call(
            model='qwen-vl-chat',
            input={
                'image': img_file,
                'text': '请为这张图片生成4-7个标签，逗号分隔。'
            }
        )
    try:
        tags = json.loads(response.output.text)['tags']
        return tags[:7]
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return ["unknown"]

def analyze_video(file_path: str) -> list:
    """使用通义千问API分析视频"""
    # 注意：此部分需要根据实际提供的API进行适当调整，可能需要增改import部分
    # 假设有一个适用于视频分析的API端点
    client = Generation(api_key=DASHSCOPE_API_KEY)
    with open(file_path, "rb") as vid_file:
        response = client.call(
            model='qwen-video-analysis',  # 这里假设存在一个视频分析模型
            input={
                'video': vid_file,
                'text': '请为这段视频生成4-7个标签，逗号分隔。'
            }
        )
    try:
        tags = json.loads(response.output.text)['tags']
        return tags[:7]
    except Exception as e:
        print(f"Error analyzing video: {e}")
        return ["unknown"]

def get_tags_from_text(text: str) -> list:
    """使用通义千问API获取文本标签"""
    client = Generation(api_key=DASHSCOPE_API_KEY)
    prompt = f"请为以下文本生成4-7个标签：\n\n{text}"
    response = client.call(model="qwen-turbo", prompt=prompt)
    try:
        output = response.output.text.strip()
        tags = [t.strip() for t in output.split(",")]
        return tags[:7]
    except Exception as e:
        print(f"Error getting tags from text: {e}")
        return ["unknown"]

# ==================== 消息处理核心逻辑 ====================
def process_message(message: str, chat_history: list) -> Tuple[str, list, str]:
    """统一处理消息和CID替换"""
    if not message:
        return "", chat_history, "⚠️ 请输入消息"

    cid, status_msg = match_cid(message)
    display_message = message

    if cid and cid in uploaded_files:
        display_message = message.replace(cid, "上述文件", 1)
        status_msg = f"✅ 正在分析: {uploaded_files[cid][0][:15]}..."

        try:
            response = requests.get(f"https://ipfs.io/ipfs/{cid}", timeout=30)
            file_content = response.text[:5000]
            api_message = f"文件内容：\n{file_content}\n\n用户问题：{message}"
        except Exception as e:
            return "", chat_history, f"⚠️ 文件读取失败: {str(e)}"
    else:
        api_message = message

    # 使用 Qwen-turbo 回答问题
    try:
        client = Generation(api_key=DASHSCOPE_API_KEY)
        response = client.call(model="qwen-turbo", prompt=api_message)
        ai_response = response.output.text
        chat_history.append((display_message, ai_response))
    except Exception as e:
        chat_history.append((display_message, f"⚠️ API错误: {str(e)}"))

    return "", chat_history, status_msg

# ==================== 简化版界面 ====================
with gr.Blocks(title="IPFS文件分析") as app:
    gr.Markdown("## 📡 IPFS文件分析系统")

    # 文件上传区
    with gr.Row():
        file_upload = gr.UploadButton("📤 上传文件", file_types=[".txt", ".pdf", ".docx", ".cpp", ".csv", ".jpg", ".jpeg", ".png", ".mp4"])
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