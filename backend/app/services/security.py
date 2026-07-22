import uuid
from datetime import UTC, datetime

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.endpoint import Endpoint
from app.db.models.inventory_bitlocker_volume import InventoryBitlockerVolume
from app.db.models.inventory_firewall_profile import InventoryFirewallProfile
from app.db.models.inventory_security_status import InventorySecurityStatus
from app.db.models.inventory_windows_update import InventoryWindowsUpdate
from app.db.models.security_event import SecurityEvent
from app.schemas.security import (
    EndpointSecuritySummary,
    FleetSecuritySummary,
    SecurityEventSchema,
    SecurityRecommendation,
    SecurityScore,
    SecurityTimelineResponse,
)


class SecurityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_fleet_summary(self) -> FleetSecuritySummary:
        # Get total endpoints
        total_stmt = select(func.count(Endpoint.id))
        total_endpoints = (await self.db.execute(total_stmt)).scalar_one()

        # Get all security statuses
        status_stmt = select(InventorySecurityStatus)
        statuses = (await self.db.execute(status_stmt)).scalars().all()

        protected = 0
        high_risk = 0
        total_score = 0.0

        # Calculate scores and risks dynamically
        for status in statuses:
            score_data = await self.calculate_security_score(status.endpoint_id)
            total_score += score_data.total_score

            # Simple heuristic: if score > 80 it's protected, < 50 high risk
            if score_data.total_score >= 80:
                protected += 1
            elif score_data.total_score < 50:
                high_risk += 1

        unprotected = total_endpoints - protected

        # Pending updates: count rows whose installation state indicates they are not installed.
        updates_stmt = select(func.count(InventoryWindowsUpdate.id)).where(
            InventoryWindowsUpdate.installation_state.in_(["NotInstalled", "Pending", "Unknown"])
        )
        pending_updates = (await self.db.execute(updates_stmt)).scalar_one()

        # Recent events (last 24h)
        yesterday = datetime.now(UTC).replace(day=datetime.now(UTC).day - 1)
        events_stmt = select(func.count(SecurityEvent.id)).where(SecurityEvent.timestamp >= yesterday)
        recent_events = (await self.db.execute(events_stmt)).scalar_one()

        return FleetSecuritySummary(
            average_score=total_score / max(len(statuses), 1),
            total_endpoints=total_endpoints,
            protected_endpoints=protected,
            unprotected_endpoints=unprotected,
            high_risk_endpoints=high_risk,
            pending_updates_endpoints=pending_updates,
            recent_security_events=recent_events,
        )

    async def get_endpoint_summary(self, endpoint_id: int) -> EndpointSecuritySummary:
        score = await self.calculate_security_score(endpoint_id)
        recommendations = await self.generate_recommendations(endpoint_id)

        # Get last scan time from defender
        stmt = select(InventorySecurityStatus.defender_last_quick_scan).where(InventorySecurityStatus.endpoint_id == endpoint_id)
        last_scan = (await self.db.execute(stmt)).scalar_one_or_none()

        return EndpointSecuritySummary(
            endpoint_id=endpoint_id,
            score=score,
            recommendations=recommendations,
            last_scan=last_scan
        )

    async def calculate_security_score(self, endpoint_id: int) -> SecurityScore:
        stmt = select(InventorySecurityStatus).where(InventorySecurityStatus.endpoint_id == endpoint_id)
        status = (await self.db.execute(stmt)).scalar_one_or_none()

        if not status:
            return SecurityScore(
                total_score=0,
                defender_score=0,
                firewall_score=0,
                bitlocker_score=0,
                tpm_score=0,
                secure_boot_score=0,
                updates_score=0,
            )

        # Weighting logic (Configurable max 100)
        # Defender: 30, Firewall: 20, BitLocker: 20, TPM: 10, SecureBoot: 10, Updates: 10
        defender_score = 0.0
        if status.defender_enabled:
            defender_score += 10
        if status.defender_rtp:
            defender_score += 15
        if status.defender_tamper_protection:
            defender_score += 5

        firewall_score = 0.0
        fw_stmt = select(InventoryFirewallProfile).where(
            InventoryFirewallProfile.endpoint_id == endpoint_id,
            InventoryFirewallProfile.enabled
        )
        fw_profiles = (await self.db.execute(fw_stmt)).scalars().all()
        if len(fw_profiles) > 0:
            firewall_score = 20.0  # Simplification

        bitlocker_score = 0.0
        bl_stmt = select(InventoryBitlockerVolume).where(
            InventoryBitlockerVolume.endpoint_id == endpoint_id,
            InventoryBitlockerVolume.protection_status == "On"
        )
        bl_volumes = (await self.db.execute(bl_stmt)).scalars().all()
        if len(bl_volumes) > 0:
            bitlocker_score = 20.0

        tpm_score = 10.0 if status.tpm_enabled else 0.0
        sb_score = 10.0 if status.secure_boot_enabled else 0.0

        updates_score = 10.0
        upd_stmt = select(func.count(InventoryWindowsUpdate.id)).where(
            InventoryWindowsUpdate.endpoint_id == endpoint_id,
            InventoryWindowsUpdate.installation_state.in_(["NotInstalled", "Pending", "Unknown"]),
        )
        pending_updates = (await self.db.execute(upd_stmt)).scalar_one()
        if pending_updates > 5:
            updates_score = 0.0
        elif pending_updates > 0:
            updates_score = 5.0

        total = defender_score + firewall_score + bitlocker_score + tpm_score + sb_score + updates_score

        return SecurityScore(
            total_score=total,
            defender_score=defender_score,
            firewall_score=firewall_score,
            bitlocker_score=bitlocker_score,
            tpm_score=tpm_score,
            secure_boot_score=sb_score,
            updates_score=updates_score,
        )

    async def generate_recommendations(self, endpoint_id: int) -> list[SecurityRecommendation]:
        recs = []
        stmt = select(InventorySecurityStatus).where(InventorySecurityStatus.endpoint_id == endpoint_id)
        status = (await self.db.execute(stmt)).scalar_one_or_none()

        if not status:
            return recs

        if not status.defender_enabled:
            recs.append(SecurityRecommendation(
                id=str(uuid.uuid4()),
                title="Enable Windows Defender",
                description="Windows Defender is currently disabled. Enable it to protect against malware.",
                severity="high",
                category="defender"
            ))
        elif not status.defender_rtp:
            recs.append(SecurityRecommendation(
                id=str(uuid.uuid4()),
                title="Enable Real-Time Protection",
                description="Real-time protection is disabled. Enable it to block threats automatically.",
                severity="high",
                category="defender"
            ))

        fw_stmt = select(InventoryFirewallProfile).where(
            InventoryFirewallProfile.endpoint_id == endpoint_id,
            InventoryFirewallProfile.profile_name == "Domain",
            not InventoryFirewallProfile.enabled
        )
        fw_off = (await self.db.execute(fw_stmt)).scalar_one_or_none()
        if fw_off:
            recs.append(SecurityRecommendation(
                id=str(uuid.uuid4()),
                title="Enable Domain Firewall",
                description="Domain firewall profile is disabled.",
                severity="high",
                category="firewall"
            ))

        if not status.secure_boot_enabled:
            recs.append(SecurityRecommendation(
                id=str(uuid.uuid4()),
                title="Enable Secure Boot",
                description="Secure boot prevents malicious code from loading at startup.",
                severity="medium",
                category="os"
            ))

        return recs

    async def get_timeline(self, limit: int = 50) -> SecurityTimelineResponse:
        stmt = select(SecurityEvent).order_by(desc(SecurityEvent.timestamp)).limit(limit)
        events = (await self.db.execute(stmt)).scalars().all()

        count_stmt = select(func.count(SecurityEvent.id))
        total = (await self.db.execute(count_stmt)).scalar_one()

        return SecurityTimelineResponse(
            events=[SecurityEventSchema.model_validate(e) for e in events],
            total=total
        )

    async def record_event(
        self, endpoint_id: int, event_type: str, severity: str, description: str
    ) -> None:
        event = SecurityEvent(
            endpoint_id=endpoint_id,
            event_type=event_type,
            severity=severity,
            description=description,
            timestamp=datetime.now(UTC),
        )
        self.db.add(event)
        await self.db.flush()

    async def detect_state_changes(self, endpoint_id: int, old_status: InventorySecurityStatus | None, new_status: InventorySecurityStatus) -> None:
        if not old_status:
            return

        # Defender Status Changes
        if old_status.defender_enabled and not new_status.defender_enabled:
            await self.record_event(endpoint_id, "Defender Disabled", "critical", "Windows Defender antivirus was disabled.")
        elif not old_status.defender_enabled and new_status.defender_enabled:
            await self.record_event(endpoint_id, "Defender Enabled", "info", "Windows Defender antivirus was enabled.")

        if old_status.defender_rtp and not new_status.defender_rtp:
            await self.record_event(endpoint_id, "RTP Disabled", "critical", "Real-Time Protection was disabled.")

        if old_status.defender_tamper_protection and not new_status.defender_tamper_protection:
            await self.record_event(endpoint_id, "Tamper Protection Disabled", "critical", "Defender Tamper Protection was disabled.")

        # Firewall Changes
        # Note: Firewall profile changes would be detected separately, but for now we look at general security status
        # Secure Boot
        if old_status.secure_boot_enabled and not new_status.secure_boot_enabled:
            await self.record_event(endpoint_id, "Secure Boot Disabled", "high", "Secure Boot was disabled on the endpoint.")
