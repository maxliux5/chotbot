#!/usr/bin/env python3
"""
RAG自动加载工具：自动加载doc目录的文件并跟踪已加载的文件
"""

import os
import json
import hashlib
from typing import List, Dict

# 配置
DOC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "doc"))
TRACK_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".rag_loaded.json"))

def get_file_hash(file_path: str) -> str:
    """计算文件的MD5哈希值"""
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        # 分块读取大文件
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def load_loaded_files() -> Dict[str, str]:
    """加载已加载文件的记录"""
    if os.path.exists(TRACK_FILE):
        try:
            with open(TRACK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_loaded_files(loaded: Dict[str, str]) -> None:
    """保存已加载文件的记录"""
    with open(TRACK_FILE, "w", encoding="utf-8") as f:
        json.dump(loaded, f, indent=2, ensure_ascii=False)

def get_new_or_updated_files(doc_dir: str = None) -> List[str]:
    """获取新的或更新过的文件"""
    doc_dir = doc_dir or DOC_DIR
    loaded = load_loaded_files()
    new_files = []
    
    # 遍历doc目录下的所有文件（支持嵌套目录）
    for root, dirs, files in os.walk(doc_dir):
        for file_name in files:
            # 过滤常见文档格式
            if file_name.endswith((".md", ".txt", ".pdf", ".docx", ".rst")):
                file_path = os.path.join(root, file_name)
                file_hash = get_file_hash(file_path)
                
                # 检查文件是否未加载或已更新
                if file_path not in loaded or loaded[file_path] != file_hash:
                    new_files.append(file_path)
    
    return new_files

def load_documents(doc_dir: str = None) -> List[str]:
    """加载doc目录下的所有文档内容（支持MD/TXT/RST/PDF）"""
    doc_dir = doc_dir or DOC_DIR
    documents = []
    
    for root, dirs, files in os.walk(doc_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            try:
                # 处理Markdown/Text/ReST文件
                if file_name.endswith((".md", ".txt", ".rst")):
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if content.strip():
                            documents.append(content)
                
                # 处理PDF文件
                elif file_name.endswith(".pdf"):
                    from pdfminer.high_level import extract_text
                    
                    # 使用pdfminer.six提取PDF内容
                    pdf_content = extract_text(file_path)
                    
                    if pdf_content.strip():
                        documents.append(pdf_content)
                        
            except UnicodeDecodeError:
                # 跳过无法解码的文件
                continue
            except Exception as e:
                # 跳过无法处理的PDF文件
                print(f"跳过异常文件 {file_name}: {str(e)}")
                continue
    
    return documents

def update_loaded_record(doc_dir: str = None) -> None:
    """更新已加载文件的记录"""
    doc_dir = doc_dir or DOC_DIR
    loaded = load_loaded_files()
    
    # 遍历所有文档文件并更新哈希记录
    for root, dirs, files in os.walk(doc_dir):
        for file_name in files:
            if file_name.endswith((".md", ".txt", ".pdf", ".docx", ".rst")):
                file_path = os.path.join(root, file_name)
                file_hash = get_file_hash(file_path)
                loaded[file_path] = file_hash
    
    # 保存更新后的记录
    save_loaded_files(loaded)

def clear_loaded_record() -> None:
    """清除已加载文件的记录"""
    if os.path.exists(TRACK_FILE):
        os.remove(TRACK_FILE)

def get_document_count(doc_dir: str = None) -> int:
    """获取文档目录下的文件数量"""
    doc_dir = doc_dir or DOC_DIR
    count = 0
    
    for root, dirs, files in os.walk(doc_dir):
        for file_name in files:
            if file_name.endswith((".md", ".txt", ".pdf", ".docx", ".rst")):
                count += 1
    
    return count
