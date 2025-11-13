from chotbot.rag.vector_store import SimpleVectorStore
from chotbot.utils.config import Config

class RAGRetriever:
    def __init__(self, vector_store: SimpleVectorStore):
        self.vector_store = vector_store
        self.top_k = Config.RAG_TOP_K
    
    def retrieve(self, query_embedding: any, k: int = None) -> list:
        """
        Retrieve relevant documents based on the query embedding.
        
        Args:
            query_embedding: Embedding of the query
            k: Number of documents to retrieve
            
        Returns:
            list: List of relevant documents
        """
        k = k or self.top_k
        results = self.vector_store.similarity_search(query_embedding, k=k)
        return [result["document"] for result in results]
