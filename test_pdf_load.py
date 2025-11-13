#!/usr/bin/env python3
"""测试PDF加载功能"""

import sys
import os
import tempfile
sys.path.insert(0, 'src')
from chotbot.utils.rag_loader import load_documents, DOC_DIR

# 创建一个临时PDF文件用于测试
test_pdf_content = '''%PDF-1.4
1 0 obj <</Type/Catalog/Pages 2 0 R>> endobj
2 0 obj <</Type/Pages/Kids [3 0 R]/Count 1/MediaBox [0 0 612 792]>> endobj
3 0 obj <</Type/Page/Parent 2 0 R/Contents 4 0 R>> endobj
4 0 obj <</Length 55>> stream
BT /F1 12 Tf 0 700 Td (测试PDF文档内容) Tj ET
endstream endobj
xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000050 00000 n 
0000000100 00000 n 
0000000150 00000 n 
trailer <</Size 5/Root 1 0 R>>
startxref
200
%%EOF
'''

# 创建临时PDF文件
temp_pdf_path = os.path.join(DOC_DIR, "test.pdf")
with open(temp_pdf_path, "w") as f:
    f.write(test_pdf_content)

# 测试加载PDF文件
print("测试PDF文件路径:", temp_pdf_path)
documents = load_documents()
print("加载的文档总数:", len(documents))
print("是否包含PDF内容:", "测试PDF文档内容" in str(documents))

# 清理临时文件
os.remove(temp_pdf_path)
print("\n✅ PDF加载功能测试完成！")
