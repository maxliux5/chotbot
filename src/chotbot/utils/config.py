import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # LLM Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_v1")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Deepseek Embedding Configuration
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_EMBEDDING_MODEL = os.getenv("DEEPSEEK_EMBEDDING_MODEL", "deepseek-chat")
    
    # RAG Configuration
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
    RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
    RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "100"))
    
    # MCP Configuration
    MCP_MAX_CONTEXT_SIZE = int(os.getenv("MCP_MAX_CONTEXT_SIZE", "4096"))
    MCP_HISTORY_LIMIT = int(os.getenv("MCP_HISTORY_LIMIT", "10"))
