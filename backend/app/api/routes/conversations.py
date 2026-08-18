from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.models.conversation import ConversationCreate, ConversationDetailResponse, ConversationResponse, MessageCreate, MessageResponse
from app.services.conversation_service import add_message, conversation_exists, create_conversation, get_conversation, list_conversations

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("")
async def create_new_conversation(payload: ConversationCreate | None = None) -> ConversationDetailResponse:
    title = None
    if payload is not None:
        title = payload.title

    conversation = create_conversation(title)
    return ConversationDetailResponse(
        conversation_id=conversation["conversation_id"],
        title=conversation["title"],
        created_at=conversation["created_at"],
        updated_at=conversation["updated_at"],
        messages=[],
    )


@router.get("")
async def list_all_conversations() -> list[ConversationResponse]:
    conversations = list_conversations()
    return [
        ConversationResponse(
            conversation_id=item["conversation_id"],
            title=item["title"],
            created_at=item["created_at"],
            updated_at=item["updated_at"],
        )
        for item in conversations
    ]


@router.get("/{conversation_id}")
async def get_conversation_detail(conversation_id: str) -> ConversationDetailResponse:
    conversation = get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    return ConversationDetailResponse(
        conversation_id=conversation["conversation_id"],
        title=conversation["title"],
        created_at=conversation["created_at"],
        updated_at=conversation["updated_at"],
        messages=[
            MessageResponse(
                message_id=item["message_id"],
                conversation_id=item["conversation_id"],
                role=item["role"],
                content=item["content"],
                created_at=item["created_at"],
            )
            for item in conversation["messages"]
        ],
    )


@router.post("/{conversation_id}/messages")
async def create_message(conversation_id: str, payload: MessageCreate) -> MessageResponse:
    if not conversation_exists(conversation_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    message = add_message(conversation_id, payload.role, payload.content)
    return MessageResponse(
        message_id=message["message_id"],
        conversation_id=message["conversation_id"],
        role=message["role"],
        content=message["content"],
        created_at=message["created_at"],
    )
