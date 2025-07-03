import re
import requests
import gradio as gr
import time
import os
import json
from typing import Optional, Tuple, List, Dict
from datetime import datetime
from docx import Document

# ==================== 配置 ====================
IPFS_API_URL = "http://192.168.67.128:5001"
DEEPSEEK_API_KEY = "sk-5c343e8522ef4787bcd862aa005af5b4"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_EXTENSIONS = [".txt", ".pdf", ".docx", ".jpg"]

# 存储已上传文件 {CID: (文件名, 上传时间, 文件类型, 文件路径)}
uploaded_files: Dict[str, Tuple[str, str, str, str]] = {}

# 防抖相关变量
last_input_time = 0

# ==================== 辅助函数 ====================
def match_cid(msg: str) -> Tuple[Optional[str], str]:
    """从消息中匹配CID"""
    if not msg:
        return None, "🟡 未检测到文件引用"
    
    cid_pattern = r"\b(Qm[1-9A-HJ-NP-Za-km-z]{44}|bafy[0-9A-Za-z]{44,})\b"
    matches = re.findall(cid_pattern, msg)
    
    if matches:
        cid = matches[0]
        if cid in uploaded_files:
            filename = uploaded_files[cid][0]
            return cid, f"✅ 匹配文件: {filename}"
        return None, f"🟠 CID未找到文件: {cid[:10]}..."
    
    return None, "🟡 未检测到文件引用"

