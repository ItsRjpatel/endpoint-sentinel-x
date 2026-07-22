from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.security import (
    EndpointSecuritySummary,
    FleetSecuritySummary,
    SecurityTimelineResponse,
)
from app.services.security import SecurityService

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/fleet-summary", response_model=FleetSecuritySummary, summary="Get fleet security summary")
async def get_fleet_summary(db: Annotated[AsyncSession, Depends(get_db)]):
    service = SecurityService(db)
    return await service.get_fleet_summary()


@router.get(
    "/endpoints/{endpoint_id}/summary",
    response_model=EndpointSecuritySummary,
    summary="Get endpoint security summary",
)
async def get_endpoint_summary(
    endpoint_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    service = SecurityService(db)
    return await service.get_endpoint_summary(endpoint_id)


@router.get("/timeline", response_model=SecurityTimelineResponse, summary="Get security timeline")
async def get_security_timeline(
    db: Annotated[AsyncSession, Depends(get_db)], limit: int = 50
):
    service = SecurityService(db)
    return await service.get_timeline(limit=limit)
