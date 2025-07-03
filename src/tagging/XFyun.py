# 线程与并发处理
import _thread as thread

# 日期与时间处理
import datetime
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time

# 数据格式处理
import json

# 加密与哈希处理
import hashlib
import hmac

# 编码与解码处理
import base64

# 网络请求
from urllib.parse import urlencode
import ssl
import websocket

XFYUN_APP_ID = "2d773673"
XFYUN_API_SECRET = "OWZiMDk0ODkyNTc4MDVjODM2NWFmNmZh"
XFYUN_API_KEY = "659100c0db628af3f3a4fa2cc980e48e"
REQUEST_HOST = "spark-api.cn-huabei-1.xf-yun.com"
REQUEST_METHOD = "/v2.1/image"
API_URL = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"

def general_url_authentication():
    cur_time = datetime.now()
    date = format_date_time(mktime(cur_time.timetuple()))
    
    tmp = "host: " + REQUEST_HOST + "\n"
    tmp += "date: " + date + "\n"
    tmp += "GET " + REQUEST_METHOD + " HTTP/1.1"
    
    tmp_sha = hmac.new(XFYUN_API_SECRET.encode('utf-8'), tmp.encode('utf-8'), digestmod = hashlib.sha256).digest()
    
    signature = base64.b64encode(tmp_sha).decode(encoding = 'utf-8')
    
    authorization_origin = f"api_key=\"{XFYUN_API_KEY}\", algorithm=\"hmac-sha256\", headers=\"host date request-line\", signature=\"{signature}\""
    
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    
    v = {
		"authorization": authorization,
        "date": date,
    	"host": REQUEST_HOST
    }
    url = API_URL + '?' + urlencode(v)
    return url

# 收到websocket连接建立的处理
def on_open(ws, data_url):
    prompt = """
    You are an API that extracts image tags from a base64-encoded image provided in a data URL.
    
    Your only task is to output 4 to 7 relevant tags for the image in strict JSON format.
    Do not include any commentary, explanation, markdown, or natural language before or after the JSON.
    Only output the JSON object — nothing else.
    
    EXAMPLE JSON OUTPUT:
    {
        "tag": ["geography", "mountains", "world", "jpg"]
    }
    """
    
    data = {
        "header": {
            "app_id": XFYUN_APP_ID
        },
        "parameter": {
            "chat": {
                "domain": "imagev3",
                "temperature": 0.5,
                "top_k": 4,
                "max_tokens": 2028,
                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text":
                [
                    {
                        "role": "user",
                        "content": data_url,
                        "content_type": "image"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        }
    }
    
    data = json.dumps(data)
    ws.send(data)

# 收到websocket消息的处理
def on_message(ws, message, callback):
    data = json.loads(message)
    content = ""

    if((data['header']['code']) != 0):
        ws.close()
    
    else:
        content = data["payload"]["choices"]["text"][0]["content"]
        if((data["payload"]["choices"]["status"]) == 2):
            ws.close()
    
    callback(content)

def get_tags_from_data_url(data_url: str) -> list[str]:
    """
    使用讯飞星火大模型获取data URL标签
    输入: data URL
    输出：标签列表
    """
    
    url = general_url_authentication()
    
    response = ""
    def callback(content):
        nonlocal response
        response += content
    
    ws = websocket.WebSocketApp(url, on_message = lambda ws, message: on_message(ws, message, callback), on_open = (lambda ws: on_open(ws, data_url)))
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    
    return json.loads(response or "{}").get("tag", [])