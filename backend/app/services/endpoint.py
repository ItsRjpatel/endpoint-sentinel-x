from datetime import UTC, datetime
from typing import List, Optional

from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.endpoint import Endpoint
from app.db.models.inventory_hardware import InventoryHardware
from app.db.models.inventory_os import InventoryOS
from app.db.models.security_event import SecurityEvent
from app.db.models.performance_history import PerformanceHistory
from app.schemas.endpoint import EndpointResponse, EndpointListResponse, EndpointDetailsResponse, OperatingSystemInfo
from app.services.security import SecurityService


class EndpointService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_endpoints(self, search: Optional[str] = None, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> EndpointListResponse:
        stmt = select(Endpoint).order_by(Endpoint.hostname)
        if status:
            stmt = stmt.where(func.lower(Endpoint.lifecycle_state) == status.lower())
        if search:
            stmt = stmt.where(Endpoint.hostname.ilike(f"%{search}%"))
        
        stmt = stmt.limit(limit).offset(offset)
        results = (await self.db.execute(stmt)).scalars().all()

        count_stmt = select(func.count(Endpoint.id))
        total = (await self.db.execute(count_stmt)).scalar_one()

        sec_service = SecurityService(self.db)

        endpoints = []
        for ep in results:
            score = await sec_service.calculate_security_score(ep.id)
            
            alerts_stmt = select(func.count(SecurityEvent.id)).where(SecurityEvent.endpoint_id == ep.id, SecurityEvent.severity.in_(["high", "critical"]))
            alerts_count = (await self.db.execute(alerts_stmt)).scalar_one()

            endpoints.append(EndpointResponse(
                id=str(ep.uuid),
                status=ep.lifecycle_state.lower(),
                hostname=ep.hostname,
                deviceType="desktop",  # default for now
                user=None,
                os=ep.os_platform,
                ipAddress=ep.ip_address,
                securityScore=int(score.total_score),
                compliance="compliant",
                lastSeen=ep.last_seen.isoformat() if ep.last_seen else datetime.now(UTC).isoformat(),
                alerts=alerts_count
            ))
            
        return EndpointListResponse(data=endpoints, total=total)

    async def get_endpoint_details(self, endpoint_uuid: str) -> EndpointDetailsResponse:
        # Find endpoint
        stmt = select(Endpoint).where(Endpoint.uuid == endpoint_uuid)
        ep = (await self.db.execute(stmt)).scalar_one_or_none()
        if not ep:
            raise ValueError(f"Endpoint not found: {endpoint_uuid}")

        sec_service = SecurityService(self.db)
        score = await sec_service.calculate_security_score(ep.id)
        
        alerts_stmt = select(func.count(SecurityEvent.id)).where(SecurityEvent.endpoint_id == ep.id, SecurityEvent.severity.in_(["high", "critical"]))
        alerts_count = (await self.db.execute(alerts_stmt)).scalar_one()

        hw_stmt = select(InventoryHardware).where(InventoryHardware.endpoint_id == ep.id).order_by(desc(InventoryHardware.created_at)).limit(1)
        hw = (await self.db.execute(hw_stmt)).scalar_one_or_none()
        
        os_stmt = select(InventoryOS).where(InventoryOS.endpoint_id == ep.id).order_by(desc(InventoryOS.created_at)).limit(1)
        os_info = (await self.db.execute(os_stmt)).scalar_one_or_none()

        perf_stmt = select(PerformanceHistory).where(PerformanceHistory.endpoint_id == ep.id).order_by(desc(PerformanceHistory.timestamp)).limit(1)
        perf = (await self.db.execute(perf_stmt)).scalar_one_or_none()

        return EndpointDetailsResponse(
            id=str(ep.uuid),
            status=ep.lifecycle_state.lower(),
            hostname=ep.hostname,
            deviceType="desktop",
            user=None,
            os=ep.os_platform,
            ipAddress=ep.ip_address,
            securityScore=int(score.total_score),
            compliance="compliant",
            lastSeen=ep.last_seen.isoformat() if ep.last_seen else datetime.now(UTC).isoformat(),
            alerts=alerts_count,
            
            manufacturer=hw.system_manufacturer if hw else "Unknown",
            model=hw.system_product_name if hw else "Unknown",
            serialNumber=hw.bios_serial_number if hw else "Unknown",
            assetTag="N/A",
            domain=ep.domain_workgroup or "WORKGROUP",
            macAddress="Unknown",
            
            operatingSystem=OperatingSystemInfo(
                name=os_info.caption if os_info else ep.os_platform,
                version=os_info.version if os_info else ep.os_version,
                build=os_info.build_number if os_info else "Unknown",
                architecture=os_info.os_architecture if os_info else "Unknown",
                installDate=os_info.install_date.isoformat() if os_info and os_info.install_date else datetime.now(UTC).isoformat()
            ),
            isolated=False,
            riskScore=int(100 - score.total_score),
            riskLevel="low" if score.total_score > 80 else "high",
            riskFactors=[],
            openAlertsCount=alerts_count,
            
            hardware={
                "cpu": hw.cpu_model if hw else "Unknown",
                "cores": hw.cpu_cores if hw else 0,
                "memory": hw.total_ram_bytes if hw else 0,
            },
            performance={
                "cpu": perf.cpu_usage_percent if perf else 0,
                "memory": perf.memory_usage_percent if perf else 0,
                "disk": perf.disk_usage_percent if perf else 0,
                "networkIn": perf.network_in_bytes if perf else 0,
                "networkOut": perf.network_out_bytes if perf else 0,
            },
            security={
                "score": int(score.total_score),
                "defender": score.defender_score > 0,
                "firewall": score.firewall_score > 0,
                "bitlocker": score.bitlocker_score > 0,
            },
            networkAdapters=[],
            software=[],
            updates=[],
            services=[],
            users=[],
            timeline=[]
        )
