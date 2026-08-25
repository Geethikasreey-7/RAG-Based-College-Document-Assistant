from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.config import RELEVANCE_THRESHOLD, TOP_K
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language query to search documents")

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Query cannot be empty or whitespace only.")
        return value.strip()


class SearchResult(BaseModel):
    chunk_id: str
    text: str
    relevance_score: float
    source_filename: str
    page_number: int


class SearchResponse(BaseModel):
    query: str
    chunk_count: int
    results: list[SearchResult]


@router.post("")
async def search(request: SearchRequest) -> SearchResponse:
    retrieval = RetrievalService(top_k=TOP_K, relevance_threshold=RELEVANCE_THRESHOLD)

    try:
        retrieved_chunks = retrieval.search(request.query)
    except ValueError as exc:
        logger.exception("Search failed for query: %s", request.query)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.exception("Unexpected error during search: %s", request.query)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search operation failed.") from exc

    results = [
        SearchResult(
            chunk_id=chunk.chunk_id,
            text=chunk.text,
            relevance_score=chunk.relevance_score,
            source_filename=chunk.source_filename,
            page_number=chunk.page_number,
        )
        for chunk in retrieved_chunks
    ]

    return SearchResponse(query=request.query, chunk_count=len(results), results=results)
