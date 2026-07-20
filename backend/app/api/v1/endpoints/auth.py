from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token
from app.schemas.auth import Token

router = APIRouter()


@router.post(
    "/auth/login", response_model=Token, summary="Token generation login exchange skeleton"
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Authentication skeleton endpoint.
    Performs validation against developer default credentials.
    Do NOT use default credentials in production!
    """
    if form_data.username == "admin@sentinelx.local" and form_data.password == "admin_password":
        access_token = create_access_token(subject=form_data.username)
        return Token(access_token=access_token, token_type="bearer")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
