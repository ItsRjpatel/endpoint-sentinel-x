import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommandCreate(BaseModel):
    """Payload to create a new command via the REST API."""
    command_type: str = Field(..., description="The type of command to run (e.g., Ping)")
    command_version: int = Field(1, description="Version of the command")
    parameters: dict | None = Field(default=None, description="Optional parameters for the command")


class CommandResponse(BaseModel):
    """Response model for a Command."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    endpoint_id: uuid.UUID
    command_type: str
    command_version: int
    schema_version: int
    parameters: dict | None
    status: str
    created_at: datetime
    queued_at: datetime | None
    sent_at: datetime | None
    acknowledged_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    retry_count: int
    execution_duration: int | None
    result_json: dict | None
    error: str | None


class CommandUpdateStatus(BaseModel):
    """Payload to update the status of a command internally or via webhook/WS."""
    status: str
    timestamp: datetime
    error: str | None = None
    result_json: dict | None = None
    execution_duration: int | None = None
