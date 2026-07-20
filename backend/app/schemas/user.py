from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.role import UserRole


class UserBase(BaseModel):
    """Base Pydantic schema for User."""

    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    role: UserRole
    is_active: bool = True
    is_verified: bool = False


class UserCreate(UserBase):
    """Schema for creating a new User."""

    organization_id: int
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating an existing User."""

    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    role: UserRole | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    password: str | None = Field(None, min_length=8)


class UserResponse(UserBase):
    """Response schema for returning User details, hiding sensitive fields like password_hash."""

    id: int
    uuid: UUID
    organization_id: int
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
