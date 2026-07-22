from datetime import datetime

from pydantic import BaseModel


class SecurityRecommendation(BaseModel):
    id: str
    title: str
    description: str
    severity: str  # "high", "medium", "low"
    category: str  # "defender", "firewall", "bitlocker", "os"


class SecurityScore(BaseModel):
    total_score: float
    max_score: float = 100.0
    defender_score: float
    firewall_score: float
    bitlocker_score: float
    tpm_score: float
    secure_boot_score: float
    updates_score: float


class FleetSecuritySummary(BaseModel):
    average_score: float
    total_endpoints: int
    protected_endpoints: int
    unprotected_endpoints: int
    high_risk_endpoints: int
    pending_updates_endpoints: int
    recent_security_events: int


class EndpointSecuritySummary(BaseModel):
    endpoint_id: int
    score: SecurityScore
    recommendations: list[SecurityRecommendation]
    last_scan: datetime | None = None


class SecurityEventSchema(BaseModel):
    id: int
    endpoint_id: int
    event_type: str
    severity: str
    description: str
    timestamp: datetime

    class Config:
        from_attributes = True


class SecurityTimelineResponse(BaseModel):
    events: list[SecurityEventSchema]
    total: int
