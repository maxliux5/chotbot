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
        Run the ReAct agent and return the final answer and thinking steps.
        
        Returns:
            tuple: (final_answer, thinking_steps)
            - final_answer: The final answer to the user's question
            - thinking_steps: List of dictionaries containing the thinking process
        """
        # 1. 初始化思考过程和历史记录
        thought = (
            f"I need to answer the following question: {user_input}. "
            f"I should use the tools available to find the answer. "
            f"The available tools are: {self.tool_manager.get_tool_list()}. "
            f"I will start by thinking about which tool to use."
        )
        history = []
        thinking_steps = []
        all_citations = []  # 存储所有引用信息
        logger.info(f"Initial thought: {thought}")

        # 2. ReAct 循环
        for i in range(max_steps):
            logger.info(f"--- Step {i+1} ---")

            # 3. 生成行动（Action）
            prompt = f"""Thought: {thought}

请按照以下要求执行：
1. 尽可能使用提供的工具获取信息来回答问题
2. 最终答案中必须包含使用工具获取的引用来源
3. 工具使用格式：[工具名[参数]]，例如 search[北京天气]

Action: """
            action = self.llm_client.generate([{"role": "user", "content": prompt}])
            logger.info(f"Action: {action}")

            # 4. 检查是否得出最终答案
            if "Final Answer:" in action:
                final_answer = action.split("Final Answer:")[-1].strip()
                
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

            # 5. 执行行动并获取观察结果
            observation = self._execute_action(action)
            logger.info(f"Observation: {observation}")

            # 提取引用信息（如果有）
            step_citations = []
            try:
                import json
                # 尝试解析observation为JSON对象
                if isinstance(observation, str) and (observation.startswith('{') or observation.startswith('[')):
                    obs_data = json.loads(observation)
                    if isinstance(obs_data, dict) and 'citations' in obs_data:
                        step_citations = obs_data['citations']
                        logger.info(f"Extracted citations: {step_citations}")
                        all_citations.extend(step_citations)
            except:
                # 如果解析失败，忽略
                pass

            # 6. 更新历史和思考过程
            history.append(f"Thought: {thought}")
            history.append(f"Action: {action}")
            history.append(f"Observation: {observation}")
            
            # 添加当前步骤到思考步骤列表
            thinking_steps.append({
                "step": len(thinking_steps) + 1,
                "type": "action",
                "thought": thought,
                "action": action,
                "observation": observation
            })

            history_str = "\n".join(history)
            thought = (
                f"""Based on the history, I need to decide the next step. 
If I have the answer, I will output 'Final Answer:'. 
Otherwise, I will choose another action.

History:
{history_str}"""
            )

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
        Stream the ReAct agent's thinking process.
        
        Yields:
            Dict[str, Any]: Each step of the thinking process
        """
        # 1. 初始化思考过程和历史记录
        thought = (
            f"I need to answer the following question: {user_input}. "
            f"I should use the tools available to find the answer. "
            f"The available tools are: {self.tool_manager.get_tool_list()}. "
            f"I will start by thinking about which tool to use."
        )
        history = []
        all_citations = []  # 存储所有引用信息
        logger.info(f"Initial thought: {thought}")

        # 发送初始思考
        yield {
            "type": "thought",
            "step": 0,
            "content": thought
        }

        # 2. ReAct 循环
        for i in range(max_steps):
            logger.info(f"--- Step {i+1} ---")

            # 3. 生成行动（Action）
            prompt = f"""Thought: {thought}

请按照以下要求执行：
1. 尽可能使用提供的工具获取信息来回答问题
2. 最终答案中必须包含使用工具获取的引用来源
3. 工具使用格式：[工具名[参数]]，例如 search[北京天气]

Action: """
            action = self.llm_client.generate([{"role": "user", "content": prompt}])
            logger.info(f"Action: {action}")

            # 4. 检查是否得出最终答案
            if "Final Answer:" in action:
                final_answer = action.split("Final Answer:")[-1].strip()
                
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

            # 5. 执行行动并获取观察结果
            observation = self._execute_action(action)
            logger.info(f"Observation: {observation}")

            # 提取引用信息（如果有）
            step_citations = []
            try:
                import json
                # 尝试解析observation为JSON对象
                if isinstance(observation, str) and (observation.startswith('{') or observation.startswith('[')):
                    obs_data = json.loads(observation)
                    if isinstance(obs_data, dict) and 'citations' in obs_data:
                        step_citations = obs_data['citations']
                        all_citations.extend(step_citations)
            except:
                # 如果解析失败，忽略
                pass

            # 6. 发送当前步骤的思考过程
            yield {
                "type": "step",
                "step": i + 1,
                "thought": thought,
                "action": action,
                "observation": observation
            }

            # 7. 更新历史和思考过程
            history.append(f"Thought: {thought}")
            history.append(f"Action: {action}")
            history.append(f"Observation: {observation}")

            history_str = "\n".join(history)
            thought = (
                f"""Based on the history, I need to decide the next step. 
If I have the answer, I will output 'Final Answer:'. 
Otherwise, I will choose another action.

History:
{history_str}"""
            )

        # 8. 超出最大步数，发送错误信息
        logger.warning("Max steps reached, unable to find an answer.")
        yield {
            "type": "error",
            "step": max_steps,
            "content": "Sorry, I couldn't find an answer after several steps."
        }

    def _execute_action(self, action: str) -> str:
        tool_name, tool_input = self._parse_action(action)
        if not tool_name or not tool_input:
            logger.warning(f"Invalid action: {action}")
            return "Invalid action. Please try again."

        tool = self.tool_manager.get_tool(tool_name)
        if not tool:
            logger.error(f"Tool '{tool_name}' not found.")
            return f"Tool '{tool_name}' not found."

        try:
            result = tool.run(tool_input)
            return str(result)
        except Exception as e:
            logger.error(f"Error executing tool: {e}")
            return f"Error executing tool: {e}"

    def _parse_action(self, action: str) -> tuple[str, str] | tuple[None, None]:
        match = re.match(r"(.*?)\[(.*?)\]", action)
        if not match:
            return None, None

        tool_name = match.group(1).strip()
        tool_input = match.group(2).strip()
        return tool_name, tool_input
