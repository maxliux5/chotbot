import sys
import os
import logging
import traceback
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('./chotbot/backend.log')
    ]
)
logger = logging.getLogger(__name__)

# 添加 src 目录到 Python 导入路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi import FastAPI, HTTPException
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
logger.info("正在初始化 Chatbot...")
try:
    chatbot = Chatbot()
    logger.info("Chatbot 初始化成功")
except Exception as e:
    logger.error(f"Chatbot 初始化失败: {str(e)}")
    logger.error(traceback.format_exc())
    chatbot = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    logger.info("收到根路径请求")
    return {"status": "ok", "message": "Chotbot API is running"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """普通聊天接口"""
    logger.info(f"收到聊天请求: {request.message}")
    
    if not chatbot:
        logger.error("Chatbot 未初始化")
        return ChatResponse(response="抱歉，聊天机器人服务暂时不可用")
    
    try:
        logger.info("开始调用 chatbot.chat...")
        response = chatbot.chat(request.message, use_rag=False)  # 暂时关闭 RAG
        logger.info(f"chatbot 返回: {response}")
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"聊天处理失败: {str(e)}")
        logger.error(traceback.format_exc())
        return ChatResponse(response=f"抱歉，发生错误：{str(e)}")

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式聊天接口 - 简化版"""
    logger.info(f"收到流式聊天请求: {request.message}")
    
    if not chatbot:
        logger.error("Chatbot 未初始化")
        from fastapi.responses import StreamingResponse
        return StreamingResponse("抱歉，聊天机器人服务暂时不可用", media_type="text/plain")
    
    try:
        # 先获取完整响应
        logger.info("开始调用 chatbot.chat (流式)...")
        response = chatbot.chat(request.message, use_rag=False)
        logger.info(f"chatbot 流式返回: {response}")
        
        # 模拟流式返回（因为原始 chat_stream 可能有问题）
        async def generate():
            yield response
        
        from fastapi.responses import StreamingResponse
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        logger.error(f"流式聊天处理失败: {str(e)}")
        logger.error(traceback.format_exc())
        from fastapi.responses import StreamingResponse
        return StreamingResponse(f"错误：{str(e)}", media_type="text/plain")
