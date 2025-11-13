from typing import List, Dict, Any
from chotbot.utils.config import Config

class MCPContextManager:
    """
    Model Context Protocol (MCP) manager for handling chat context.
    
    This implementation manages the chat history and context window
    to ensure efficient use of the model's context limit.
    """
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.max_context_size = Config.MCP_MAX_CONTEXT_SIZE
        self.history_limit = Config.MCP_HISTORY_LIMIT
    
    def add_message(self, role: str, content: str):
        """
        Add a message to the context history.
        
        Args:
            role (str): Role of the message (user, assistant, system)
            content (str): Content of the message
        """
        message = {
            "role": role,
            "content": content
        }
        self.history.append(message)
        
        # Limit the history to the configured limit
        if len(self.history) > self.history_limit:
            self.history = self.history[-self.history_limit:]
    
    def get_context(self, max_tokens: int = None) -> List[Dict[str, Any]]:
        """
        Get the context messages within the token limit.
        
        Args:
            max_tokens (int): Maximum number of tokens allowed (default: MCP_MAX_CONTEXT_SIZE)
            
        Returns:
            List[Dict[str, Any]]: Context messages
        """
        max_tokens = max_tokens or self.max_context_size
        
        # Simple token count estimation (1 token ~ 4 chars)
        def estimate_tokens(text: str) -> int:
            return len(text) // 4
        
        # Build context from the end
        context = []
        total_tokens = 0
        
        for message in reversed(self.history):
            message_tokens = estimate_tokens(message["content"])
            if total_tokens + message_tokens > max_tokens:
                break
            
            context.insert(0, message)
            total_tokens += message_tokens
        
        return context
    
    def clear(self):
        """
        Clear the context history.
        """
        self.history = []
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the full history.
        
        Returns:
            List[Dict[str, Any]]: Full context history
        """
        return self.history.copy()
    
    def get_history_count(self) -> int:
        """
        Get the number of messages in the history.
        
        Returns:
            int: Number of messages
        """
        return len(self.history)
