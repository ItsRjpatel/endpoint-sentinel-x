from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class FleetOverviewStats(BaseModel):
    total_endpoints: int
    online: int
    offline: int
    active_alerts: int
    critical_alerts: int
    pending_commands: int
    security_score: int
    compliance_score: int

class HealthDataPoint(BaseModel):
    time: str
    cpu: int
    memory: int
    disk: int
    network_in: int
    network_out: int

class ActivityEvent(BaseModel):
    id: str
    type: str
    message: str
    timestamp: str

class SecurityOverview(BaseModel):
    protected: int
    at_risk: int
    critical: int
    unknown: int
    score: int
    compliance_progress: int

class DashboardAlert(BaseModel):
    id: str
    severity: str
    endpoint: str
    message: str
    timestamp: str
    status: str

class DashboardCommand(BaseModel):
    id: str
    endpoint: str
    command: str
    status: str
    executed_at: str
    duration_ms: Optional[int]
