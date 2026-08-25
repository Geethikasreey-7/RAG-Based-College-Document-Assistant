import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import DocumentUpload from "./components/DocumentUpload";
import DocumentList from "./components/DocumentList";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import { documentAPI, chatAPI, conversationAPI } from "./services/api";
import "./styles/App.css";

function App() {
  const [documents, setDocuments] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false);
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);
  const [isLoadingChat, setIsLoadingChat] = useState(false);
  const [chatError, setChatError] = useState("");

  useEffect(() => {
    loadDocuments();
    loadConversations();
  }, []);

  const loadDocuments = async () => {
    setIsLoadingDocuments(true);
    try {
      const result = await documentAPI.list();
      setDocuments(result.documents || []);
    } catch (error) {
      console.error("Failed to load documents:", error);
    } finally {
      setIsLoadingDocuments(false);
    }
  };

  const loadConversations = async () => {
    setIsLoadingConversations(true);
    try {
      const result = await conversationAPI.list();
      setConversations(result || []);

      if (result && result.length > 0 && !activeConversationId) {
        setActiveConversationId(result[0].conversation_id);
        const detail = await conversationAPI.get(result[0].conversation_id);
        setMessages((detail.messages || []).map((message) => ({
          role: message.role,
          text: message.content,
          sources: [],
        })));
      }
    } catch (error) {
      console.error("Failed to load conversations:", error);
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const handleUploadSuccess = () => {
    loadDocuments();
    setChatError("");
  };

  const handleUploadError = (error) => {
    console.error("Upload error:", error);
  };

  const handleDocumentDeleted = (filename) => {
    setDocuments((prev) => prev.filter((doc) => doc.filename !== filename));
  };

  const handleCreateConversation = async () => {
    try {
      const conversation = await conversationAPI.create(`Chat ${conversations.length + 1}`);
      setConversations((prev) => [conversation, ...prev]);
      setActiveConversationId(conversation.conversation_id);
      setMessages([]);
      setChatError("");
    } catch (error) {
      console.error("Failed to create conversation:", error);
      setChatError("Unable to create a new conversation.");
    }
  };

  const handleSelectConversation = async (conversationId) => {
    setActiveConversationId(conversationId);
    try {
      const conversation = await conversationAPI.get(conversationId);
      setMessages((conversation.messages || []).map((message) => ({
        role: message.role,
        text: message.content,
        sources: [],
      })));
      setChatError("");
    } catch (error) {
      console.error("Failed to load conversation details:", error);
      setChatError("Unable to load this conversation.");
    }
  };

  const handleDeleteConversation = async (e, conversationId) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this conversation?")) return;

    try {
      await conversationAPI.delete(conversationId);
      const remaining = conversations.filter((c) => c.conversation_id !== conversationId);
      setConversations(remaining);

      if (activeConversationId === conversationId) {
        if (remaining.length > 0) {
          handleSelectConversation(remaining[0].conversation_id);
        } else {
          setActiveConversationId(null);
          setMessages([]);
        }
      }
    } catch (error) {
      console.error("Failed to delete conversation:", error);
      setChatError("Unable to delete this conversation.");
    }
  };

  const handleSendMessage = async (question) => {
    if (!documents || documents.length === 0) {
      setChatError("Please upload documents first before asking questions.");
      return;
    }

    let currentConversationId = activeConversationId;
    if (!currentConversationId) {
      try {
        const conversation = await conversationAPI.create(`Chat ${conversations.length + 1}`);
        currentConversationId = conversation.conversation_id;
        setConversations((prev) => [conversation, ...prev]);
        setActiveConversationId(currentConversationId);
      } catch (error) {
        console.error("Failed to create conversation:", error);
        setChatError("Unable to create a conversation before sending the message.");
        return;
      }
    }

    setChatError("");
    setMessages((prev) => [...prev, { role: "user", text: question, sources: [] }]);
    setIsLoadingChat(true);

    try {
      await conversationAPI.addMessage(currentConversationId, "user", question);
      const result = await chatAPI.chat(question, currentConversationId);
      const assistantMessage = {
        role: "assistant",
        text: result.answer,
        sources: result.sources || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);
      await conversationAPI.addMessage(currentConversationId, "assistant", result.answer);
      await loadConversations();
    } catch (error) {
      const errorMsg =
        error.response?.data?.detail ||
        error.message ||
        "Failed to generate answer";
      setChatError(errorMsg);
      setMessages((prev) => [
        ...prev,
        {
          role: "error",
          text: `Error: ${errorMsg}`,
        },
      ]);
    } finally {
      setIsLoadingChat(false);
    }
  };

  return (
    <div className="app">
      <Navbar />
      <div className="app-container">
        <aside className="sidebar">
          <div className="sidebar-content">
            <section className="sidebar-section">
              <div className="sidebar-header-row">
                <h2 className="section-title">Conversations</h2>
                <button className="new-conversation-button" onClick={handleCreateConversation}>
                  New
                </button>
              </div>

              <div className="conversation-list">
                {isLoadingConversations ? (
                  <div className="empty-state small">
                    <span className="spinner">⟳</span>
                    <span>Loading conversations...</span>
                  </div>
                ) : conversations.length === 0 ? (
                  <div className="empty-state small">
                    <span className="empty-icon">💬</span>
                    <span>No conversations yet</span>
                  </div>
                ) : (
                  conversations.map((conversation) => (
                    <div
                      key={conversation.conversation_id}
                      className={`conversation-item ${
                        activeConversationId === conversation.conversation_id ? "active" : ""
                      }`}
                      onClick={() => handleSelectConversation(conversation.conversation_id)}
                      role="button"
                      tabIndex={0}
                    >
                      <div className="conversation-item-content">
                        <span className="conversation-title">{conversation.title}</span>
                        <span className="conversation-meta">
                          {new Date(conversation.updated_at).toLocaleDateString()}
                        </span>
                      </div>
                      <button
                        className="conversation-delete-button"
                        onClick={(e) => handleDeleteConversation(e, conversation.conversation_id)}
                        title="Delete conversation"
                      >
                        ✕
                      </button>
                    </div>
                  ))
                )}
              </div>
            </section>

            <section className="sidebar-section">
              <h2 className="section-title">Upload Documents</h2>
              <DocumentUpload
                onUploadSuccess={handleUploadSuccess}
                onUploadError={handleUploadError}
              />
            </section>

            <section className="sidebar-section">
              <DocumentList
                documents={documents}
                onDocumentDeleted={handleDocumentDeleted}
                isLoading={isLoadingDocuments}
              />
            </section>
          </div>
        </aside>

        <main className="main-content">
          <div className="chat-container">
            <ChatWindow
              messages={messages}
              isLoading={isLoadingChat}
              error={chatError}
            />
            <ChatInput
              onSend={handleSendMessage}
              isLoading={isLoadingChat}
              disabled={!documents || documents.length === 0}
            />
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
