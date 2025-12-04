import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [thinkingSteps, setThinkingSteps] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, thinkingSteps]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    console.log('=== 前端调试信息 ===');
    console.log('用户输入:', inputValue.trim());

    const userMessage = { role: 'user', content: inputValue.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setThinkingSteps([]); // 清空之前的思考步骤

    try {
      console.log('正在发送请求到后端...');
      
      // 使用 ReAct 流式接口
      const response = await fetch('http://localhost:5001/api/chat/react-stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage.content }),
      });

      console.log('后端响应状态:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('后端错误响应:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      // 处理流式响应
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = { role: 'assistant', content: '' };
      let currentSteps = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            console.log('收到步骤数据:', data);

            if (data.type === 'thought') {
              // 初始思考
              currentSteps.push({
                step: 0,
                type: 'thought',
                content: data.content
              });
              setThinkingSteps([...currentSteps]);
            } else if (data.type === 'step') {
              // 步骤更新
              currentSteps.push({
                step: data.step,
                type: 'action',
                thought: data.thought,
                action: data.action,
                observation: data.observation
              });
              setThinkingSteps([...currentSteps]);
            } else if (data.type === 'final_answer') {
              // 最终答案
              assistantMessage.content = data.content;
              
              // 添加最终答案到思考步骤
              currentSteps.push({
                step: currentSteps.length,
                type: 'final_answer',
                content: data.content
              });
              setThinkingSteps([...currentSteps]);
              
              // 添加到消息列表
              setMessages(prev => [...prev, assistantMessage]);
            } else if (data.type === 'error') {
              // 错误处理
              assistantMessage.content = `错误: ${data.content}`;
              setMessages(prev => [...prev, assistantMessage]);
            }
          } catch (e) {
            console.error('解析步骤数据失败:', e, '原始数据:', line);
          }
        }
      }

    } catch (error) {
      console.error('=== 前端错误 ===');
      console.error('错误详情:', error);
      console.error('错误堆栈:', error.stack);
      
      const errorMessage = { 
        role: 'assistant', 
        content: `抱歉，发生了错误：${error.message}

调试信息：
- 请确保后端服务运行在 http://localhost:5001
- 检查浏览器控制台是否有CORS错误
- 检查后端日志文件 backend.log` 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      // 清空思考步骤（可选，根据需求决定）
      setTimeout(() => setThinkingSteps([]), 5000);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="app">
      <div className="chat-container">
        <div className="messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="message-content">{msg.content}</div>
            </div>
          ))}
          
          {/* 思考过程展示 */}
          {thinkingSteps.length > 0 && (
            <div className="message assistant thinking">
              <div className="message-content">
                <div className="thinking-header">🤔 思考过程:</div>
                {thinkingSteps.map((step, index) => (
                  <div key={index} className="thinking-step">
                    {step.type === 'thought' && (
                      <div className="thought">
                        <strong>初始思考:</strong>
                        <div className="thought-content">{step.content}</div>
                      </div>
                    )}
                    {step.type === 'action' && (
                      <div className="action">
                        <strong>步骤 {step.step}:</strong>
                        <div className="action-content">
                          <div className="sub-thought">
                            <strong>💭 思考:</strong> {step.thought}
                          </div>
                          <div className="action-detail">
                            <strong>🎯 行动:</strong> <code>{step.action}</code>
                          </div>
                          <div className="observation">
                            <strong>👁️ 观察:</strong> {step.observation}
                          </div>
                        </div>
                      </div>
                    )}
                    {step.type === 'final_answer' && (
                      <div className="final-answer">
                        <strong>✅ 最终答案:</strong>
                        <div className="final-answer-content">{step.content}</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {isLoading && (
            <div className="message assistant">
              <div className="message-content loading">正在思考...</div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="input-area">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入问题..."
            disabled={isLoading}
          />
          <button onClick={handleSend} disabled={isLoading}>
            发送
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
