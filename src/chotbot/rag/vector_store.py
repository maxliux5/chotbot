import numpy as np
from typing import List, Dict, Any

class SimpleVectorStore:
    """
    A simple in-memory vector store for RAG.
    """
    def __init__(self):
        self.documents = []
        self.embeddings = []
    
    def add_documents(self, documents: List[str], embeddings: List[np.ndarray]):
        """
        Add documents and their embeddings to the vector store.
        
        Args:
            documents (List[str]): List of document texts
            embeddings (List[np.ndarray]): List of embeddings
        """
        for doc, emb in zip(documents, embeddings):
            self.documents.append(doc)
            self.embeddings.append(emb)
    
    def similarity_search(self, query_embedding: np.ndarray, k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for the most similar documents to the query embedding.
        
        Args:
            query_embedding (np.ndarray): Query embedding
            k (int): Number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of results with document and score
        """
        if not self.embeddings:
            return []
        
        # Calculate cosine similarity
        embeddings = np.array(self.embeddings)
        similarities = np.dot(embeddings, query_embedding) / (
            np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top k results
        top_indices = similarities.argsort()[::-1][:k]
        
        results = []
        for idx in top_indices:
            results.append({
                "document": self.documents[idx],
                "score": float(similarities[idx])
            })
        
        return results
