import logging
import pandas as pd
from datetime import datetime
from math import log
import re
import json
from typing import Iterator, Dict, Any
from chotbot.core.llm_client import LLMClient
from chotbot.mcp.tools.tool_manager import ToolManager

# 配置日志
logger = logging.getLogger(__name__)

class ReActAgent:
    def __init__(self, llm_client: LLMClient, tool_manager: ToolManager, history_compressor: "HistoryCompressor" = None, rag_manager: "RAGManager" = None):
        self.llm_client = llm_client
        self.tool_manager = tool_manager
        self.history_compressor = history_compressor
        self.rag_manager = rag_manager
        self.history = []

    def run(self, user_input: str, max_steps: int = 100, user_id: str = None) -> tuple[str, list]:
        """
        Run the ReAct agent with Tool Calls and return the final answer and thinking steps.
        
        Returns:
            tuple: (final_answer, thinking_steps)
            - final_answer: The final answer to the user's question
            - thinking_steps: List of dictionaries containing the thinking process
        """
        # 0. 添加用户画像
        profile_prompt = ""
        if self.rag_manager and user_id:
            profile = self.rag_manager.query(f"user_profile_{user_id}")
            if profile:
                profile_prompt = f"The user's profile is as follows: {profile}. Please refer to this information to provide a more personalized and accurate answer."
        # 1. 初始化思考过程和历史记录
        current_time = datetime.now().strftime("%Y-%m-%d")
        system_prompt_content = f"""You are a helpful assistant.

**IMPORTANT INSTRUCTIONS:**
1.  **The current date is {current_time}.** You MUST use this date for any calculations related to age or time. DO NOT use your internal knowledge about the date.
2.  For questions about current facts or events (e.g., "who is the current president", "what is the latest news"), you MUST use the `search` tool to get real-time information. Your internal knowledge is outdated.
3.  {profile_prompt}

Use the provided tools to answer the user's question. When you have the final answer, use the `end_tool` to complete the task.
"""
        # 1. 生成计划
        plan_prompt = f"""Please create a step-by-step plan to answer the following user query. The user query is: {user_input}"""
        plan_messages = [
            {"role": "system", "content": system_prompt_content.strip()},
            {"role": "user", "content": plan_prompt}
        ]
        plan, _ = self.llm_client.generate_with_tools(plan_messages, [])
        
        yield {
            "type": "plan",
            "content": plan
        }

        # 2. 执行计划
        messages = [
            {"role": "system", "content": system_prompt_content.strip()},
            {"role": "user", "content": user_input}
        ]

        # 1. 初始化
        self.history.clear()
        self.history.append({"role": "user", "content": user_input})
        messages.extend(self.history)

        yield {
            "type": "thought",
            "step": 0,
            "content": "我正在思考如何回答你的问题..."
        }

        for i in range(max_steps):
            # 2. 调用LLM
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
                        final_answer = tool_result.get("result", "")
                        model_citations = tool_result.get("citations", [])
                        
                        # 使用大模型自己提供的引用来源
                        if model_citations:
                            final_answer += "\n\n### 引用来源：\n"
                            for i, citation in enumerate(model_citations, 1):
                                final_answer += f"{i}. [{citation.get('title', '')}]({citation.get('url', '')})\n"
                        
                        logger.info(f"Final Answer: {final_answer}")
                        
                        # 添加最终答案到思考步骤
                        thinking_steps.append({
                            "step": len(thinking_steps) + 1,
                            "type": "final_answer",
                            "content": final_answer,
                            "thought": "Final answer reached"
                        })
                        
                        # 保存聊天记录和用户画像
                        self.history.append(messages)
                        if user_id:
                            with open(f"history/{user_id}_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.json", "w") as f:
                                json.dump(self.history, f, indent=4)
                        if self.history_compressor and len(self.history) % 5 == 0:
                            user_profile = self.history_compressor.extract_user_profile(self.history)
                            if user_profile and self.rag_manager:
                                self.rag_manager.add_documents([f"user_profile_{user_id}: {json.dumps(user_profile)}"])

                        return final_answer, thinking_steps
                    
                    
                    # 添加工具调用到思考步骤
                    # 处理tool_call对象，提取工具名和参数
                    # ChatCompletionMessageFunctionToolCall对象有function属性
                    tool_name = tool_call.function.name
                    arguments = tool_call.function.arguments
                    
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
                
                # 发送最终答案
                yield {
                    "type": "final_answer",
                    "step": i + 1,
                    "content": final_answer
                }
                
                return

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

           # 0. 添加用户画像
        profile_prompt = ""
        if self.rag_manager:
            profile = self.rag_manager.query(f"user_profile")
            if profile:
                profile_prompt = f"The user's profile is as follows: {profile}. Please refer to this information to provide a more personalized and accurate answer."
        
        current_time = datetime.now().strftime("%Y-%m-%d")
        system_prompt_content = f"""You are a helpful assistant.

**IMPORTANT INSTRUCTIONS:**
1.  **The current date is {current_time}.** You MUST use this date for any calculations related to age or time. DO NOT use your internal knowledge about the date.
2.  For questions about current facts or events (e.g., "who is the current president", "what is the latest news"), you MUST use the `search` tool to get real-time information. Your internal knowledge is outdated.
3.  {profile_prompt}

Use the provided tools to answer the user's question. When you have the final answer, use the `end_tool` to complete the task.
"""
        # 1. 生成计划
        plan_prompt = f"""Please create a step-by-step plan to answer the following user query. The user query is: {user_input}"""
        plan_messages = [
            {"role": "system", "content": system_prompt_content.strip()},
            {"role": "user", "content": plan_prompt}
        ]
        plan, _ = self.llm_client.generate_with_tools(plan_messages, [])
        
        yield {
            "type": "plan",
            "content": plan
        }

        # 2. 执行计划
        messages = [
            {"role": "system", "content": system_prompt_content.strip()},
            {"role": "user", "content": user_input}
        ]

        # 1. 初始化
        self.history.clear()
        self.history.append({"role": "user", "content": user_input})
        messages.extend(self.history)

        yield {
            "type": "thought",
            "step": 0,
            "content": "我正在思考如何回答你的问题..."
        }

        for i in range(max_steps):
            # 2. 调用LLM
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
                        final_answer = tool_result.get("result", "")
                        model_citations = tool_result.get("citations", [])
                        
                        # 使用大模型自己提供的引用来源
                        if model_citations:
                            final_answer += "\n\n### 引用来源：\n"
                            for i, citation in enumerate(model_citations, 1):
                                final_answer += f"{i}. [{citation.get('title', '')}]({citation.get('url', '')})\n"
                        
                        logger.info(f"Final Answer: {final_answer}")
                        
                        # 发送最终答案
                        yield {
                            "type": "final_answer",
                            "step": i + 1,
                            "content": final_answer
                        }
                        
                        return
                    
                    
                    # 改造返回给前端的数据结构
                    yield {
                        "type": "step",
                        "step": i + 1,
                        "thought": response,  # LLM的思考过程
                        "action": f"{tool_call.function.name}({tool_call.function.arguments})",
                        "observation": json.dumps(tool_result, ensure_ascii=False)
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
