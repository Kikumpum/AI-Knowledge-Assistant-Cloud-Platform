import json
import logging
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.rag_service import RAGService
from app.core.config import get_settings
from app.infrastructure.models import Conversation, Message, User
from app.infrastructure.repositories import ConversationRepository, MessageRepository

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.conv_repo = ConversationRepository(session)
        self.msg_repo = MessageRepository(session)
        self.rag = RAGService()

    async def list_conversations(self, user_id: int) -> list[Conversation]:
        return list(await self.conv_repo.list_by_user(user_id))

    async def get_conversation(self, user_id: int, conversation_id: int) -> Optional[Conversation]:
        return await self.conv_repo.get_by_id(conversation_id, user_id)

    async def create_conversation(self, user_id: int, title: str = "New Chat") -> Conversation:
        return await self.conv_repo.create(user_id, title)

    async def delete_conversation(self, user: User, conversation_id: int) -> bool:
        conv = await self.conv_repo.get_by_id(conversation_id, user.id)
        if not conv:
            return False
        await self.conv_repo.delete(conv)
        return True

    async def get_messages(self, user_id: int, conversation_id: int) -> list[Message]:
        conv = await self.conv_repo.get_by_id(conversation_id, user_id)
        if not conv:
            return []
        return list(await self.msg_repo.list_by_conversation(conversation_id))

    async def send_message(
        self,
        user: User,
        conversation_id: int,
        content: str,
    ) -> dict[str, Any]:
        conv = await self.conv_repo.get_by_id(conversation_id, user.id)
        if not conv:
            raise ValueError("Conversation not found")

        await self.msg_repo.create(conversation_id, "user", content)

        history = await self.msg_repo.list_by_conversation(conversation_id)
        history_pairs = [
            {"role": m.role, "content": m.content}
            for m in history[:-1]
            if m.role in ("user", "assistant")
        ][-6:]

        rag_result = await self.rag.generate_response(
            query=content,
            user_id=user.id,
            history=history_pairs,
        )

        assistant_msg = await self.msg_repo.create(
            conversation_id,
            "assistant",
            rag_result["answer"],
            sources=rag_result.get("sources"),
        )

        if conv.title == "New Chat" and len(content) > 0:
            title = content[:60] + ("..." if len(content) > 60 else "")
            await self.conv_repo.update_title(conv, title)

        return {
            "message": assistant_msg,
            "sources": rag_result.get("sources", []),
        }


class MonitoringService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_stats(self) -> dict[str, Any]:
        from app.infrastructure.repositories import (
            ConversationRepository,
            DocumentRepository,
            MessageRepository,
            UserRepository,
        )
        from app.infrastructure.vector_store import VectorStoreService

        settings = get_settings()
        chroma_ok = VectorStoreService.get_instance().health_check()

        return {
            "users": await UserRepository(self.session).count(),
            "conversations": await ConversationRepository(self.session).count(),
            "messages": await MessageRepository(self.session).count(),
            "documents": await DocumentRepository(self.session).count(),
            "services": {
                "database": "healthy",
                "chromadb": "healthy" if chroma_ok else "unhealthy",
                "embedding_model": settings.embedding_model,
            },
            "app": {
                "name": settings.app_name,
                "environment": settings.app_env,
            },
        }
