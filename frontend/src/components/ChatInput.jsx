import React, { useState } from "react";
import "../styles/ChatInput.css";

export const ChatInput = ({ onSend, isLoading, disabled }) => {
  const [input, setInput] = useState("");

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading || disabled) return;

    onSend(trimmed);
    setInput("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-input">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about your documents... (Enter to send)"
        disabled={isLoading || disabled}
        className="input-textarea"
        rows="3"
      />
      <button
        onClick={handleSend}
        disabled={!input.trim() || isLoading || disabled}
        className="send-button"
        title="Send message"
      >
        {isLoading ? "⟳" : "→"}
      </button>
    </div>
  );
};

export default ChatInput;
