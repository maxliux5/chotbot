import logging
import re
from chotbot.core.llm_client import LLMClient
from chotbot.mcp.tools.tool_manager import ToolManager

# 配置日志
logger = logging.getLogger(__name__)

class ReActAgent:
    def __init__(self, llm_client: LLMClient, tool_manager: ToolManager):
        self.llm_client = llm_client
        self.tool_manager = tool_manager

    def run(self, user_input: str, max_steps: int = 100) -> str:
        # 1. 初始化思考过程和历史记录
        thought = (
            f"I need to answer the following question: {user_input}. "
            f"I should use the tools available to find the answer. "
            f"The available tools are: {self.tool_manager.get_tool_list()}. "
            f"I will start by thinking about which tool to use."
        )
        history = []
        logger.info(f"Initial thought: {thought}")

        # 2. ReAct 循环
        for i in range(max_steps):
            logger.info(f"--- Step {i+1} ---")

            # 3. 生成行动（Action）
            prompt = f"""Thought: {thought}

Action: [Your action here, e.g., search[query]]"""
            action = self.llm_client.generate([{"role": "user", "content": prompt}])
            logger.info(f"Action: {action}")

            # 4. 检查是否得出最终答案
            if "Final Answer:" in action:
                final_answer = action.split("Final Answer:")[-1].strip()
                logger.info(f"Final Answer: {final_answer}")
                return final_answer

            # 5. 执行行动并获取观察结果
            observation = self._execute_action(action)
            logger.info(f"Observation: {observation}")

            # 6. 更新历史和思考过程
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

        # 7. 超出最大步数，返回错误信息
        logger.warning("Max steps reached, unable to find an answer.")
        return "Sorry, I couldn't find an answer after several steps."

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
