import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from chotbot.core.chatbot import Chatbot

app = FastAPI(title="Chotbot API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot = Chatbot()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "Chotbot Backend API"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        response = chatbot.chat(request.message, use_rag=False)  # 暂时关闭 RAG
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
