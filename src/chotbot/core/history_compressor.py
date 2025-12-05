import logging
from typing import List, Dict, Any, Optional
from chotbot.core.llm_client import LLMClient

logger = logging.getLogger(__name__)


class HistoryCompressor:
    """
    History compression using LLM to summarize and compress conversation history.
    This helps manage long conversations by reducing token usage while retaining
    important information.
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        
    def compress(
        self, 
        history: List[Dict[str, Any]], 
        strategy: str = "summary",
        keep_last_n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Compress conversation history using specified strategy.
        
        Args:
            history: Full conversation history
            strategy: Compression strategy ("summary", "extract_key_info", "hybrid")
            keep_last_n: Number of recent messages to keep uncompressed
            
        Returns:
            Compressed history
        """
        if len(history) <= keep_last_n + 2:
            logger.info("History too short for compression, skipping")
            return history
        
        # Separate recent messages that will be kept as-is
        recent_messages = history[-keep_last_n:]
        old_messages = history[:-keep_last_n]
        
        if not old_messages:
            return history
        
        logger.info(f"Compressing {len(old_messages)} old messages using {strategy} strategy")
        
        # Compress old messages based on strategy
        if strategy == "summary":
            compressed = self._compress_by_summary(old_messages)
        elif strategy == "extract_key_info":
            compressed = self._compress_by_extraction(old_messages)
        elif strategy == "hybrid":
            compressed = self._compress_hybrid(old_messages)
        else:
            raise ValueError(f"Unknown compression strategy: {strategy}")
        
        # Combine compressed old messages with recent messages
        result = compressed + recent_messages
        
        logger.info(f"Compression reduced history from {len(history)} to {len(result)} messages")
        
        return result
    
    def _compress_by_summary(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Compress by generating a comprehensive summary of old conversations.
        """
        # Format messages for LLM
        conversation_text = self._format_conversation(messages)
        
        # Create summary prompt
        prompt = f"""Please summarize the following conversation comprehensively. 
Extract the key topics discussed, important decisions made, and any relevant context 
that would be important for continuing this conversation.

Conversation:
{conversation_text}

Provide a concise but comprehensive summary:"""
        
        try:
            summary = self.llm_client.generate([
                {"role": "user", "content": prompt}
            ])
            
            # Return as a single system message containing the summary
            return [{
                "role": "system",
                "content": f"[History Summary] {summary}",
                "compressed": True,
                "original_count": len(messages)
            }]
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            # Fallback: return truncated history
            return messages[:3] if len(messages) > 3 else messages
    
    def _compress_by_extraction(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Compress by extracting only key information (facts, decisions, preferences).
        """
        conversation_text = self._format_conversation(messages)
        
        prompt = f"""Analyze the following conversation and extract only the key information 
that would be essential for continuing the conversation. Focus on:
1. Important facts or data mentioned
2. Decisions that were made
3. User preferences or constraints
4. Action items or next steps

Conversation:
{conversation_text}

Extract only the essential information in a concise format:"""
        
        try:
            key_info = self.llm_client.generate([
                {"role": "user", "content": prompt}
            ])
            
            return [{
                "role": "system",
                "content": f"[Key Information] {key_info}",
                "compressed": True,
                "original_count": len(messages),
                "strategy": "extraction"
            }]
            
        except Exception as e:
            logger.error(f"Failed to extract key info: {e}")
            return messages[:2] if len(messages) > 2 else messages
    
    def _compress_hybrid(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Hybrid approach: both summary and key information extraction.
        """
        conversation_text = self._format_conversation(messages)
        
        prompt = f"""Please analyze the following conversation and provide:
1. A brief summary of what was discussed
2. Key facts, decisions, and important details that should be remembered

Conversation:
{conversation_text}

Provide your analysis in a structured format:"""
        
        try:
            analysis = self.llm_client.generate([
                {"role": "user", "content": prompt}
            ])
            
            return [{
                "role": "system",
                "content": f"[Conversation Analysis] {analysis}",
                "compressed": True,
                "original_count": len(messages),
                "strategy": "hybrid"
            }]
            
        except Exception as e:
            logger.error(f"Failed hybrid compression: {e}")
            return self._compress_by_summary(messages)
    
    def _format_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Format conversation history as text for LLM processing."""
        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)
    
    def should_compress(
        self, 
        history: List[Dict[str, Any]], 
        threshold_messages: int = 15,
        threshold_tokens: Optional[int] = None
    ) -> bool:
        """
        Determine if compression is needed based on history size.
        
        Args:
            history: Current conversation history
            threshold_messages: Compress when exceeding this many messages
            threshold_tokens: Compress when exceeding this many tokens (optional)
            
        Returns:
            True if compression is recommended
        """
        if len(history) < threshold_messages:
            return False
        
        if threshold_tokens:
            # Estimate token count
            total_chars = sum(len(msg.get("content", "")) for msg in history)
            estimated_tokens = total_chars // 4
            if estimated_tokens > threshold_tokens:
                return True
        
        return len(history) >= threshold_messages
    
    def incremental_compress(
        self, 
        history: List[Dict[str, Any]],
        chunk_size: int = 10,
        strategy: str = "summary"
    ) -> List[Dict[str, Any]]:
        """
        Incrementally compress history in chunks to maintain more details
        while still reducing token usage.
        
        Args:
            history: Full conversation history
            chunk_size: Number of messages per chunk for compression
            strategy: Compression strategy to use
            
        Returns:
            Incrementally compressed history
        """
        if len(history) <= chunk_size + 3:
            return history
        
        # Keep recent messages uncompressed
        recent_messages = history[-3:]
        old_messages = history[:-3]
        
        # Compress old messages in chunks
        compressed_chunks = []
        for i in range(0, len(old_messages), chunk_size):
            chunk = old_messages[i:i + chunk_size]
            if len(chunk) > 2:
                compressed_chunk = self._compress_by_summary(chunk)
                compressed_chunks.extend(compressed_chunk)
            else:
                compressed_chunks.extend(chunk)
        
        return compressed_chunks + recent_messages

    def extract_user_profile(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract user profile from conversation history.

        Args:
            messages: Conversation history

        Returns:
            A dictionary containing the user's profile
        """
        conversation_text = self._format_conversation(messages)

        prompt = f"""
        Based on the following conversation, please extract a user profile.
        The profile should be in JSON format and include the following fields:
        - basic_info: name, gender, age, location, occupation
        - interests: hobbies, topics of interest
        - behavior_patterns: communication style, preference for detail, decision-making habits
        - potential_needs: potential needs or problems to be solved

        Conversation:
        {conversation_text}

        Please provide the user profile in JSON format:
        """

        try:
            profile_str = self.llm_client.generate([
                {"role": "user", "content": prompt}
            ])
            # Ensure the output is a valid JSON
            return json.loads(profile_str)
        except Exception as e:
            logger.error(f"Failed to extract user profile: {e}")
            return {}


class CompressedHistoryManager:
    """
    Manager that integrates compression with history management.
    """
    
    def __init__(self, llm_client: LLMClient, compressor: HistoryCompressor = None):
        self.llm_client = llm_client
        self.compressor = compressor or HistoryCompressor(llm_client)
        self.compression_history = []
    
    def add_message(self, message: Dict[str, Any]):
        """Add a message and track compression events."""
        # This would be called by the context manager
        pass
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get statistics about compression operations."""
        return {
            "total_compressions": len(self.compression_history),
            "compression_events": self.compression_history
        }
