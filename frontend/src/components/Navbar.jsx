import React from "react";
import "../styles/Navbar.css";

export const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-logo">
          <span className="logo-icon">📄</span>
          <span className="logo-text">RAG Chatbot</span>
        </div>
        <div className="navbar-info">
          <span className="navbar-tagline">Semantic search & AI-powered answers</span>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