def safe_read_file(file_path: str) -> str:
    """安全读取文件内容，确保UTF-8编码"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        encodings = ["utf-8-sig", "gbk", "gb2312", "big5"]
        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    content = f.read()
                # 转换回UTF-8
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return content
            except:
                continue
        raise ValueError("⚠️ 无法解析文件编码")

def validate_file(file_path: str):
    """验证文件是否有效"""
    if not os.path.exists(file_path):
        raise FileNotFoundError("文件不存在")
    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        raise ValueError(f"文件大小超过限制({MAX_FILE_SIZE/1024/1024}MB)")

def decode_docx(file_path: str) -> str:
    """解码docx文件内容"""
    try:
        doc = Document(file_path)
        content = "\n".join([para.text for para in doc.paragraphs])
        return content
    except Exception as e:
        raise ValueError(f"无法解码docx文件: {str(e)}")

# ==================== 文件上传 ====================
def handle_upload(file) -> str:
    """处理文件上传到IPFS"""
    if not file:
        return "⚠️ 请选择文件"
    
    try:
        validate_file(file.name)
        ext = os.path.splitext(file.name)[1].lower()
        
        if ext not in SUPPORTED_EXTENSIONS:
            return f"❌ 不支持的文件类型: {ext}"
        
        # 处理文本文件编码
        if ext == ".txt":
            safe_read_file(file.name)  # 这会自动转换编码为UTF-8
        elif ext == ".docx":
            content = decode_docx(file.name)
            with open(file.name, "w", encoding="utf-8") as f:
                f.write(content)
        
        # 上传到IPFS
        with open(file.name, "rb") as f:
            response = requests.post(
                f"{IPFS_API_URL}/api/v0/add",
                files={"file": f},
                timeout=30
            )
        response.raise_for_status()
        
        result = response.json()
        cid = result["Hash"]
        uploaded_files[cid] = (
            os.path.basename(file.name),
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            ext.strip("."),
            file.name
        )
        
        return f"✅ 上传成功\nCID: {cid}\n文件名: {uploaded_files[cid][0]}"
    
    except Exception as e:
        return f"❌ 上传失败: {str(e)}"

# ==================== 命令解析 ====================
def parse_command(message: str, cid: str) -> List[List[str]]:
    """使用DeepSeek API解析用户命令为指定格式"""
    try:
        file_type = uploaded_files[cid][2] if cid in uploaded_files else "unknown"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = (
            f"请将以下命令解析为Python列表的列表格式 [[操作], [关键词], [文件类型], [cid]]\n"
            f"1. 必须返回Python列表的列表格式，不能是JSON或其他格式\n"
            f"2. 操作仅限：add_prefix(在句首加), add_suffix(在句尾加), delete(删除), find(查找), download(下载)\n"
            f"3. 关键词可以是多个的数组，如查找可以是[["草"]["猫"]]，没有关键词则为空列表[]\n"
            f"4. 文件类型是当前文件类型或unknown\n"
            f"5. 每条指令仅返回一条结构\n\n"
            f"6. 添加句子的两条指令关键词为添加的内容，删除句子的关键词为空列表，查找的关键词为查找内容，下载的关键词为空列表\n"
            f"示例1: "在文件Qm...开头添加：霓虹" → [["add_prefix"], ["霓虹"], ["{file_type}"], ["Qm..."]]\n"
            f"示例2: "删除文件bafy..." → [["delete"], [], ["{file_type}"], ["bafy..."]]\n"
            f"示例3: "查找一张有猫的图片" → [["find"], ["猫"], ["unknown"], []]\n"
            f"示例4: "查找一张带有草的png图片" → [["find"], ["草"], ["png"], []]\n"
            f"当前命令: {message}\nCID: {cid}\n文件类型: {file_type}"
        )
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=15
        )
        response.raise_for_status()
        
        result = response.json()["choices"][0]["message"]["content"]
        
        # 直接解析为Python列表
        try:
            # 移除可能的多余字符
            cleaned_result = result.strip().replace("```python", "").replace("```", "").strip()
            parsed_result = eval(cleaned_result)
            print(f"解析结果: {parsed_result}")
            # 验证结果格式
            if (isinstance(parsed_result, list) and len(parsed_result) == 4 and
                all(isinstance(item, list) for item in parsed_result)):
                return parsed_result
            else:
                raise ValueError("返回的格式不正确")
        except Exception as e:
            print(f"解析结果失败: {str(e)}")
            print(f"原始返回内容: {result}")
            raise ValueError("无法解析返回的列表格式")
    
    except Exception as e:
        print(f"命令解析失败: {str(e)}")
        return [["parse_error"], [], ["unknown"], [cid]]

# ==================== 消息处理 ====================
def process_message(message: str, chat_history: list, confirmed: bool = False) -> Tuple[str, list, str]:
    """处理用户消息并执行相应操作"""
    if not message.strip():
        return "", chat_history, "⚠️ 请输入有效消息"
    
    # 匹配CID
    cid, status_msg = match_cid(message)
    cid = cid or "unknown"
    
    try:
        # 解析命令
        command_parts = parse_command(message, cid)
        operations, keywords, file_type, cid_list = command_parts
        
        operation = operations[0][0] if operations else ""
        keyword_list = keywords if keywords else []
        filetype = file_type[0][0] if file_type else "unknown"
        real_cid = cid_list[0][0] if cid_list else cid
        
        filename = uploaded_files.get(real_cid, ("未知文件",))[0]
        
        # 确认流程
        if not confirmed:
            operation_map = {
                "add_prefix": "在句首添加内容",
                "add_suffix": "在句末添加内容",
                "delete": "删除内容",
                "find": "查找内容",
                "download": "下载文件"
            }
            
            display_operation = operation_map.get(operation, operation)
            keywords_display = "、".join(keyword_list) if keyword_list else "无"
            
            confirm_msg = (
                f"📄 操作确认\n"
                f"-------------------------\n"
                f"📂 文件名: {filename}\n"
                f"🛠️ 操作: {display_operation}\n"
                f"🔑 关键词: {keywords_display}\n"
                f"📄 文件类型: {filetype}\n"
                f"-------------------------\n"
                f"请确认是否执行？"
            )
            return "", chat_history, confirm_msg
        
        # 确认后的操作反馈（模拟）
        result_text = (
            f"✅ 操作执行成功\n"
            f"-------------------------\n"
            f"📂 文件名: {filename}\n"
            f"🛠️ 操作: {operation}\n"
            f"🔑 关键词: {"、".join(keyword_list) if keyword_list else "无"}\n"
            f"📄 文件类型: {filetype}\n"
            f"🆔 CID: {real_cid}\n"
            f"-------------------------\n"
            f"（此为模拟反馈）"
        )
        chat_history.append((message, result_text))
        return "", chat_history, "✅ 操作已完成"
    
    except Exception as e:
        error_msg = f"❌ 操作失败: {str(e)}"
        chat_history.append((message, error_msg))
        return "", chat_history, "⚠️ 操作失败"

# ==================== 防抖函数 ====================
def debounced_match_cid(message):
    """防抖的CID匹配函数"""
    global last_input_time
    current_time = time.time() * 1000
    if current_time - last_input_time < 500:
        return "🟡 正在输入..."
    last_input_time = current_time
    return match_cid(message)[1]

# ==================== Gradio界面 ====================
with gr.Blocks(title="IPFS文件操作系统") as app:
    gr.Markdown("## 📦 IPFS文件智能指令系统")

    with gr.Row():
        file_upload = gr.UploadButton("📤 上传文件", file_types=SUPPORTED_EXTENSIONS)
        upload_status = gr.Markdown("等待文件上传...")

    chatbot = gr.Chatbot(height=400, label="操作记录")
    msg = gr.Textbox(label="输入操作指令", placeholder="例如：在文件Qm...开头添加"内容"...")
    status_display = gr.Markdown("🟡 等待输入...")

    with gr.Row():
        submit_btn = gr.Button("🚀 发送")
        confirm_btn = gr.Button("✅ 确认操作")
        cancel_btn = gr.Button("❌ 取消操作")
        clear_btn = gr.ClearButton([msg, chatbot, upload_status])

    # 事件绑定
    file_upload.upload(handle_upload, inputs=file_upload, outputs=upload_status)
    submit_btn.click(
        process_message, 
        inputs=[msg, chatbot], 
        outputs=[msg, chatbot, status_display]
    )
    confirm_btn.click(
        lambda x, y: process_message(x, y, True), 
        inputs=[msg, chatbot], 
        outputs=[msg, chatbot, status_display]
    )
    cancel_btn.click(
        lambda: ("", chatbot, "❌ 操作已取消"), 
        outputs=[msg, chatbot, status_display]
    )
    msg.change(
        fn=debounced_match_cid, 
        inputs=msg, 
        outputs=status_display
    )

if __name__ == "__main__":
    app.launch(server_port=7860)