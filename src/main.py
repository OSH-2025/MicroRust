# 文件与路径操作
import os
import tempfile
from werkzeug.utils import secure_filename

import tempfile

# MIME类型识别
from mimetypes import guess_type

# 编码与解码处理
import base64

# 网络请求
from flask import Flask, request, render_template, jsonify

# AI打标接口
from tagging.tagging import file_to_tag, message_to_tag

# neo4j接口
from MR_neo4j.neo4j_handler import add_new_file, query_files_by_filename, query_files_by_cid, query_files_by_tags, delete_file_by_cid

# IPFS接口
from MR_IPFS.IPFS_init import start_ipfs, terminate_ipfs
from MR_IPFS.IPFS_handler import upload_file_to_ipfs, download_file_from_ipfs, get_file_content_from_ipfs

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods = ["POST"])
def upload_file():
    if "file" not in request.files:
        return (jsonify({"error": "没有文件被上传"}), 400)
    
    file = request.files["file"]
    if not file.filename:
        return (jsonify({"error": "没有选择文件"}), 400)
    
    try:
        # 创建一个临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            # 用原始文件名创建临时文件路径
            file_name = secure_filename(file.filename)
            file_path = os.path.join(tmpdir, file_name)

            # 保存上传文件到临时路径
            file.save(file_path)

            # 生成标签
            tags = file_to_tag(file_path)

            # 上传到IPFS
            cid = upload_file_to_ipfs(file_path)

            # 添加到Neo4j
            add_new_file(cid, file_name, tags)

            return jsonify({"success": True, "tags": tags})
    
    except Exception as e:
        return (jsonify({"error": str(e)}), 500)

@app.route("/search", methods=["POST"])
def search_files():
    search_type = request.form.get("search_type")
    search_query = request.form.get("search_query", "").strip()
    
    print("Search query: ", search_query)
    print("Search type: ", search_type)
    
    if not search_query:
        return jsonify({"results": [], "tags": []})
    
    if search_type == "nlp":
        tags = message_to_tag(search_query)
        results = query_files_by_tags(tags, limit = 5)
        return jsonify({"results": results, "tags": tags})
    
    elif search_type == "tags":
        tags = [tag.strip() for tag in search_query.split(",") if tag.strip()]
        results = query_files_by_tags(tags, limit = 5)
        return jsonify({"results": results, "tags": tags})
    
    elif search_type == "filename":
        results = query_files_by_filename(search_query)
        return jsonify({"results": results, "tags": []})
    
    return jsonify({"results": []})

@app.route("/preview/<cid>")
def get_preview(cid):
    try:
        result = query_files_by_cid(cid)
        file_name = result[0]["filename"]

        (mime_type, _) = guess_type(file_name)
        if mime_type and mime_type.startswith("text/"):
            content = get_file_content_from_ipfs(cid)
            return jsonify({"type": "text", "content": content})
        
        return jsonify({"type": "error"})
    
    except Exception as e:
        return (jsonify({"type": "error"}), 500)

@app.route("/download/<cid>")
def download(cid):
    try:
        # 获取文件名
        result = query_files_by_cid(cid)
        file_name = result[0]["filename"]
        
        # 获取下载路径
        download_url = download_file_from_ipfs(cid)
        
        # 浏览器重定向到该链接
        return jsonify({"url": download_url, "filename": file_name})
    
    except Exception as e:
        return (jsonify({"error": str(e)}), 500)

@app.route("/delete/<cid>", methods=["DELETE"])
def delete_file(cid):
    try:
        delete_file_by_cid(cid)
        return jsonify({"success": True})
    
    except Exception as e:
        return (jsonify({"error": str(e)}), 500)

if __name__ == "__main__":
    daemon = start_ipfs();
    app.run(debug = True, port = 5000, use_reloader = False)
    if daemon:
        terminate_ipfs(daemon)