from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrganizationBase(BaseModel):
    """Base Pydantic schema for Organization."""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    is_active: bool = True


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new Organization."""

    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an existing Organization."""

    name: str | None = Field(None, min_length=1, max_length=100)
    slug: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    is_active: bool | None = None


class OrganizationResponse(OrganizationBase):
    """Schema for returning an Organization response, excluding internal DB fields where needed."""

    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
