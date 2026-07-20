from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.security import decode_access_token
from app.schemas.auth import TokenPayload, UserRead

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserRead:
    """Authentication skeleton dependency.
    Decodes JWT token and parses sub details.
    Does not do database validation (auth skeleton).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenPayload(sub=username)
    except jwt.PyJWTError:
        raise credentials_exception from None

    # Return a validated skeleton user instead of querying database
    # (as per the "no business logic" requirement)
    return UserRead(
        id="usr_0000000000000001",
        email=token_data.sub or "admin@sentinelx.local",
        is_active=True,
        is_superuser=True,
    )


async def get_current_active_user(
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> UserRead:
    """Ensures user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
