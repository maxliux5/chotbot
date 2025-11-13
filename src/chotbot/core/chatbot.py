from chotbot.core.llm_client import LLMClient
from chotbot.rag.rag_manager import RAGManager
from chotbot.mcp.processor import MCPProcessor

class Chatbot:
    """
    Main Chatbot class that integrates LLM, RAG, and MCP.
    """
    def __init__(self):
        self.llm_client = LLMClient()
        self.rag_manager = RAGManager(self.llm_client)
        self.mcp_processor = MCPProcessor(self.llm_client)
    
    def add_documents(self, documents: list):
        """
        Add documents to the RAG system.
        
        Args:
            documents (list): List of document texts
        """
        self.rag_manager.add_documents(documents)
    
    def chat(self, user_input: str, use_rag: bool = True, system_prompt: str = None) -> str:
        """
        Process a user input and generate a response.
        
        Args:
            user_input (str): User's input message
            use_rag (bool): Whether to use RAG for retrieval
            system_prompt (str): Optional system prompt
            
        Returns:
            str: Generated response
        """
        if use_rag:
            # Use RAG for response generation
            response = self.rag_manager.query(user_input)
            # Add to MCP context
            self.mcp_processor.context_manager.add_message("user", user_input)
            self.mcp_processor.context_manager.add_message("assistant", response)
            return response
        else:
            # Use MCP for context-aware generation
            return self.mcp_processor.interact(user_input, system_prompt=system_prompt)
    
    def clear_context(self):
        """
        Clear the chat context.
        """
        self.mcp_processor.clear_context()
    
    def get_context(self) -> list:
        """
        Get the current chat context.
        
        Returns:
            list: Current context messages
        """
        return self.mcp_processor.get_context()
