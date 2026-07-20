from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
)
from app.db.models.user import User
from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.repositories.user import UserRepository
from app.schemas.auth import Token
from app.schemas.user import UserResponse

router = APIRouter()


@router.post("/auth/login", response_model=Token, summary="OAuth2 compatible token login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Authenticates a user via username or email and returns access & refresh tokens."""
    repo = UserRepository(db)
    user = await repo.get_by_email(form_data.username)
    if not user:
        user = await repo.get_by_username(form_data.username)

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is disabled",
        )

    access_token = create_access_token(subject=str(user.uuid))
    refresh_token = create_refresh_token(subject=str(user.uuid))
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/auth/logout", summary="Log out active session")
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Logs out user by invalidating their token. In a stateless context, returns confirmation."""
    return {"detail": "Logged out successfully"}


@router.post("/auth/refresh", response_model=Token, summary="Refresh JWT access token")
async def refresh_access_token(
    refresh_token: Annotated[str, Body(..., embed=True)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Validates refresh token and issues a new access token & refresh token."""
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_uuid_str = payload.get("sub")
    if not user_uuid_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    try:
        user_uuid = UUID(user_uuid_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from None

    repo = UserRepository(db)
    user = await repo.get_by_uuid(user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is disabled",
        )

    access_token = create_access_token(subject=str(user.uuid))
    new_refresh_token = create_refresh_token(subject=str(user.uuid))
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.get("/auth/me", response_model=UserResponse, summary="Get current user details")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    """Returns details of the currently authenticated active user."""
    return current_user
