import React from "react";
import "../styles/SourceReferences.css";

export const SourceReferences = ({ sources }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="source-references">
      <div className="sources-header">📚 Sources</div>
      <ul className="sources-list">
        {sources.map((source, index) => (
          <li key={index} className="source-item">
            <span className="source-file">{source.filename}</span>
            <span className="source-page">Page {source.page}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SourceReferences;
