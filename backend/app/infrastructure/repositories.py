import json
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import Conversation, Document, Message, User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, email: str, hashed_password: str, full_name: str) -> User:
        user = User(email=email, hashed_password=hashed_password, full_name=full_name)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(User))
        return result.scalar_one()


class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_user(self, user_id: int, limit: int = 50) -> Sequence[Conversation]:
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_id(self, conversation_id: int, user_id: int) -> Optional[Conversation]:
        result = await self.session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, title: str = "New Chat") -> Conversation:
        conv = Conversation(user_id=user_id, title=title)
        self.session.add(conv)
        await self.session.flush()
        await self.session.refresh(conv)
        return conv

    async def update_title(self, conversation: Conversation, title: str) -> Conversation:
        conversation.title = title
        await self.session.flush()
        return conversation

    async def delete(self, conversation: Conversation) -> None:
        await self.session.delete(conversation)

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Conversation))
        return result.scalar_one()


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_conversation(self, conversation_id: int) -> Sequence[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return result.scalars().all()

    async def create(
        self,
        conversation_id: int,
        role: str,
        content: str,
        sources: Optional[list[dict]] = None,
    ) -> Message:
        sources_json = json.dumps(sources) if sources else None
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=sources_json,
        )
        self.session.add(msg)
        await self.session.flush()
        await self.session.refresh(msg)
        return msg

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Message))
        return result.scalar_one()


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_user(self, user_id: int) -> Sequence[Document]:
        result = await self.session.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, document_id: int, user_id: int) -> Optional[Document]:
        result = await self.session.execute(
            select(Document).where(Document.id == document_id, Document.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self, user_id: int, filename: str, file_type: str, status: str = "processing"
    ) -> Document:
        doc = Document(user_id=user_id, filename=filename, file_type=file_type, status=status)
        self.session.add(doc)
        await self.session.flush()
        await self.session.refresh(doc)
        return doc

    async def update_processed(
        self, document: Document, chunk_count: int, chroma_ids: list[str], status: str = "ready"
    ) -> Document:
        document.chunk_count = chunk_count
        document.chroma_ids = json.dumps(chroma_ids)
        document.status = status
        await self.session.flush()
        return document

    async def update_failed(self, document: Document, status: str = "failed") -> Document:
        document.status = status
        await self.session.flush()
        return document

    async def delete(self, document: Document) -> None:
        await self.session.delete(document)

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Document))
        return result.scalar_one()
