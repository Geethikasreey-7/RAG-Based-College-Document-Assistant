"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router
from app.api.routes.conversations import router as conversations_router
from app.api.routes.documents import router as documents_router
from app.api.routes.search import router as search_router
from app.services.conversation_service import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

app = FastAPI(title="RAG Document Chatbot API", version="0.1.0")

# Configure CORS to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    init_db()


app.include_router(documents_router)
app.include_router(search_router)
app.include_router(conversations_router)
app.include_router(chat_router)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "message": "API is running"}
