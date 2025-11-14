from openai import OpenAI
from chotbot.utils.config import Config

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_BASE_URL
        )
      
    
    def generate(self, messages: list, **kwargs):
        """
        Generate a response from the LLM.
        
        Args:
            messages (list): List of messages in OpenAI format
            **kwargs: Additional parameters for the API call
            
        Returns:
            str: Generated response
        """
        try:
            response = self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=messages,
                temperature=Config.TEMPERATURE,
                **kwargs
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"LLM API error: {str(e)}")
    
    def generate_stream(self, messages: list, **kwargs):
        """
        Generate a streaming response from the LLM.
        
        Args:
            messages (list): List of messages in OpenAI format
            **kwargs: Additional parameters for the API call
            
        Yields:
            str: Chunks of the generated response
        """
        try:
            stream = self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=messages,
                temperature=Config.TEMPERATURE,
                stream=True,
                **kwargs
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise RuntimeError(f"LLM API error: {str(e)}")
