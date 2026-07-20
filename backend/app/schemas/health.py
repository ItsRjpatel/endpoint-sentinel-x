from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="Overall platform status (healthy/unhealthy)")
    version: str = Field(..., description="API service configuration version")
    services: dict[str, str] = Field(
        ..., description="Nested status logs for dependencies (database, cache, etc.)"
    )
