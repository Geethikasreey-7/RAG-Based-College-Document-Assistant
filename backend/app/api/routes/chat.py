from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.config import CHAT_HISTORY_LIMIT
from app.services.conversation_service import get_recent_messages
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question to answer using document context")
    conversation_id: str | None = Field(default=None, description="Optional conversation identifier to include recent chat history")


class SourceInfo(BaseModel):
    filename: str
    page: int


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceInfo]


@router.post("")
async def chat(request: ChatRequest) -> ChatResponse:
    rag = RAGService()
    conversation_history = []

    if request.conversation_id:
        conversation_history = [
            {"role": message["role"], "content": message["content"]}
            for message in get_recent_messages(request.conversation_id, limit=CHAT_HISTORY_LIMIT)
        ]

    try:
        rag_response = rag.generate(request.question, conversation_history=conversation_history)
    except ValueError as exc:
        logger.exception("RAG generation failed for question: %s", request.question)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.exception("Unexpected error during RAG generation: %s", request.question)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate an answer.") from exc

    sources = [SourceInfo(filename=source.filename, page=source.page) for source in rag_response.sources]

    return ChatResponse(question=request.question, answer=rag_response.answer, sources=sources)
