from chotbot.core.llm_client import LLMClient

class RAGGenerator:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def generate(self, query: str, context_docs: list) -> str:
        """
        Generate a response using RAG (Retrieval-Augmented Generation).
        
        Args:
            query (str): User query
            context_docs (list): Relevant documents from retrieval
            
        Returns:
            str: Generated response
        """
        if not context_docs:
            # Fallback to normal LLM generation if no context
            return self.llm_client.generate([
                {"role": "user", "content": query}
            ])
        
        # Construct prompt with context
        context = "\n\n".join(context_docs)
        prompt = f"""
You are an assistant who answers questions based on the given context.
Context:
{context}

Question: {query}

Please answer the question using only the information from the context. If you cannot answer the question from the context, please say "I don't have enough information to answer that question."
"""
        
        return self.llm_client.generate([
            {"role": "user", "content": prompt}
        ])
