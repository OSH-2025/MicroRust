import re
import os
import requests
import gradio as gr
import time
from typing import Optional, Tuple
from datetime import datetime
import json
from openai import OpenAI
from neo4j_handler import add_new_file
from deepseek_tagging import convert_file_to_text, get_tags_from_text
from IPFS_handler import upload_file_to_ipfs, get_file_content_from_ipfs

# ==================== 配置 ====================
DEEPSEEK_API_KEY = "sk-5c343e8522ef4787bcd862aa005af5b4"
MAX_FILE_SIZE = 10 * 1024 * 1024

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
        cid = upload_file_to_ipfs(file.name)
        uploaded_files[cid] = (file.name, datetime.now().strftime("%Y-%m-%d %H:%M"))
        # 获取 tag
        file_content = convert_file_to_text(file.name)
        tags = get_tags_from_text(file_content)

        # 更新Neo4j数据库    
        filename = os.path.basename(file.name)
        add_new_file(cid, filename, tags)
        
        return f"✅ 上传成功！\nCID: {cid}\n文件名: {file.name}\n标签:\n{tags}"
    except Exception as e:
        return f"❌ 上传失败: {str(e)}"

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
            file_content = get_file_content_from_ipfs(cid)
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