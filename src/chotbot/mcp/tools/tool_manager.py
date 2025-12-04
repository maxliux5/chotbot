#!/usr/bin/env python3
"""
MCP 工具管理器
"""

from typing import Dict, Any, List
from chotbot.mcp.tools.weather import WeatherTool
from chotbot.mcp.tools.fund import FundTool
from chotbot.mcp.tools.search import SearchTool

class ToolManager:
    """
    工具管理器类，用于管理所有可调用的 MCP 工具
    """
    
    def __init__(self):
        self.tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """
        初始化所有工具
        """
        self.tools["查询天气"] = WeatherTool()
        self.tools["查询基金信息"] = FundTool()
        self.tools["search"] = SearchTool()
    
    def get_tool_list(self) -> List[Dict[str, Any]]:
        """
        获取所有可用工具的列表
        
        Returns:
            List[Dict[str, Any]]: 工具列表
        """
        tool_list = []
        
        for tool_name, tool_instance in self.tools.items():
            # 获取工具的方法信息
            methods = []
            for method_name in dir(tool_instance):
                if not method_name.startswith('_'):
                    method = getattr(tool_instance, method_name)
                    if callable(method):
                        methods.append(method_name)
            
            tool_list.append({
                "name": tool_name,
                "type": tool_instance.__class__.__name__,
                "methods": methods
            })
        
        return tool_list
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        获取工具定义，用于OpenAI Function Calling
        
        Returns:
            List[Dict[str, Any]]: OpenAI函数定义列表
        """
        definitions = []
        
        # search工具
        definitions.append({
            "type": "function",
            "function": {
                "name": "search",
                "description": "Search for information on the internet",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        })
        
        # end_tool - 用于表示任务完成
        definitions.append({
            "type": "function",
            "function": {
                "name": "end_tool",
                "description": "Call this tool when you have completed the task and have the final answer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "final_answer": {
                            "type": "string",
                            "description": "The final answer to the user's question"
                        }
                    },
                    "required": ["final_answer"]
                }
            }
        })
        
        return definitions
    
    def get_tool(self, tool_name: str):
        """
        根据工具名称获取工具实例
        
        Args:
            tool_name (str): 工具名称
            
        Returns:
            object: 工具实例
        """
        return self.tools.get(tool_name)
    
    def call_tool(self, tool_name: str, method: str, **kwargs) -> Any:
        """
        调用指定工具的指定方法
        
        Args:
            tool_name (str): 工具名称
            method (str): 方法名称
            **kwargs: 方法参数
            
        Returns:
            Any: 工具调用结果
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return {"error": f"工具 {tool_name} 不存在"}
        
        if not hasattr(tool, method):
            return {"error": f"工具 {tool_name} 没有方法 {method}"}
        
        tool_method = getattr(tool, method)
        
        try:
            result = tool_method(**kwargs)
            return result
        except Exception as e:
            return {"error": f"工具调用失败: {str(e)}", "message": "请检查参数是否正确"}
    
    def execute_tool_call(self, tool_call) -> Dict[str, Any]:
        """
        执行工具调用（OpenAI Function Calling格式）
        
        Args:
            tool_call: 工具调用信息（ChatCompletionMessageFunctionToolCall对象）
            
        Returns:
            工具执行结果
        """
        # ChatCompletionMessageFunctionToolCall对象有function属性
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        tool_call_id = tool_call.id
        
        if tool_name == "end_tool":
            # end_tool是特殊的完成工具
            return {
                "tool": "end_tool",
                "result": arguments["final_answer"],
                "status": "completed",
                "tool_call_id": tool_call_id
            }
        elif tool_name == "search":
            # 执行search工具
            tool = self.get_tool("search")
            if tool:
                result = tool.run(arguments["query"])
                return {
                    "tool": "search",
                    "result": result,
                    "status": "success",
                    "tool_call_id": tool_call_id
                }
            else:
                return {
                    "tool": "search",
                    "error": "Tool not found",
                    "status": "error",
                    "tool_call_id": tool_call_id
                }
        else:
            return {
                "tool": tool_name,
                "error": f"Unknown tool: {tool_name}",
                "status": "error",
                "tool_call_id": tool_call_id
            }
