from datetime import UTC, datetime, timedelta
from typing import List

from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.command import Command
from app.db.models.endpoint import Endpoint
from app.db.models.security_event import SecurityEvent
from app.db.models.performance_history import PerformanceHistory
from app.schemas.dashboard import (
    ActivityEvent,
    DashboardAlert,
    DashboardCommand,
    FleetOverviewStats,
    HealthDataPoint,
    SecurityOverview,
)
from app.services.security import SecurityService


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_fleet_overview(self) -> FleetOverviewStats:
        total_stmt = select(func.count(Endpoint.id))
        total_endpoints = (await self.db.execute(total_stmt)).scalar_one()

        online_stmt = select(func.count(Endpoint.id)).where(Endpoint.lifecycle_state == "ONLINE")
        online = (await self.db.execute(online_stmt)).scalar_one()

        offline = total_endpoints - online

        alerts_stmt = select(func.count(SecurityEvent.id)).where(SecurityEvent.severity.in_(["high", "critical"]))
        active_alerts = (await self.db.execute(alerts_stmt)).scalar_one()

        crit_alerts_stmt = select(func.count(SecurityEvent.id)).where(SecurityEvent.severity == "critical")
        critical_alerts = (await self.db.execute(crit_alerts_stmt)).scalar_one()

        cmd_stmt = select(func.count(Command.id)).where(Command.status.in_(["PENDING", "SENT"]))
        pending_commands = (await self.db.execute(cmd_stmt)).scalar_one()

        sec_service = SecurityService(self.db)
        sec_summary = await sec_service.get_fleet_summary()

        return FleetOverviewStats(
            total_endpoints=total_endpoints,
            online=online,
            offline=offline,
            active_alerts=active_alerts,
            critical_alerts=critical_alerts,
            pending_commands=pending_commands,
            security_score=int(sec_summary.average_score),
            compliance_score=95,  # Placeholder until compliance service is built
        )

    async def get_fleet_health(self) -> List[HealthDataPoint]:
        now = datetime.now(UTC)
        twenty_four_hours_ago = now - timedelta(hours=24)
        
        # We group by hour and average the performance metrics
        stmt = (
            select(
                func.date_trunc('hour', PerformanceHistory.timestamp).label("hour"),
                func.avg(PerformanceHistory.cpu_usage_percent).label("cpu"),
                func.avg(PerformanceHistory.memory_usage_percent).label("memory"),
                func.avg(PerformanceHistory.disk_usage_percent).label("disk"),
                func.avg(PerformanceHistory.network_in_bytes).label("net_in"),
                func.avg(PerformanceHistory.network_out_bytes).label("net_out"),
            )
            .where(PerformanceHistory.timestamp >= twenty_four_hours_ago)
            .group_by("hour")
            .order_by("hour")
        )
        results = (await self.db.execute(stmt)).all()

        data_points = []
        for row in results:
            data_points.append(HealthDataPoint(
                time=row.hour.isoformat() if row.hour else now.isoformat(),
                cpu=int(row.cpu or 0),
                memory=int(row.memory or 0),
                disk=int(row.disk or 0),
                network_in=int((row.net_in or 0) / 1024),  # convert to KB
                network_out=int((row.net_out or 0) / 1024),
            ))
            
        # If no data, return a default point so UI doesn't crash
        if not data_points:
            data_points.append(HealthDataPoint(
                time=now.isoformat(),
                cpu=0, memory=0, disk=0, network_in=0, network_out=0
            ))
            
        return data_points

    async def get_activity_feed(self) -> List[ActivityEvent]:
        # Merge security events and recent endpoints for a cohesive feed
        stmt = select(SecurityEvent, Endpoint).join(Endpoint, Endpoint.id == SecurityEvent.endpoint_id).order_by(desc(SecurityEvent.timestamp)).limit(20)
        results = (await self.db.execute(stmt)).all()
        
        feed = []
        for event, endpoint in results:
            feed.append(ActivityEvent(
                id=str(event.uuid),
                type="error" if event.severity == "critical" else "warning" if event.severity == "high" else "info",
                message=f"[{endpoint.hostname}] {event.event_type}: {event.description}",
                timestamp=event.timestamp.isoformat()
            ))
        return feed

    async def get_security_overview(self) -> SecurityOverview:
        sec_service = SecurityService(self.db)
        summary = await sec_service.get_fleet_summary()
        return SecurityOverview(
            protected=summary.protected_endpoints,
            at_risk=summary.high_risk_endpoints,
            critical=summary.unprotected_endpoints,
            unknown=0,
            score=int(summary.average_score),
            compliance_progress=95,
        )

    async def get_recent_alerts(self) -> List[DashboardAlert]:
        stmt = select(SecurityEvent, Endpoint).join(Endpoint, Endpoint.id == SecurityEvent.endpoint_id).where(SecurityEvent.severity.in_(["high", "critical"])).order_by(desc(SecurityEvent.timestamp)).limit(10)
        results = (await self.db.execute(stmt)).all()
        alerts = []
        for event, endpoint in results:
            alerts.append(DashboardAlert(
                id=str(event.uuid),
                severity=event.severity,
                endpoint=endpoint.hostname,
                message=event.description,
                timestamp=event.timestamp.isoformat(),
                status="active"
            ))
        return alerts

    async def get_recent_commands(self) -> List[DashboardCommand]:
        stmt = select(Command, Endpoint).join(Endpoint, Endpoint.id == Command.endpoint_id).order_by(desc(Command.created_at)).limit(10)
        results = (await self.db.execute(stmt)).all()
        commands = []
        for cmd, endpoint in results:
            commands.append(DashboardCommand(
                id=str(cmd.id),
                endpoint=endpoint.hostname,
                command=cmd.command_type,
                status=cmd.status.lower(),
                executed_at=cmd.created_at.isoformat(),
                duration_ms=cmd.execution_duration
            ))
        return commands
