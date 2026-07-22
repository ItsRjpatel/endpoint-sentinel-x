import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PolicyVersionResponse(BaseModel):
    """Schema for policy version response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: uuid.UUID
    policy_id: int
    version: int
    configuration: dict
    change_summary: str | None = None
    created_at: datetime
    updated_at: datetime


class PolicyAssignmentCreate(BaseModel):
    """Schema to assign a policy to an endpoint."""
    endpoint_id: int


class PolicyAssignmentResponse(BaseModel):
    """Schema for policy assignment response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: uuid.UUID
    policy_id: int
    endpoint_id: int
    assigned_by_id: int | None = None
    created_at: datetime
    updated_at: datetime


class PolicyCreate(BaseModel):
    """Schema for creating a new policy."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    category: str = Field(..., description="E.g., security, compliance, operational")
    enabled: bool = True
    priority: int = 100
    configuration: dict = Field(..., description="JSON payload of the initial policy configuration")


class PolicyUpdate(BaseModel):
    """Schema for updating an existing policy. Triggers a new version if configuration changes."""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    category: str | None = None
    enabled: bool | None = None
    priority: int | None = None
    configuration: dict | None = Field(default=None, description="New configuration to create a new version")
    change_summary: str | None = Field(default=None, description="Summary of the changes for the new version")


class PolicyResponse(BaseModel):
    """Full representation of a policy, including versions and assignments."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: uuid.UUID
    organization_id: int
    name: str
    description: str | None
    category: str
    enabled: bool
    priority: int
    current_version: int
    created_by_id: int | None
    created_at: datetime
    updated_at: datetime

    versions: list[PolicyVersionResponse] = []
    assignments: list[PolicyAssignmentResponse] = []


class PolicyListResponse(BaseModel):
    """Simplified policy representation for list views."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: uuid.UUID
    organization_id: int
    name: str
    description: str | None
    category: str
    enabled: bool
    priority: int
    current_version: int
    created_at: datetime
    updated_at: datetime
