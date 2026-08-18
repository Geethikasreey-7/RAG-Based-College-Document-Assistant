from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier")
    text: str = Field(..., description="Clean text content for the chunk")
    source_filename: str = Field(..., description="Original source filename")
    page_number: int = Field(..., description="Page number the chunk belongs to")
    chunk_index: int = Field(..., description="Chunk order within the page")


class DocumentProcessingResult(BaseModel):
    filename: str
    page_count: int
    chunk_count: int
    status: str
