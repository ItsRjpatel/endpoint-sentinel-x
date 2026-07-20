from uuid import UUID

from pydantic import BaseModel, Field


class AgentRegisterRequest(BaseModel):
    """Payload for registering a new agent endpoint using an enrollment token."""

    enrollment_token: str = Field(..., description="Active enrollment token secure value")
    hostname: str = Field(..., description="System hostname")
    os_platform: str = Field(..., description="Operating System Platform (e.g. windows, linux)")
    os_version: str = Field(..., description="Operating System Version")
    hardware_uuid: str = Field(..., description="Unique BIOS/System Hardware UUID")
    ip_address: str = Field(..., description="Local/Public IP address of the host")


class AgentRegisterResponse(BaseModel):
    """Response returned upon successful registration of an agent."""

    agent_id: UUID
    agent_secret: str
    lifecycle_state: str


class AgentHeartbeatRequest(BaseModel):
    """Payload sent by agents on periodic heartbeat signals."""

    status: str = Field("healthy", description="General status of the agent process")
    cpu_pct: float = Field(..., ge=0.0, le=100.0, description="CPU usage percent")
    ram_pct: float = Field(..., ge=0.0, le=100.0, description="RAM usage percent")


class AgentHeartbeatResponse(BaseModel):
    """Response returned to agents indicating heartbeat receipt."""

    status: str
    next_heartbeat_seconds: int = 30


class AgentRotateSecretResponse(BaseModel):
    """Response containing the newly rotated secret key."""

    new_agent_secret: str


class AgentConfigResponse(BaseModel):
    """Configuration mapping policy settings for the agent."""

    heartbeat_interval_seconds: int = 30
    policy: dict = Field(default_factory=dict)
