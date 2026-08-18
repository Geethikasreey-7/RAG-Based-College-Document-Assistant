import React, { useEffect, useRef } from "react";
import { SourceReferences } from "./SourceReferences";
import "../styles/ChatWindow.css";

export const ChatWindow = ({ messages, isLoading, error }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (messages.length === 0 && !isLoading && !error) {
    return (
      <div className="chat-window">
        <div className="empty-chat-state">
          <span className="empty-chat-icon">💬</span>
          <h2>Welcome to RAG Chatbot</h2>
          <p>Upload documents and ask questions about their content.</p>
          <ul className="chat-tips">
            <li>📤 Upload PDFs from the left panel</li>
            <li>🔍 Ask questions about your documents</li>
            <li>📝 Get answers with source citations</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-window">
      {messages.length > 0 && (
        <div className="messages-container">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === "user" ? "👤" : "🤖"}
              </div>
              <div className="message-content-wrapper">
                <div className="message-text">{msg.text}</div>
                {msg.sources && msg.sources.length > 0 && (
                  <SourceReferences sources={msg.sources} />
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {isLoading && (
        <div className="message assistant">
          <div className="message-avatar">🤖</div>
          <div className="message-content-wrapper">
            <div className="loading-indicator">
              <span className="spinner">⟳</span>
              <span>Thinking...</span>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="message error">
          <div className="message-avatar">⚠️</div>
          <div className="message-content-wrapper">
            <div className="error-text">{error}</div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatWindow;
