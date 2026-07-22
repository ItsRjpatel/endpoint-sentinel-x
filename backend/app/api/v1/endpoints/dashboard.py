from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.dashboard import (
    ActivityEvent,
    DashboardAlert,
    DashboardCommand,
    FleetOverviewStats,
    HealthDataPoint,
    SecurityOverview,
)
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", dependencies=[Depends(get_current_user)])


@router.get("/fleet-overview", response_model=FleetOverviewStats)
async def get_fleet_overview(db: Annotated[AsyncSession, Depends(get_db)]):
    service = DashboardService(db)
    return await service.get_fleet_overview()


@router.get("/fleet-health", response_model=list[HealthDataPoint])
async def get_fleet_health(db: Annotated[AsyncSession, Depends(get_db)]):
    service = DashboardService(db)
    return await service.get_fleet_health()


@router.get("/activity-feed", response_model=list[ActivityEvent])
async def get_activity_feed(db: Annotated[AsyncSession, Depends(get_db)]):
    service = DashboardService(db)
    return await service.get_activity_feed()


@router.get("/security-overview", response_model=SecurityOverview)
async def get_security_overview(db: Annotated[AsyncSession, Depends(get_db)]):
    service = DashboardService(db)
    return await service.get_security_overview()


@router.get("/recent-alerts", response_model=list[DashboardAlert])
async def get_recent_alerts(db: Annotated[AsyncSession, Depends(get_db)]):
    service = DashboardService(db)
    return await service.get_recent_alerts()


@router.get("/recent-commands", response_model=list[DashboardCommand])
async def get_recent_commands(db: Annotated[AsyncSession, Depends(get_db)]):
    service = DashboardService(db)
    return await service.get_recent_commands()
