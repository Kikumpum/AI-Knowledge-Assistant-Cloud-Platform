from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.infrastructure.models import User
from app.infrastructure.repositories import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def register(self, email: str, password: str, full_name: str) -> User:
        email = email.lower().strip()
        existing = await self.repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")
        return await self.repo.create(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name.strip(),
        )

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.repo.get_by_email(email.lower().strip())
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def issue_tokens(self, user: User) -> dict[str, str]:
        subject = str(user.id)
        return {
            "access_token": create_access_token(subject),
            "refresh_token": create_refresh_token(subject),
            "token_type": "bearer",
        }

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        try:
            user = await self.repo.get_by_id(int(user_id))
        except (TypeError, ValueError):
            return None
        if not user or not user.is_active:
            return None
        return create_access_token(str(user.id))
