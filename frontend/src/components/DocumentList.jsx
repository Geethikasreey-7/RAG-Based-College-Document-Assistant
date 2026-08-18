import React, { useState } from "react";
import { documentAPI } from "../services/api";
import "../styles/DocumentList.css";

export const DocumentList = ({ documents, onDocumentDeleted, isLoading }) => {
  const [deletingFile, setDeletingFile] = useState(null);
  const [deleteError, setDeleteError] = useState("");

  const handleDelete = async (filename) => {
    if (!window.confirm(`Delete "${filename}"?`)) return;

    setDeletingFile(filename);
    setDeleteError("");

    try {
      await documentAPI.delete(filename);
      onDocumentDeleted(filename);
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || "Delete failed";
      setDeleteError(errorMsg);
    } finally {
      setDeletingFile(null);
    }
  };

  const getStatusLabel = (doc) => {
    if (doc.chunk_count > 0) return "Ready";
    return "Processing";
  };

  if (isLoading) {
    return (
      <div className="document-list">
        <div className="empty-state">
          <span className="spinner">⟳</span>
          <span>Loading documents...</span>
        </div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="document-list">
        <div className="empty-state">
          <span className="empty-icon">📋</span>
          <span>No documents uploaded yet</span>
        </div>
      </div>
    );
  }

  return (
    <div className="document-list">
      <h3 className="document-list-title">Documents ({documents.length})</h3>
      {deleteError && <div className="delete-error-message">{deleteError}</div>}
      <div className="document-items">
        {documents.map((doc) => (
          <div key={doc.filename} className="document-item">
            <div className="document-info">
              <span className="document-icon">📄</span>
              <div className="document-details">
                <span className="document-name">{doc.filename}</span>
                <div className="document-meta">
                  <span className="document-chunks">{doc.chunk_count} chunks</span>
                  <span className={`status-badge ${doc.chunk_count > 0 ? "ready" : "processing"}`}>
                    {getStatusLabel(doc)}
                  </span>
                </div>
              </div>
            </div>
            <button
              className="delete-button"
              onClick={() => handleDelete(doc.filename)}
              disabled={deletingFile === doc.filename}
              title="Delete document"
            >
              {deletingFile === doc.filename ? "..." : "✕"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DocumentList;
