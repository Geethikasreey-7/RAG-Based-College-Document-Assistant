from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    title: str | None = Field(default=None, description="Optional conversation title")


class ConversationResponse(BaseModel):
    conversation_id: str = Field(..., description="Unique conversation identifier")
    title: str = Field(..., description="Conversation title")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class MessageCreate(BaseModel):
    role: Literal["user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., min_length=1, description="Message content")


class MessageResponse(BaseModel):
    message_id: str = Field(..., description="Unique message identifier")
    conversation_id: str = Field(..., description="Conversation identifier")
    role: Literal["user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., description="Message text")
    created_at: str = Field(..., description="Message creation timestamp")


class ConversationDetailResponse(BaseModel):
    conversation_id: str = Field(..., description="Unique conversation identifier")
    title: str = Field(..., description="Conversation title")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    messages: list[MessageResponse] = Field(default_factory=list, description="Messages in this conversation")
