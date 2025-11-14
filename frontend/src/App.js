import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { role: 'user', content: inputValue.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage.content }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let assistantMessage = { role: 'assistant', content: '' };
      setMessages(prev => [...prev, assistantMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        assistantMessage.content += chunk;
        setMessages(prev => [...prev.slice(0, -1), { ...assistantMessage }]);
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = { role: 'assistant', content: '抱歉，发生了错误，请稍后重试。' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
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
