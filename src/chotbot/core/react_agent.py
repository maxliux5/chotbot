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
        thought = f"I need to answer the following question: {user_input}\nThis is the first step, I should use deepsearch to find the answer."
        logger.info(f"Initial thought: {thought}")
        
        # Add a new variable to store the history of thoughts and actions
        history = []

        for i in range(max_steps):
            logger.info(f"------Step {i+1}-----")
            
            # Generate action based on the current thought
            action = self.llm_client.generate([{"role": "user", "content": f"{thought}\nAction:"}])
            logger.info(f"Action: {action}")
            
            # Append thought and action to history
            history.append(f"Thought: {thought}")
            history.append(f"Action: {action}")

            if "Final Answer:" in action:
                final_answer = action.split("Final Answer:")[-1].strip()
                logger.info(f"Final Answer: {final_answer}")
                return final_answer

            # Execute the action and get observation
            observation = self._execute_action(action)
            logger.info(f"Observation: {observation}")
            
            # Append observation to history
            history.append(f"Observation: {observation}")
            
            # Update thought with the latest history
            thought = f"Based on the following history:\n{'\n'.join(history)}\nI need to decide the next step. If I have enough information, I will provide the final answer. Otherwise, I will continue to use tools."

        logger.warning("Max steps reached, unable to find an answer.")
        return "I am sorry, but I was unable to find an answer."

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
