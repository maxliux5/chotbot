import logging
from math import log
import re
import json
from typing import Iterator, Dict, Any
from chotbot.core.llm_client import LLMClient
from chotbot.mcp.tools.tool_manager import ToolManager

# 配置日志
logger = logging.getLogger(__name__)

class ReActAgent:
    def __init__(self, llm_client: LLMClient, tool_manager: ToolManager):
        self.llm_client = llm_client
        self.tool_manager = tool_manager

    def run(self, user_input: str, max_steps: int = 100) -> tuple[str, list]:
        """
        Run the ReAct agent with Tool Calls and return the final answer and thinking steps.
        
        Returns:
            tuple: (final_answer, thinking_steps)
            - final_answer: The final answer to the user's question
            - thinking_steps: List of dictionaries containing the thinking process
        """
        # 1. 初始化思考过程和历史记录
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the provided tools to answer the user's question. When you have the final answer, use the end_tool to complete the task."},
            {"role": "user", "content": user_input}
        ]
        
        thinking_steps = []
        all_citations = []  # 存储所有引用信息
        logger.info(f"Starting ReAct agent with user input: {user_input}")

        # 2. ReAct 循环
        for i in range(max_steps):
            logger.info(f"--- Step {i+1} ---")

            # 3. 使用Tool Calls生成响应
            tools = self.tool_manager.get_tool_definitions()
            response, tool_calls = self.llm_client.generate_with_tools(messages, tools)
            
            logger.info(f"LLM response: {response}")
            logger.info(f"Tool calls: {tool_calls}")

            # 4. 检查是否有工具调用
            if tool_calls:
                for tool_call in tool_calls:
                    # 执行工具调用
                    tool_result = self.tool_manager.execute_tool_call(tool_call)
                    logger.info(f"Tool result: {tool_result}")
                    
                    # 检查是否是end_tool（任务完成）
                    if tool_result.get("tool") == "end_tool" and tool_result.get("status") == "completed":
                        final_answer = tool_result["result"]
                        
                        # 如果有引用信息，将其添加到最终答案中
                        if all_citations:
                            final_answer += "\n\n### 引用来源：\n"
                            unique_citations = []
                            seen_hrefs = set()
                            for citation in all_citations:
                                if citation['href'] not in seen_hrefs:
                                    seen_hrefs.add(citation['href'])
                                    unique_citations.append(citation)
                            
                            for i, citation in enumerate(unique_citations, 1):
                                final_answer += f"{i}. [{citation['title']}]({citation['href']})"
                                if 'source' in citation:
                                    final_answer += f" - {citation['source']}"
                                final_answer += "\n"
                        
                        logger.info(f"Final Answer: {final_answer}")
                        
                        # 添加最终答案到思考步骤
                        thinking_steps.append({
                            "step": len(thinking_steps) + 1,
                            "type": "final_answer",
                            "content": final_answer,
                            "thought": "Final answer reached"
                        })
                        
                        return final_answer, thinking_steps
                    
                    # 如果是search工具，提取引用信息
                    if tool_result.get("tool") == "search" and tool_result.get("status") == "success":
                        result_data = tool_result.get("result", {})
                        if isinstance(result_data, dict) and 'citations' in result_data:
                            all_citations.extend(result_data['citations'])
                    
                    # 添加工具调用到思考步骤
                    # 处理tool_call对象，提取工具名和参数
                    if hasattr(tool_call, 'function'):
                        tool_name = tool_call.function.name
                        arguments = tool_call.function.arguments
                    else:
                        tool_name = tool_call["function"]["name"]
                        arguments = tool_call["function"]["arguments"]
                    
                    thinking_steps.append({
                        "step": len(thinking_steps) + 1,
                        "type": "tool_call",
                        "tool": tool_name,
                        "arguments": arguments,
                        "result": tool_result
                    })
                    
                    # 将工具结果添加到消息历史
                    messages.append({
                        "role": "assistant",
                        "tool_calls": [tool_call]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result)
                    })
            else:
                # 没有工具调用，直接返回响应作为最终答案
                final_answer = response if response else "No response generated."
                
                # 如果有引用信息，将其添加到最终答案中
                if all_citations:
                    final_answer += "\n\n### 引用来源：\n"
                    unique_citations = []
                    seen_hrefs = set()
                    for citation in all_citations:
                        if citation['href'] not in seen_hrefs:
                            seen_hrefs.add(citation['href'])
                            unique_citations.append(citation)
                    
                    for i, citation in enumerate(unique_citations, 1):
                        final_answer += f"{i}. [{citation['title']}]({citation['href']})"
                        if 'source' in citation:
                            final_answer += f" - {citation['source']}"
                        final_answer += "\n"
                
                logger.info(f"Final Answer: {final_answer}")
                
                # 添加最终答案到思考步骤
                thinking_steps.append({
                    "step": len(thinking_steps) + 1,
                    "type": "final_answer",
                    "content": final_answer,
                    "thought": "Final answer reached"
                })
                
                return final_answer, thinking_steps

        # 7. 超出最大步数，返回错误信息
        logger.warning("Max steps reached, unable to find an answer.")
        error_message = "Sorry, I couldn't find an answer after several steps."
        
        thinking_steps.append({
            "step": len(thinking_steps) + 1,
            "type": "error",
            "content": error_message,
            "thought": "Max steps reached"
        })
        
        return error_message, thinking_steps

    def run_stream(self, user_input: str, max_steps: int = 100) -> Iterator[Dict[str, Any]]:
        """
        Stream the ReAct agent's thinking process with Tool Calls.
        
        Yields:
            Dict[str, Any]: Each step of the thinking process
        """
        # 1. 初始化消息历史
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the provided tools to answer the user's question. When you have the final answer, use the end_tool to complete the task."},
            {"role": "user", "content": user_input}
        ]
        
        all_citations = []  # 存储所有引用信息
        logger.info(f"Starting ReAct agent with user input: {user_input}")

        # 2. ReAct 循环
        for i in range(max_steps):
            logger.info(f"--- Step {i+1} ---")

            # 3. 使用Tool Calls生成响应
            tools = self.tool_manager.get_tool_definitions()
            response, tool_calls = self.llm_client.generate_with_tools(messages, tools)
            
            logger.info(f"LLM response: {response}")
            logger.info(f"Tool calls: {tool_calls}")

            # 4. 检查是否有工具调用
            if tool_calls:
                for tool_call in tool_calls:
                    # 执行工具调用
                    tool_result = self.tool_manager.execute_tool_call(tool_call)
                    logger.info(f"Tool result: {tool_result}")
                    
                    # 检查是否是end_tool（任务完成）
                    if tool_result.get("tool") == "end_tool" and tool_result.get("status") == "completed":
                        final_answer = tool_result["result"]
                        
                        # 如果有引用信息，将其添加到最终答案中
                        if all_citations:
                            final_answer += "\n\n### 引用来源：\n"
                            unique_citations = []
                            seen_hrefs = set()
                            for citation in all_citations:
                                if citation['href'] not in seen_hrefs:
                                    seen_hrefs.add(citation['href'])
                                    unique_citations.append(citation)
                            
                            for i, citation in enumerate(unique_citations, 1):
                                final_answer += f"{i}. [{citation['title']}]({citation['href']})"
                                if 'source' in citation:
                                    final_answer += f" - {citation['source']}"
                                final_answer += "\n"
                        
                        logger.info(f"Final Answer: {final_answer}")
                        
                        # 发送最终答案
                        yield {
                            "type": "final_answer",
                            "step": i + 1,
                            "content": final_answer
                        }
                        
                        return
                    
                    # 如果是search工具，提取引用信息
                    if tool_result.get("tool") == "search" and tool_result.get("status") == "success":
                        result_data = tool_result.get("result", {})
                        if isinstance(result_data, dict) and 'citations' in result_data:
                            all_citations.extend(result_data['citations'])
                    
                    # 发送工具调用步骤
                    yield {
                        "type": "tool_call",
                        "step": i + 1,
                        "tool": tool_call["function"]["name"],
                        "arguments": tool_call["function"]["arguments"],
                        "result": tool_result
                    }
                    
                    # 将工具结果添加到消息历史
                    messages.append({
                        "role": "assistant",
                        "tool_calls": [tool_call]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result)
                    })
            else:
                # 没有工具调用，直接返回响应作为最终答案
                final_answer = response if response else "No response generated."
                
                # 如果有引用信息，将其添加到最终答案中
                if all_citations:
                    final_answer += "\n\n### 引用来源：\n"
                    unique_citations = []
                    seen_hrefs = set()
                    for citation in all_citations:
                        if citation['href'] not in seen_hrefs:
                            seen_hrefs.add(citation['href'])
                            unique_citations.append(citation)
                    
                    for i, citation in enumerate(unique_citations, 1):
                        final_answer += f"{i}. [{citation['title']}]({citation['href']})"
                        if 'source' in citation:
                            final_answer += f" - {citation['source']}"
                        final_answer += "\n"
                
                logger.info(f"Final Answer: {final_answer}")
                
                # 发送最终答案
                yield {
                    "type": "final_answer",
                    "step": i + 1,
                    "content": final_answer
                }
                
                return

        # 5. 超出最大步数，发送错误信息
        logger.warning("Max steps reached, unable to find an answer.")
        yield {
            "type": "error",
            "step": max_steps,
            "content": "Sorry, I couldn't find an answer after several steps."
        }

    def _execute_action(self, action: str) -> str:
        """Legacy method - no longer used with Tool Calls"""
        logger.warning("_execute_action is deprecated. Use Tool Calls instead.")
        return "Deprecated method"
