from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class HardwareInfo(BaseModel):
    manufacturer: str
    model: str
    serialNumber: str
    cpu: str
    cores: int
    memory: int

class EndpointResponse(BaseModel):
    id: str
    status: str
    hostname: str
    deviceType: str
    user: Optional[str]
    os: str
    ipAddress: str
    securityScore: int
    compliance: str
    lastSeen: str
    alerts: int

class EndpointListResponse(BaseModel):
    data: List[EndpointResponse]
    total: int

class OperatingSystemInfo(BaseModel):
    name: str
    version: str
    build: str
    architecture: str
    installDate: str

class RiskFactor(BaseModel):
    label: str
    weight: str

class EndpointDetailsResponse(EndpointResponse):
    manufacturer: str
    model: str
    serialNumber: str
    assetTag: str
    domain: str
    macAddress: str
    operatingSystem: OperatingSystemInfo
    isolated: bool
    riskScore: int
    riskLevel: str
    riskFactors: List[RiskFactor]
    openAlertsCount: int
    
    hardware: dict
    performance: dict
    security: dict
    networkAdapters: list
    software: list
    updates: list
    services: list
    users: list
    timeline: list
