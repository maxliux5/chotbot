#!/usr/bin/env python3
"""调试PDF加载"""

import sys
import os
import tempfile
sys.path.insert(0, 'src')

# 直接测试PyPDF2的功能
from PyPDF2 import PdfReader

# 创建一个真实的PDF文件
test_pdf_path = os.path.join('doc', 'test_debug.pdf')

# 使用reportlab创建真实PDF
from reportlab.pdfgen import canvas
c = canvas.Canvas(test_pdf_path)
c.setFont('Helvetica', 12)
c.drawString(100, 750, '测试真实PDF文档')
c.drawString(100, 730, '这是PDF的第二行内容')
c.drawString(100, 710, '第三行：用于测试PDF加载功能')
c.save()

print('PDF文件路径:', test_pdf_path)
print('文件大小:', os.path.getsize(test_pdf_path), 'bytes')

# 测试PyPDF2读取
try:
    pdf_reader = PdfReader(test_pdf_path)
    print('PDF页数:', len(pdf_reader.pages))
    
    for i, page in enumerate(pdf_reader.pages):
        print(f'\n第{i+1}页内容:')
        content = page.extract_text()
        print(f'内容长度: {len(content)}')
        print(f'内容: "{content}"')
        print(f'是否为空: {content.strip() == ""}')
        
except Exception as e:
    print('错误:', type(e).__name__, str(e))
    import traceback
    traceback.print_exc()

# 清理
os.remove(test_pdf_path)
