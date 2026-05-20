from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserEntity:
    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime


@dataclass
class ConversationEntity:
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime


@dataclass
class MessageEntity:
    id: int
    conversation_id: int
    role: str
    content: str
    sources: Optional[str]
    created_at: datetime


@dataclass
class DocumentEntity:
    id: int
    user_id: int
    filename: str
    file_type: str
    chunk_count: int
    status: str
    created_at: datetime
