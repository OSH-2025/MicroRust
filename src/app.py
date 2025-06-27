from flask import Flask, render_template, request, jsonify, send_file, url_for
import os
from werkzeug.utils import secure_filename
from utils.neo4j_handler import add_new_file, query_files_by_tags, query_files_by_filename, delete_file_by_cid
from utils.IPFS_handler import upload_file_to_ipfs, get_file_content_from_ipfs
from utils.ai_tagging import auto_to_tag
import fitz  # PyMuPDF for PDF handling
from PIL import Image
import io
import docx
import base64
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传文件夹存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_preview(file_path, file_type):
    """生成文件预览内容"""
    try:
        if file_type == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return {'type': 'text', 'content': f.read()[:2000]}  # 返回前2000个字符
        elif file_type == 'pdf':
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return {'type': 'text', 'content': text[:2000]}
        elif file_type in ['png', 'jpg', 'jpeg']:
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                return {'type': 'image', 'content': f'data:image/{file_type};base64,{encoded_string}'}
        elif file_type == 'docx':
            doc = docx.Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return {'type': 'text', 'content': text[:2000]}
        return {'type': 'error', 'content': '不支持的文件类型'}
    except Exception as e:
        return {'type': 'error', 'content': f'预览生成失败: {str(e)}'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件被上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件类型'}), 400

    try:
        # 生成带时间戳的文件名，避免重名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = secure_filename(timestamp + file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 使用AI生成标签
        tags = auto_to_tag(file_path)
        if isinstance(tags, str) and tags.startswith("Error"):
            tags = []  # 如果标签生成失败，使用空列表
        
        # 上传到IPFS
        cid = upload_file_to_ipfs(file_path)
        if cid.startswith("上传失败"):
            return jsonify({'error': cid}), 500
        
        # 添加到Neo4j
        add_new_file(cid, filename, tags)
        
        # 生成预览
        file_type = filename.rsplit('.', 1)[1].lower()
        preview = get_file_preview(file_path, file_type)
        
        # 删除临时文件
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'cid': cid,
            'tags': tags,
            'preview': preview
        })
    
    except Exception as e:
        # 确保清理临时文件
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search_files():
    search_type = request.form.get('search_type')
    search_query = request.form.get('search_query', '').strip()
    
    print("Search query: ", search_query)
    print("Search type: ", search_type)
    
    if not search_query:
        return jsonify({'results': []})
    
    if search_type == 'tags':
        tags = [tag.strip() for tag in search_query.split(',') if tag.strip()]
        results = query_files_by_tags(tags, limit=5)
    else:  # filename
        results = query_files_by_filename(search_query)
    
    return jsonify({'results': results})

@app.route('/delete/<cid>', methods=['DELETE'])
def delete_file(cid):
    try:
        delete_file_by_cid(cid)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preview/<cid>')
def get_preview(cid):
    try:
        content = get_file_content_from_ipfs(cid)
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 