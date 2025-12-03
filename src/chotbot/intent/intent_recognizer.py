#!/usr/bin/env python3
"""
意图识别模块 - 使用LLM进行意图识别与槽位提取
"""

import os
import json
import re
import json
from typing import Dict, List
from chotbot.core.llm_client import LLMClient

class IntentRecognizer:
    """
    意图识别类，使用LLM进行意图识别和槽位提取
    """

    def __init__(self, config_path: str = None):
        """
        初始化意图识别模块
        Args:
            config_path: 意图配置文件路径
        """
        self.config = self._load_config(config_path)
        self.intents = self.config.get('intents', [])
        self.llm_client = LLMClient()

    def _load_config(self, config_path: str = None) -> Dict:
        """
        加载意图配置文件
        Args:
            config_path: 配置文件路径
        Returns:
            配置字典
        """
        default_config = {
            "intents": []
        }

        if not config_path:
            return default_config

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件 {config_path} 不存在")

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def recognize(self, user_input: str) -> Dict:
        """
        识别用户输入的意图和槽位
        Args:
            user_input: 用户输入文本
        Returns:
            识别结果，包含intent和slots
        """
        # 预处理用户输入
        input_clean = user_input.strip()
        
        # 准备意图列表和示例
        intent_info = []
        for intent in self.intents:
            intent_info.append(f"意图名称：{intent['name']}")
            intent_info.append(f"意图描述：{intent.get('description', '无描述')}")
            intent_info.append(f"示例：{'; '.join(intent.get('examples', []))}")
            slots = intent.get('slots', [])
            if slots:
                slot_info = []
                for slot in slots:
                    slot_info.append(f"{slot['name']}（类型：{slot['type']}）")
                intent_info.append(f"槽位：{'; '.join(slot_info)}")
            intent_info.append("")
        
        intent_info_str = "\n".join(intent_info)
        
        # 构建prompt
        prompt = f"""
我需要你作为一个意图识别助手，根据用户输入和提供的意图配置，识别出正确的意图和对应的槽位。
要求：
1. 仅从提供的意图列表中选择一个最匹配的意图
2. 槽位提取要准确，仅提取用户输入中明确提到的信息
3. 输出格式必须是严格的JSON格式，包含intent（意图名称）、slots（槽位字典）和confidence（置信度，0-1之间）
4. 如果没有匹配的意图，返回意图为'闲聊'，置信度0.5

提供的意图配置：
{intent_info_str}

用户输入：{input_clean}
"""
        
        try:
            # 使用LLM进行意图识别
            response = self.llm_client.generate([
                {"role": "system", "content": "你是一个意图识别专家，严格按照要求输出JSON格式的结果"},
                {"role": "user", "content": prompt}
            ])
            
            # 解析LLM输出
            # 去除可能的markdown格式
            if response.strip().startswith('```json'):
                response = response[7:].strip()
                if response.endswith('```'):
                    response = response[:-3].strip()
            elif response.strip().startswith('```'):
                response = response[3:].strip()
                if response.endswith('```'):
                    response = response[:-3].strip()
            
            result = json.loads(response)
            
            # 确保结果格式正确
            if 'intent' not in result:
                result['intent'] = '闲聊'
            if 'slots' not in result:
                result['slots'] = {}
            if 'confidence' not in result:
                result['confidence'] = 0.5

            # 如果意图是 deepsearch，则将用户输入作为 query 槽位
            if result['intent'] == "deepsearch":
                result['slots']['query'] = user_input
                
            return result
        except Exception as e:
            # 发生错误时返回默认结果
            return {
                'intent': '闲聊',
                'slots': {},
                'confidence': 0.5
            }

    def add_intent(self, intent_name: str, examples: List[str], slots: List[Dict] = None) -> None:
        """
        添加新意图
        Args:
            intent_name: 意图名称
            examples: 意图示例
            slots: 槽位信息
        """
        new_intent = {
            'name': intent_name,
            'examples': examples,
            'slots': slots or []
        }
        self.intents.append(new_intent)

    def save_config(self, config_path: str) -> None:
        """
        保存配置文件
        Args:
            config_path: 配置文件路径
        """
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
