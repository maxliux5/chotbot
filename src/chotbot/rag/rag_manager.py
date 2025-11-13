from chotbot.rag.vector_store import SimpleVectorStore
from chotbot.rag.retriever import RAGRetriever
from chotbot.rag.generator import RAGGenerator
from chotbot.core.llm_client import LLMClient
from chotbot.utils.config import Config
from chotbot.utils.rag_loader import load_documents, update_loaded_record, DOC_DIR
from sentence_transformers import SentenceTransformer  # 引入本地Embedding模型

class RAGManager:
    def __init__(self, llm_client: LLMClient = None, auto_load: bool = True):
        self.vector_store = SimpleVectorStore()
        self.llm_client = llm_client or LLMClient()
        self.retriever = RAGRetriever(self.vector_store)
        self.generator = RAGGenerator(self.llm_client)
        
        # 初始化本地Embedding模型（首次运行自动下载，后续本地使用）
        # 模型：all-MiniLM-L6-v2 - 轻量高效，支持中文，体积~40MB
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 自动加载doc目录的文件
        if auto_load:
            self.auto_load_documents()
    
    def auto_load_documents(self):
        """自动加载doc目录的文件"""
        try:
            documents = load_documents()
            if documents:
                self.add_documents(documents)
                # 更新已加载文件的记录
                update_loaded_record()
        except Exception as e:
            print(f"自动加载文档失败: {str(e)}")
    
    def add_documents(self, documents: list):
        """
        Add documents to the RAG system.
        
        Args:
            documents (list): List of document texts
        """
        # For simplicity, we're using a dummy embedding generator
        # In production, you should use a real embedding model like OpenAI's text-embedding-3-small
        embeddings = [self._get_real_embedding(doc) for doc in documents]
        self.vector_store.add_documents(documents, embeddings)
    
    def query(self, query: str) -> str:
        """
        Process a query using RAG.
        
        Args:
            query (str): User query
            
        Returns:
            str: Generated response
        """
        # Generate dummy embedding for the query
        query_embedding = self._get_real_embedding(query)
        
        # Retrieve relevant documents
        context_docs = self.retriever.retrieve(query_embedding)
        
        # Generate response
        return self.generator.generate(query, context_docs)
    
    def _get_real_embedding(self, text: str) -> list:
        """
        使用本地模型生成向量嵌入（无网络请求，完全免费）
        
        Args:
            text (str): 输入文本
            
        Returns:
            list: 向量嵌入
        """
        try:
            # 本地生成Embedding
            embedding = self.embedding_model.encode(text, convert_to_numpy=True).tolist()
            return embedding
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"本地Embedding生成错误: {repr(e)}")
