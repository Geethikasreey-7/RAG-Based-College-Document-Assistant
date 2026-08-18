import React, { useState } from "react";
import { documentAPI } from "../services/api";
import "../styles/DocumentUpload.css";

export const DocumentUpload = ({ onUploadSuccess, onUploadError }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleFileSelect = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setSelectedFile(null);
      setErrorMessage("Please select a PDF file.");
      return;
    }

    setSelectedFile(file);
    setErrorMessage("");
    setSuccessMessage("");
    setUploadProgress(0);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setErrorMessage("Choose a PDF before uploading.");
      return;
    }

    setIsLoading(true);
    setErrorMessage("");
    setSuccessMessage("");
    setUploadProgress(0);

    try {
      const result = await documentAPI.upload(selectedFile, (progressEvent) => {
        const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
        setUploadProgress(progress);
      });

      setSuccessMessage(`✓ "${result.filename}" processed successfully (${result.chunk_count} chunks)`);
      setSelectedFile(null);
      setUploadProgress(0);
      onUploadSuccess(result);

      setTimeout(() => setSuccessMessage(""), 5000);
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || "Upload failed";
      setErrorMessage(`✗ ${errorMsg}`);
      onUploadError(error);
    } finally {
      setIsLoading(false);
      const input = document.getElementById("pdf-input");
      if (input) input.value = "";
    }
  };

  return (
    <div className="document-upload">
      <div className="upload-area">
        <label htmlFor="pdf-input" className="upload-label">
          <div className="upload-content">
            <span className="upload-icon">📤</span>
            <span className="upload-text">Select a PDF</span>
            <span className="upload-hint">Supports single-file uploads</span>
          </div>
          <input
            id="pdf-input"
            type="file"
            accept=".pdf"
            onChange={handleFileSelect}
            disabled={isLoading}
            className="upload-input"
          />
        </label>
      </div>

      {selectedFile && (
        <div className="selected-file">
          <span className="selected-file-label">Selected:</span>
          <span className="selected-file-name">{selectedFile.name}</span>
        </div>
      )}

      <div className="upload-actions">
        <button
          type="button"
          className="upload-button"
          onClick={handleUpload}
          disabled={!selectedFile || isLoading}
        >
          {isLoading ? "Uploading..." : "Upload PDF"}
        </button>
      </div>

      {isLoading && (
        <div className="upload-progress">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
          </div>
          <span className="progress-text">{uploadProgress}%</span>
        </div>
      )}

      {errorMessage && <div className="message error-message">{errorMessage}</div>}
      {successMessage && <div className="message success-message">{successMessage}</div>}
    </div>
  );
};

export default DocumentUpload;
