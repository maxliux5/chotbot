import React, { useState, useRef, useEffect, useMemo } from 'react';
import './App.css';

// Markdown 解析函数
const parseMarkdown = (text) => {
  if (!text) return '';
  
  let html = text
    // 代码块 ```code```
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    // 行内代码 `code`
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // 粗体 **text**
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    // 斜体 *text*
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    // 标题 ###
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // 链接 [text](url)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
    // 列表 - item
    .replace(/^\* (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
    // 换行
    .replace(/\n/g, '<br>');
  
  return html;
};

// Markdown 渲染组件
const MarkdownContent = ({ content }) => {
  const htmlContent = useMemo(() => parseMarkdown(content), [content]);
  
  return (
    <div 
      className="markdown-content"
      dangerouslySetInnerHTML={{ __html: htmlContent }}
    />
  );
};

function App() {
  // 新的状态结构：将每个对话轮次的信息放在一起
  // 每个轮次包含：userMessage, thinkingSteps, assistantMessage, showThinking
  const [conversations, setConversations] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  // 当前正在进行的对话的思考过程
  const [currentThinkingSteps, setCurrentThinkingSteps] = useState([]);
  const [currentPlan, setCurrentPlan] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversations, currentThinkingSteps, isLoading]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    console.log('=== 前端调试信息 ===');
    console.log('用户输入:', inputValue.trim());

    const userMessage = { role: 'user', content: inputValue.trim() };
    setInputValue('');
    setIsLoading(true);
    setCurrentThinkingSteps([]); // 清空当前思考过程
    setCurrentPlan(null); // 清空当前计划

    try {
      console.log('正在发送请求到后端...');
      
      const eventSource = new EventSource(`http://localhost:5001/api/chat/react-stream?message=${encodeURIComponent(userMessage.content)}`);
      
      let assistantMessage = { role: 'assistant', content: '' };
      let currentSteps = [];
      let hasFinalAnswer = false;

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('收到步骤数据:', data);

        if (data.type === 'plan') {
          setCurrentPlan(data.content);
        } else if (data.type === 'thought') {
          // 初始思考
          const existingThoughtIndex = currentSteps.findIndex(step => step.type === 'thought');
          if (existingThoughtIndex !== -1) {
            // 更新现有思考
            currentSteps[existingThoughtIndex].content = data.content;
          } else {
            // 添加新的思考
            currentSteps.push({
              step: 0,
              type: 'thought',
              content: data.content
            });
          }
          setCurrentThinkingSteps([...currentSteps]);
        } else if (data.type === 'step') {
          let observationText = data.observation;
          try {
            // 尝试将 observation 解析为 JSON 并格式化
            const obsJson = JSON.parse(data.observation);
            observationText = JSON.stringify(obsJson.result || obsJson, null, 2);
          } catch (e) {
            // 如果不是合法的 JSON 字符串，则直接使用原始文本
            console.log("Observation is not a JSON string, using as is.");
          }

          // 步骤更新
          currentSteps.push({
            step: data.step,
            type: 'action',
            thought: data.thought,
            action: data.action,
            observation: observationText, // 使用格式化后的文本
          });
          setCurrentThinkingSteps([...currentSteps]);
        } else if (data.type === 'final_answer') {
          // 最终答案
          assistantMessage.content = data.content;
          hasFinalAnswer = true;
          
          // 将当前对话轮次添加到会话列表中
          setConversations(prev => [
            ...prev,
            {
              userMessage,
              thinkingSteps: [...currentSteps],
              assistantMessage,
              showThinking: true // 默认显示思考过程
            }
          ]);
          
          // 清空当前思考过程
          setCurrentThinkingSteps([]);
          setIsLoading(false);
          eventSource.close();
        } else if (data.type === 'error') {
          // 错误处理
          assistantMessage.content = `错误: ${data.content}`;
          // 将当前对话轮次添加到会话列表中
          setConversations(prev => [
            ...prev,
            {
              userMessage,
              thinkingSteps: [...currentSteps],
              assistantMessage,
              showThinking: true // 默认显示思考过程
            }
          ]);
          
          // 清空当前思考过程
          setCurrentThinkingSteps([]);
          setIsLoading(false);
          eventSource.close();
        }
      };

      eventSource.onerror = (error) => {
        console.error('EventSource 失败:', error);
        eventSource.close();
        setIsLoading(false);
      };

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
      setShowThinking(false); // 隐藏思考过程
    } finally {
      setIsLoading(false);
    }
  };

  // 切换特定对话轮次的思考过程显示
  const toggleThinking = (index) => {
    setConversations(prev => {
      const newConversations = [...prev];
      newConversations[index].showThinking = !newConversations[index].showThinking;
      return newConversations;
    });
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
          {/* 显示所有对话轮次 */}
          {conversations.map((conversation, convIndex) => (
            <React.Fragment key={convIndex}>
              {/* 显示用户的问题 */}
              <div className={`message ${conversation.userMessage.role}`}>
                <div className="message-content">
                  <MarkdownContent content={conversation.userMessage.content} />
                </div>
              </div>
              
              {/* 显示思考过程 */}
              {conversation.thinkingSteps.length > 0 && (
                <div className={`message assistant thinking ${conversation.showThinking ? '' : 'collapsed'}`}>
                  <div className="message-content">
                    <div className="thinking-header" onClick={() => toggleThinking(convIndex)}>
                      🤔 思考过程
                      <span className="toggle-icon">{conversation.showThinking ? '▼' : '▶'}</span>
                    </div>
                    {conversation.showThinking && (
                      <>
                        {conversation.thinkingSteps.map((step, stepIndex) => (
                          <div key={stepIndex} className="thinking-step">
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
                                    <strong>👁️ 观察:</strong>
                                    <pre><code>{step.observation}</code></pre>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </>
                    )}
                  </div>
                </div>
              )}
              
              {/* 显示助手的答案 */}
              <div className={`message ${conversation.assistantMessage.role}`}>
                <div className="message-content">
                  <MarkdownContent content={conversation.assistantMessage.content} />
                </div>
              </div>
            </React.Fragment>
          ))}
          
          {/* 显示当前正在进行的对话的思考过程 */}
          {isLoading && currentPlan && (
            <div className="message assistant thinking">
              <div className="message-content">
                <div className="thinking-header">
                  📝 计划
                </div>
                <div className="thought-content">
                  <MarkdownContent content={currentPlan} />
                </div>
              </div>
            </div>
          )}

          {isLoading && currentThinkingSteps.length > 0 && (
            <div className={`message assistant thinking ${true ? '' : 'collapsed'}`}>
              <div className="message-content">
                <div className="thinking-header">
                  🤔 思考过程
                  <span className="toggle-icon">▼</span>
                </div>
                <>
                  {currentThinkingSteps.map((step, stepIndex) => (
                    <div key={stepIndex} className="thinking-step">
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
                              <strong>👁️ 观察:</strong>
                              <pre><code>{step.observation}</code></pre>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </>
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
