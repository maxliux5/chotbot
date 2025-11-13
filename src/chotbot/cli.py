#!/usr/bin/env python3
"""
Chatbot Console Interface
"""

import sys
from chotbot.core.chatbot import Chatbot

def main():
    print("=================================")
    print("    Chotbot - Console Version    ")
    print("=================================")
    print("Type 'exit' to quit")
    print("Type 'clear' to clear context")
    print("Type 'rag on/off' to toggle RAG")
    print("=================================")
    
    # Initialize chatbot
    chatbot = Chatbot()
    
    # Add some sample documents for RAG
    sample_docs = [
        "Python是一种广泛使用的高级编程语言，由Guido van Rossum于1989年发明，第一个公开发行版发行于1991年。",
        "Python的设计哲学强调代码的可读性和简洁性，其语法允许程序员用更少的代码行表达想法。",
        "Python支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。",
        "Python的标准库非常庞大，提供了广泛的功能，包括字符串处理、网络编程、文件操作等。",
        "Python解释器易于扩展，可以使用C或C++（或其他可以通过C调用的语言）扩展新的功能和数据类型。"
    ]
    chatbot.add_documents(sample_docs)
    
    print("\nLoaded sample documents about Python for RAG demonstration.")
    print("=================================")
    
    use_rag = True
    
    while True:
        try:
            user_input = input("\nUser: ")
            
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            elif user_input.lower() == "clear":
                chatbot.clear_context()
                print("Context cleared.")
                continue
            elif user_input.lower().startswith("rag "):
                rag_cmd = user_input.split()[1].lower()
                if rag_cmd == "on":
                    use_rag = True
                    print("RAG enabled.")
                elif rag_cmd == "off":
                    use_rag = False
                    print("RAG disabled.")
                else:
                    print("Unknown RAG command. Use 'rag on' or 'rag off'.")
                continue
            
            # Process the input
            response = chatbot.chat(user_input, use_rag=use_rag)
            
            print(f"\nAssistant: {response}")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please check your configuration and try again.")
            print("-" * 50)

if __name__ == "__main__":
    main()
