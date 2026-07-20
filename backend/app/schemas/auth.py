from pydantic import BaseModel, ConfigDict, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None
    exp: int | None = None


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
