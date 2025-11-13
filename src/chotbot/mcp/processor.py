from chotbot.mcp.context_manager import MCPContextManager
from chotbot.core.llm_client import LLMClient

class MCPProcessor:
    """
    MCP (Model Context Protocol) processor that handles context-aware interactions.
    """
    def __init__(self, llm_client: LLMClient):
        self.context_manager = MCPContextManager()
        self.llm_client = llm_client
    
    def interact(self, user_input: str, system_prompt: str = None) -> str:
        """
        Process a user input with context management.
        
        Args:
            user_input (str): User's input message
            system_prompt (str): Optional system prompt
            
        Returns:
            str: Generated response
        """
        # Add user message to context
        self.context_manager.add_message("user", user_input)
        
        # Build messages for LLM
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add context history
        messages.extend(self.context_manager.get_context())
        
        # Generate response
        response = self.llm_client.generate(messages)
        
        # Add assistant response to context
        self.context_manager.add_message("assistant", response)
        
        return response
    
    def clear_context(self):
        """
        Clear the current context history.
        """
        self.context_manager.clear()
    
    def get_context(self) -> list:
        """
        Get the current context.
        
        Returns:
            list: Current context messages
        """
        return self.context_manager.get_context()
