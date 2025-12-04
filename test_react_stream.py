#!/usr/bin/env python3
"""
测试 ReAct Agent 流式接口
"""

import requests
import json
import sys

def test_react_stream():
    """测试 ReAct 流式接口"""
    print("🧪 测试 ReAct Agent 流式接口...")
    
    try:
        # 发送请求
        response = requests.post(
            'http://localhost:5001/api/chat/react-stream',
            json={'message': '世界首富是谁'},
            stream=True,
            timeout=30
        )
        
        print(f"📡 响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.text}")
            return False
        
        print("\n📨 接收到的思考步骤:")
        print("=" * 60)
        
        step_count = 0
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    data = json.loads(line)
                    step_count += 1
                    
                    print(f"\n步骤 {step_count}:")
                    print(f"类型: {data.get('type')}")
                    
                    if data.get('type') == 'thought':
                        print(f"思考: {data.get('content', '')[:100]}...")
                    elif data.get('type') == 'step':
                        print(f"思考: {data.get('thought', '')[:80]}...")
                        print(f"行动: {data.get('action', '')}")
                        print(f"观察: {str(data.get('observation', ''))[:80]}...")
                    elif data.get('type') == 'final_answer':
                        print(f"最终答案: {data.get('content', '')}")
                    elif data.get('type') == 'error':
                        print(f"错误: {data.get('content', '')}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析失败: {e}")
                    print(f"原始数据: {line}")
        
        print("\n" + "=" * 60)
        print(f"✅ 测试完成，共接收 {step_count} 个步骤")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保服务已启动")
        print("请运行: bash start.sh")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_react_stream()
    sys.exit(0 if success else 1)