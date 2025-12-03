from chotbot.core.llm_client import LLMClient
from chotbot.rag.rag_manager import RAGManager
from chotbot.mcp.processor import MCPProcessor
from chotbot.intent.intent_recognizer import IntentRecognizer
from chotbot.mcp.tools.tool_manager import ToolManager
from chotbot.core.react_agent import ReActAgent

class Chatbot:
    """
    Main Chatbot class that integrates LLM, RAG, MCP, and Intent Recognition.
    """
    def __init__(self, intent_config_path: str = None):
        self.llm_client = LLMClient()
        self.rag_manager = RAGManager(self.llm_client)
        self.mcp_processor = MCPProcessor(self.llm_client)
        
        # 初始化意图识别模块
        self.intent_recognizer = IntentRecognizer(intent_config_path)
        
        # 初始化工具管理器
        self.tool_manager = ToolManager()
    
        # 初始化 ReAct 代理
        self.react_agent = ReActAgent(self.llm_client, self.tool_manager)
    
    def add_documents(self, documents: list):
        """
        Add documents to the RAG system.
        
        Args:
            documents (list): List of document texts
        """
        self.rag_manager.add_documents(documents)
    
    def chat(self, user_input: str, use_rag: bool = True, system_prompt: str = None) -> str:
        """
        Process a user input and generate a response.
        
        Args:
            user_input (str): User's input message
            use_rag (bool): Whether to use RAG for retrieval
            system_prompt (str): Optional system prompt
            
        Returns:
            str: Generated response
        """
        # 意图识别
        # intent_result = self.intent_recognizer.recognize(user_input)
        # intent = intent_result['intent']
        # slots = intent_result['slots']
        
        # # 可以根据意图和槽位执行不同的操作
        # # 目前只是打印识别结果
        # print(f"意图识别结果:")
        # print(f"  意图: {intent}")
        # print(f"  槽位: {slots}")
        # print(f"  置信度: {intent_result['confidence']:.2f}")
        
        # 尝试使用工具调用
        response = None
        
        # if intent == "查询天气":
        #     response = self._handle_weather_query(slots)
        # elif intent == "查询股票":
        #     response = self._handle_stock_query(slots)
        # elif intent == "查询基金":
        #     response = self._handle_fund_query(slots)
        # elif intent == "search":
        response = self._handle_deep_search(user_input)
        
        # 如果工具调用成功，直接返回结果
        if response:
            # Add to MCP context
            self.mcp_processor.context_manager.add_message("user", user_input)
            self.mcp_processor.context_manager.add_message("assistant", response)
            return response
        
        # 继续原有逻辑
        if use_rag:
            # Use RAG for response generation
            response = self.rag_manager.query(user_input)
            # Add to MCP context
            self.mcp_processor.context_manager.add_message("user", user_input)
            self.mcp_processor.context_manager.add_message("assistant", response)
            return response
        else:
            # Use MCP for context-aware generation
            return self.mcp_processor.interact(user_input, system_prompt=system_prompt)
    
    def chat_stream(self, user_input: str, use_rag: bool = True, system_prompt: str = None):
        """
        Process a user input and generate a streaming response.
        
        Args:
            user_input (str): User's input message
            use_rag (bool): Whether to use RAG for retrieval
            system_prompt (str): Optional system prompt
            
        Yields:
            str: Chunks of the generated response
        """
        # 意图识别
        intent_result = self.intent_recognizer.recognize(user_input)
        intent = intent_result['intent']
        slots = intent_result['slots']
        
        # 可以根据意图和槽位执行不同的操作
        # 目前只是打印识别结果
        print(f"意图识别结果:")
        print(f"  意图: {intent}")
        print(f"  槽位: {slots}")
        print(f"  置信度: {intent_result['confidence']:.2f}")
        
        # 尝试使用工具调用
        response = None
        
        if intent == "查询天气":
            response = self._handle_weather_query(slots)
        elif intent == "查询股票":
            response = self._handle_stock_query(slots)
        elif intent == "查询基金":
            response = self._handle_fund_query(slots)
        
        # 如果工具调用成功，直接返回结果
        if response:
            # Add to MCP context
            self.mcp_processor.context_manager.add_message("user", user_input)
            self.mcp_processor.context_manager.add_message("assistant", response)
            yield response
            return
        
        # 继续原有逻辑
        if use_rag:
            # For streaming, use the LLM client directly with retrieved context
            context_docs = self.rag_manager.retrieve_context(user_input)
            context = "\n".join([doc.page_content for doc in context_docs])
            
            # Create messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": f"上下文：{context}\n\n问题：{user_input}"})
            
            # Get streaming response
            for chunk in self.llm_client.generate_stream(messages):
                yield chunk
            
            # Combine response for context
            full_response = ""
            for chunk in self.llm_client.generate(messages):
                full_response += chunk
            
            # Add to MCP context
            self.mcp_processor.context_manager.add_message("user", user_input)
            self.mcp_processor.context_manager.add_message("assistant", full_response)
        else:
            # Use MCP for context-aware streaming generation
            response = self.mcp_processor.interact(user_input, system_prompt=system_prompt)
            yield response
    
    def _handle_weather_query(self, slots: dict) -> str:
        """
        处理天气查询意图
        
        Args:
            slots (dict): 槽位信息
            
        Returns:
            str: 天气查询结果
        """
        city = slots.get("城市")
        if not city:
            return "请告诉我您要查询哪个城市的天气。"
            
        weather_tool = self.tool_manager.get_tool("查询天气")
        result = weather_tool.get_weather_by_city(city)
        
        if "error" in result:
            return f"天气查询失败：{result['message']}"
            
        # 格式化天气信息
        weather_info = []
        for key, value in result.items():
            weather_info.append(f"{key}：{value}")
        
        return "\n".join(weather_info)
    
    def _handle_stock_query(self, slots: dict) -> str:
        """
        处理股票查询意图
        
        Args:
            slots (dict): 槽位信息
            
        Returns:
            str: 股票查询结果
        """
        stock_symbol = slots.get("股票代码")
        if not stock_symbol:
            return "请告诉我您要查询的股票代码或名称。"
            
        # 这里可以添加股票查询逻辑，目前暂时返回提示
        return f"股票查询功能正在开发中，您查询的是 {stock_symbol}。"
    
    def _handle_fund_query(self, slots: dict) -> str:
        """
        处理基金查询意图
        
        Args:
            slots (dict): 槽位信息
            
        Returns:
            str: 基金查询结果
        """
        fund_code = slots.get("基金代码")
        if not fund_code:
            return "请告诉我您要查询的基金代码。"
            
        fund_tool = self.tool_manager.get_tool("查询基金信息")
        result = fund_tool.get_fund_basic_info(fund_code)
        
        if "error" in result:
            return f"基金查询失败：{result['message']}"
            
        # 格式化基金信息
        fund_info = []
        for key, value in result.items():
            if value:  # 只显示有值的信息
                fund_info.append(f"{key}：{value}")
        
        return "\n".join(fund_info)

    def _handle_deep_search(self, user_input: str) -> str:
        """
        处理深度搜索意图
        
        Args:
            slots (dict): 槽位信息
            
        Returns:
            str: 搜索结果
        """
    
            
        return self.react_agent.run(user_input)
    
    def clear_context(self):
        """
        Clear the chat context.
        """
        self.mcp_processor.clear_context()
    
    def get_context(self) -> list:
        """
        Get the current chat context.
        
        Returns:
            list: Current context messages
        """
        return self.mcp_processor.get_context()
