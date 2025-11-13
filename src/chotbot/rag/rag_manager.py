from chotbot.rag.vector_store import SimpleVectorStore
from chotbot.rag.retriever import RAGRetriever
from chotbot.rag.generator import RAGGenerator
from chotbot.core.llm_client import LLMClient
from chotbot.utils.config import Config

class RAGManager:
    def __init__(self, llm_client: LLMClient = None):
        self.vector_store = SimpleVectorStore()
        self.llm_client = llm_client or LLMClient()
        self.retriever = RAGRetriever(self.vector_store)
        self.generator = RAGGenerator(self.llm_client)
    
    def add_documents(self, documents: list):
        """
        Add documents to the RAG system.
        
        Args:
            documents (list): List of document texts
        """
        # For simplicity, we're using a dummy embedding generator
        # In production, you should use a real embedding model like OpenAI's text-embedding-3-small
        embeddings = [self._dummy_embedding(doc) for doc in documents]
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
        query_embedding = self._dummy_embedding(query)
        
        # Retrieve relevant documents
        context_docs = self.retriever.retrieve(query_embedding)
        
        # Generate response
        return self.generator.generate(query, context_docs)
    
    def _dummy_embedding(self, text: str) -> list:
        """
        Dummy embedding generator for demonstration purposes.
        
        Args:
            text (str): Input text
            
        Returns:
            list: Dummy embedding
        """
        # Simple hash-based embedding for demonstration
        import hashlib
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return [float(hash_val % 1000) / 1000.0 for _ in range(128)]
