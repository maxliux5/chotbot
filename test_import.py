import sys
import os

# 把 src 目录加入 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
print('Python 路径:', sys.path)

try:
    from chotbot.core.chatbot import Chatbot
    print('✅ Chatbot 导入成功')
except Exception as e:
    print('❌ Chatbot 导入失败:', e)
    import traceback
    traceback.print_exc()
