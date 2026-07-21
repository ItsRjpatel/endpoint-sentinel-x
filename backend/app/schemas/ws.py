import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.command import CommandResponse


class WSEnvelope(BaseModel):
    """
    Strict envelope for all WebSocket messages.
    """
    schema_version: int = Field(1, description="Version of the WebSocket protocol schema")
    event: str = Field(..., description="Event type string")
    request_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique ID for message tracing"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="UTC timestamp of the message"
    )
    payload: dict | CommandResponse | None = Field(default=None, description="Event-specific payload")

