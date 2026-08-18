"""Application configuration.

This module loads environment variables and centralizes runtime settings.
It intentionally avoids hardcoded secrets.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

APP_NAME = os.getenv("APP_NAME", "RAG Document Chatbot")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
VECTORSTORE_TYPE = os.getenv("VECTORSTORE_TYPE", "faiss")
VECTORSTORE_PATH = os.getenv("VECTORSTORE_PATH", str(BASE_DIR / "data" / "vectorstore"))
UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIRECTORY", str(BASE_DIR / "data" / "documents"))
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "chat_history.db"))
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
TOP_K = int(os.getenv("TOP_K", "5"))
RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.0"))
MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "12000"))
CHAT_HISTORY_LIMIT = int(os.getenv("CHAT_HISTORY_LIMIT", "5"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
