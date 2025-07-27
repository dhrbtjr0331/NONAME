import React, { useState, useRef, useEffect } from 'react';
import Button from '../common/Button';

const RFQAssistantSidebar = ({ 
  isOpen, 
  onClose, 
  messages, 
  onSendMessage, 
  loading 
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputMessage.trim() && !loading) {
      onSendMessage(inputMessage.trim());
      setInputMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className={`rfq-assistant-sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <h3>RFQ Assistant</h3>
        <button 
          className="close-button"
          onClick={onClose}
          aria-label="Close RFQ Assistant"
        >
          ×
        </button>
      </div>
      
      <div className="sidebar-content">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <p>Hi! I'm your RFQ Assistant. I can help you fill out your RFQ form by asking about your requirements.</p>
              <p>Try asking me something like:</p>
              <ul>
                <li>"I need 1000 electronic components"</li>
                <li>"My budget is $50 per unit"</li>
                <li>"I need this delivered by next month"</li>
              </ul>
            </div>
          )}
          
          {messages.map((message, index) => (
            <div 
              key={index} 
              className={`message ${message.type === 'user' ? 'user-message' : 'assistant-message'}`}
            >
              <div className="message-content">
                {message.content}
              </div>
              {message.type === 'assistant' && message.timestamp && (
                <div className="message-timestamp">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              )}
            </div>
          ))}
          
          {loading && (
            <div className="message assistant-message">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        <form onSubmit={handleSubmit} className="message-input-form">
          <div className="input-container">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about your RFQ requirements..."
              className="message-input"
              rows="2"
              disabled={loading}
            />
            <Button 
              type="submit" 
              disabled={!inputMessage.trim() || loading}
              className="send-button"
            >
              Send
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RFQAssistantSidebar;