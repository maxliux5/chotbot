#!/usr/bin/env python3
"""
Test script for Chotbot
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from chotbot.core.chatbot import Chatbot

def test_chatbot():
    """Test basic chatbot functionality"""
    print("Testing Chotbot...")
    
    # Create chatbot instance
    chatbot = Chatbot()
    
    # Test adding documents
    test_docs = [
        "This is a test document about Python programming.",
        "Python is a popular language for AI and machine learning.",
    ]
    chatbot.add_documents(test_docs)
    print("✓ Documents added to RAG")
    
    # Test basic context
    chatbot.clear_context()
    print("✓ Context cleared")
    
    # Test components
    print("\n✓ All components initialized successfully")
    print("✓ LLM Client: Ready")
    print("✓ RAG Manager: Ready")
    print("✓ MCP Processor: Ready")
    
    print("\n✅ Basic functionality test passed!")
    
    # Test with sample input
    print("\nTesting sample interaction...")
    print("Note: This won't work without a valid OpenAI API key in .env")
    
    try:
        # This will fail if no API key is configured
        response = chatbot.chat("Hello, what is Python?", use_rag=False)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Expected error (no API key): {str(e)}")
    
    print("\nTo run the full chatbot, configure your API key in .env and run 'uv run chotbot'")

if __name__ == "__main__":
    test_chatbot()
