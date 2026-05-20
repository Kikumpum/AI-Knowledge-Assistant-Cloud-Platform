import json
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUser, DbSession
from app.api.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    MessageResponse,
)
from app.application.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


def _parse_sources(msg: Any) -> list | None:
    if msg.sources:
        try:
            return json.loads(msg.sources)
        except json.JSONDecodeError:
            return None
    return None


def _to_message_response(msg: Any) -> MessageResponse:
    return MessageResponse(
        id=msg.id,
        role=msg.role,
        content=msg.content,
        sources=_parse_sources(msg),
        created_at=msg.created_at,
    )


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(current_user: CurrentUser, db: DbSession):
    service = ChatService(db)
    return await service.list_conversations(current_user.id)


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    body: ConversationCreate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ChatService(db)
    return await service.create_conversation(current_user.id, body.title)


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: int,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ChatService(db)
    ok = await service.delete_conversation(current_user, conversation_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: int,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ChatService(db)
    messages = await service.get_messages(current_user.id, conversation_id)
    if messages is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv = await service.get_conversation(current_user.id, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return [_to_message_response(m) for m in messages]


@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: int,
    body: ChatRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ChatService(db)
    try:
        result = await service.send_message(current_user, conversation_id, body.message)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ChatResponse(
        message=_to_message_response(result["message"]),
        sources=result.get("sources", []),
    )
