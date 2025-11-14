import sys
import os
# 添加 src 目录到 Python 导入路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chotbot.core.chatbot import Chatbot

app = FastAPI(title="Chotbot API", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化聊天机器人（关闭 RAG，因为 faiss 未安装）
chatbot = Chatbot()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    return {"status": "ok", "message": "Chotbot API is running"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """普通聊天接口"""
    try:
        response = chatbot.chat(request.message, use_rag=False)  # 暂时关闭 RAG
        return ChatResponse(response=response)
    except Exception as e:
        return ChatResponse(response=f"抱歉，发生错误：{str(e)}")

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式聊天接口 - 简化版"""
    try:
        # 先获取完整响应
        response = chatbot.chat(request.message, use_rag=False)
        
        # 模拟流式返回（因为原始 chat_stream 可能有问题）
        async def generate():
            yield response
        
        from fastapi.responses import StreamingResponse
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        from fastapi.responses import StreamingResponse
        return StreamingResponse(f"错误：{str(e)}", media_type="text/plain")
