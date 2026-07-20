from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models.user import User
from app.dependencies.database import get_db
from app.models.role import UserRole
from app.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Decodes JWT access token, parses user UUID, and validates user exists in database."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_uuid_str: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        if user_uuid_str is None or token_type != "access":
            raise credentials_exception
        user_uuid = UUID(user_uuid_str)
    except jwt.ExpiredSignatureError:
        raise expired_exception from None
    except (jwt.InvalidTokenError, ValueError):
        raise credentials_exception from None

    repo = UserRepository(db)
    user = await repo.get_by_uuid(user_uuid)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensures that the authenticated user account is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is disabled",
        )
    return current_user


class RoleChecker:
    """Dependency helper to enforce specific user roles."""

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user


def require_role(allowed_roles: list[UserRole]) -> RoleChecker:
    """Returns a role verification dependency."""
    return RoleChecker(allowed_roles)


async def require_super_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Shorthand dependency requiring the SUPER_ADMIN role."""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin role required",
        )
    return current_user


async def require_org_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Shorthand dependency requiring either SUPER_ADMIN or ORGANIZATION_ADMIN role."""
    if current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ORGANIZATION_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization Admin role required",
        )
    return current_user
