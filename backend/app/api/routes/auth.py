from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUser, DbSession
from app.api.schemas import (
    RefreshRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.application.auth_service import AuthService
from app.infrastructure.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegister, db: DbSession) -> User:
    service = AuthService(db)
    try:
        user = await service.register(body.email, body.password, body.full_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin, db: DbSession) -> TokenResponse:
    service = AuthService(db)
    user = await service.authenticate(body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    tokens = service.issue_tokens(user)
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=dict)
async def refresh(body: RefreshRequest, db: DbSession) -> dict:
    service = AuthService(db)
    access = await service.refresh_access_token(body.refresh_token)
    if not access:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return {"access_token": access, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser) -> User:
    return current_user
