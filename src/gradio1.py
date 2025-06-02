import re
import requests
import gradio as gr
import time
from typing import Optional, Tuple
from datetime import datetime

# ==================== 配置 ====================
IPFS_API_URL = "http://192.168.220.131:5001"
DEEPSEEK_API_KEY = "your_api_key_here"
MAX_FILE_SIZE = 10 * 1024 * 1024
CHUNK_SIZE = 1024 * 512  # 每次读取512KB
MAX_RETRIES = 3  # 最大重试次数

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
        return None, f"🟠 检测到CID但未上传: {matches[0][:6]}..."
    
    return None, "🟡 未检测到文件引用"

# ==================== 防抖函数 ====================
def debounced_match_cid(message):
    global last_input_time
    current_time = time.time() * 1000  # 转换为毫秒
    
    if current_time - last_input_time < 500:
        return "🟡 正在输入..."
    
    last_input_time = current_time
    return match_cid(message)[1]

# ==================== 文件上传处理（带轮询） ====================
def handle_upload(file) -> str:
    """处理文件上传，确保更新全局状态"""
    if not file:
        return "⚠️ 请先选择文件"
    
    try:
        # 确保文件以二进制模式读取，保持原始编码
        with open(file.name, "rb") as f:
            # 分块上传
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
                timeout=15,
                headers={"Accept": "text/plain; charset=utf-8"}
            )
            content_res.encoding = 'utf-8'  # 强制使用UTF-8解码
            preview = content_res.text[:1000]
            if len(content_res.text) > 1000:
                preview += "\n...[预览截断]"
        except Exception as e:
            preview = f"🔒 无法预览文件: {str(e)}"
        
        return f"✅ 上传成功！\nCID: {cid}\n文件名: {file.name}\n预览:\n{preview}"
    except Exception as e:
        return f"❌ 上传失败: {str(e)}"

# ==================== 分块读取IPFS文件 ====================
def read_ipfs_file(cid: str, max_length: int = 5000) -> str:
    """分块读取IPFS文件内容，确保完整读取"""
    content = ""
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            response = requests.post(
                f"{IPFS_API_URL}/api/v0/cat?arg={cid}",
                timeout=30,
                stream=True,
                headers={"Accept": "text/plain; charset=utf-8"}
            )
            response.encoding = 'utf-8'  # 强制使用UTF-8解码
            
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE, decode_unicode=True):
                if chunk:
                    content += chunk
                    if len(content) >= max_length:
                        content = content[:max_length]
                        content += "\n...[内容截断]"
                        return content
            return content
        except requests.exceptions.ChunkedEncodingError:
            retries += 1
            time.sleep(1)
        except Exception as e:
            return f"⚠️ 文件读取失败: {str(e)}"
    
    return "⚠️ 达到最大重试次数，文件读取失败"

# ==================== 消息处理核心逻辑 ====================
def process_message(message: str, chat_history: list) -> Tuple[str, list, str]:
    """统一处理消息和CID替换"""
    if not message:
        return "", chat_history, "⚠️ 请输入消息"
    
    cid, status_msg = match_cid(message)
    display_message = message
    
    if cid:
        display_message = message.replace(cid, "上述文件", 1)
        status_msg = f"✅ 正在分析: {uploaded_files[cid][0][:15]}..."
        
        # 获取文件内容（使用分块读取）
        file_content = read_ipfs_file(cid)
        if file_content.startswith("⚠️"):
            return "", chat_history, file_content
        
        api_message = f"文件内容：\n{file_content}\n\n用户问题：{display_message}"
    else:
        api_message = message
    
    # 调用API
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json; charset=utf-8"
        }
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

# ==================== 界面 ====================
with gr.Blocks(title="IPFS文件分析") as app:
    gr.Markdown("## 📡 IPFS文件分析系统")
    
    with gr.Row():
        file_upload = gr.UploadButton("📤 上传文件", file_types=[".txt", ".pdf", ".docx"])
        upload_status = gr.Markdown("等待文件上传...")
    
    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(label="输入消息", placeholder="输入问题或CID...")
    status_display = gr.Markdown("🟡 等待输入...")
    
    with gr.Row():
        submit_btn = gr.Button("🚀 发送")
        clear_btn = gr.ClearButton([msg, chatbot, upload_status])

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
    
    msg.change(
        fn=debounced_match_cid,
        inputs=msg,
        outputs=status_display
    )

if __name__ == "__main__":
    app.launch(server_port=7860)