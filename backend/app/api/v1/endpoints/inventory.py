"""
Inventory collection endpoints for Endpoint Sentinel X agents.

Each endpoint represents exactly one inventory domain and is independently
rate-limited, validated, and tracked via inventory_category_states and
inventory_sync_logs for full auditability.
"""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.endpoint import Endpoint
from app.db.models.inventory_category_state import InventoryCategoryState
from app.db.models.inventory_disk import InventoryDisk
from app.db.models.inventory_hardware import InventoryHardware
from app.db.models.inventory_local_user import InventoryLocalUser
from app.db.models.inventory_network_adapter import InventoryNetworkAdapter
from app.db.models.inventory_network_address import InventoryNetworkAddress
from app.db.models.inventory_os import InventoryOS
from app.db.models.inventory_security_status import InventorySecurityStatus
from app.db.models.inventory_service import InventoryService
from app.db.models.inventory_software import InventorySoftware
from app.db.models.inventory_sync_log import InventorySyncLog
from app.db.models.inventory_volume import InventoryVolume
from app.db.models.inventory_windows_update import InventoryWindowsUpdate
from app.dependencies.agent import get_current_agent
from app.dependencies.database import get_db
from app.schemas.inventory import (
    HardwareInventoryRequest,
    InventoryResponse,
    LocalUsersInventoryRequest,
    NetworkInventoryRequest,
    OSInventoryRequest,
    SecurityInventoryRequest,
    ServicesInventoryRequest,
    SoftwareInventoryRequest,
    StorageInventoryRequest,
    WindowsUpdatesInventoryRequest,
)

router = APIRouter()

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

MAX_PAYLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


async def _check_hash(
    db: AsyncSession,
    endpoint_id: int,
    category: str,
    incoming_hash: str,
    collected_at: datetime,
) -> InventoryCategoryState | None:
    """Returns the existing state row if the hash matches (skip) or None if update needed."""
    stmt = select(InventoryCategoryState).where(
        InventoryCategoryState.endpoint_id == endpoint_id,
        InventoryCategoryState.category == category,
    )
    result = await db.execute(stmt)
    state = result.scalar_one_or_none()

    if state:
        if state.inventory_hash == incoming_hash:
            return state  # Signal: skip
        if state.collected_at > collected_at:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Stale inventory: server has a newer snapshot for category '{category}'",
            )
    return None  # Signal: proceed with update


async def _upsert_category_state(
    db: AsyncSession,
    endpoint_id: int,
    category: str,
    inventory_hash: str,
    agent_version: str | None,
    collected_at: datetime,
) -> None:
    """Upserts the accepted hash state for a given (endpoint, category) pair."""
    now = datetime.now(UTC)
    stmt = (
        pg_insert(InventoryCategoryState)
        .values(
            endpoint_id=endpoint_id,
            category=category,
            inventory_hash=inventory_hash,
            agent_version=agent_version,
            collected_at=collected_at,
            last_synced_at=now,
            created_at=now,
            updated_at=now,
        )
        .on_conflict_do_update(
            constraint="uq_category_state",
            set_={
                "inventory_hash": inventory_hash,
                "agent_version": agent_version,
                "collected_at": collected_at,
                "last_synced_at": now,
                "updated_at": now,
            },
        )
    )
    await db.execute(stmt)


async def _write_sync_log(
    db: AsyncSession,
    endpoint_id: int,
    category: str,
    sync_status: str,
    inventory_hash: str | None,
    agent_version: str | None,
    collected_at: datetime | None,
    started_at: datetime,
    failure_reason: str | None = None,
) -> None:
    """Appends an audit row to inventory_sync_logs."""
    now = datetime.now(UTC)
    duration_ms = int((now - started_at).total_seconds() * 1000)
    log = InventorySyncLog(
        endpoint_id=endpoint_id,
        category=category,
        status=sync_status,
        inventory_hash=inventory_hash,
        agent_version=agent_version,
        collected_at=collected_at,
        started_at=started_at,
        completed_at=now,
        duration_ms=duration_ms,
        failure_reason=failure_reason,
    )
    db.add(log)
    await db.flush()


# ---------------------------------------------------------------------------
# POST /inventory/hardware
# ---------------------------------------------------------------------------


@router.post(
    "/inventory/hardware", response_model=InventoryResponse, summary="Submit hardware inventory"
)
async def submit_hardware(
    request: Request,
    payload: HardwareInventoryRequest,
    current_agent: Annotated[Endpoint, Depends(get_current_agent)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InventoryResponse:
    if (
        request.headers.get("content-length")
        and int(request.headers["content-length"]) > MAX_PAYLOAD_BYTES
    ):
        raise HTTPException(status_code=413, detail="Payload Too Large")

    started_at = datetime.now(UTC)
    category = "hardware"
    eid = current_agent.id

    existing = await _check_hash(db, eid, category, payload.inventory_hash, payload.collected_at)
    if existing:
        await _write_sync_log(
            db,
            eid,
            category,
            "skipped",
            payload.inventory_hash,
            payload.agent_version,
            payload.collected_at,
            started_at,
        )
        await db.flush()
        return InventoryResponse(status="skipped", category=category)

    await db.execute(delete(InventoryHardware).where(InventoryHardware.endpoint_id == eid))
    hw = payload.hardware
    db.add(
        InventoryHardware(
            endpoint_id=eid,
            cpu_model=hw.cpu_model,
            cpu_cores=hw.cpu_cores,
            cpu_threads=hw.cpu_threads,
            total_ram_bytes=hw.total_ram_bytes,
            system_manufacturer=hw.system_manufacturer,
            system_model=hw.system_model,
            bios_version=hw.bios_version,
        )
    )
    await _upsert_category_state(
        db, eid, category, payload.inventory_hash, payload.agent_version, payload.collected_at
    )
    await _write_sync_log(
        db,
        eid,
        category,
        "success",
        payload.inventory_hash,
        payload.agent_version,
        payload.collected_at,
        started_at,
    )
    await db.flush()
    return InventoryResponse(status="accepted", category=category)


# ---------------------------------------------------------------------------
# POST /inventory/os
# ---------------------------------------------------------------------------


@router.post("/inventory/os", response_model=InventoryResponse, summary="Submit OS inventory")
async def submit_os(
    request: Request,
    payload: OSInventoryRequest,
    current_agent: Annotated[Endpoint, Depends(get_current_agent)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InventoryResponse:
    if (
        request.headers.get("content-length")
        and int(request.headers["content-length"]) > MAX_PAYLOAD_BYTES
    ):
        raise HTTPException(status_code=413, detail="Payload Too Large")

    started_at = datetime.now(UTC)
    category = "os"
    eid = current_agent.id

    existing = await _check_hash(db, eid, category, payload.inventory_hash, payload.collected_at)
    if existing:
        await _write_sync_log(
            db,
            eid,
            category,
            "skipped",
            payload.inventory_hash,
            payload.agent_version,
            payload.collected_at,
            started_at,
        )
        await db.flush()
        return InventoryResponse(status="skipped", category=category)

    await db.execute(delete(InventoryOS).where(InventoryOS.endpoint_id == eid))
    os_data = payload.os
    db.add(
        InventoryOS(
            endpoint_id=eid,
            name=os_data.name,
            version=os_data.version,
            build_number=os_data.build_number,
            architecture=os_data.architecture,
            install_date=os_data.install_date,
        )
    )
    await _upsert_category_state(
        db, eid, category, payload.inventory_hash, payload.agent_version, payload.collected_at
    )
    await _write_sync_log(
        db,
        eid,
        category,
        "success",
        payload.inventory_hash,
        payload.agent_version,
        payload.collected_at,
        started_at,
    )
    await db.flush()
    return InventoryResponse(status="accepted", category=category)


# ---------------------------------------------------------------------------
# POST /inventory/security
# ---------------------------------------------------------------------------


@router.post(
    "/inventory/security",
    response_model=InventoryResponse,
    summary="Submit security status inventory",
)
async def submit_security(
    request: Request,
    payload: SecurityInventoryRequest,
    current_agent: Annotated[Endpoint, Depends(get_current_agent)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InventoryResponse:
    if (
        request.headers.get("content-length")
        and int(request.headers["content-length"]) > MAX_PAYLOAD_BYTES
    ):
        raise HTTPException(status_code=413, detail="Payload Too Large")

    started_at = datetime.now(UTC)
    category = "security"
    eid = current_agent.id

    existing = await _check_hash(db, eid, category, payload.inventory_hash, payload.collected_at)
    if existing:
        await _write_sync_log(
            db,
            eid,
            category,
            "skipped",
            payload.inventory_hash,
            payload.agent_version,
            payload.collected_at,
            started_at,
        )
        await db.flush()
        return InventoryResponse(status="skipped", category=category)

    await db.execute(
        delete(InventorySecurityStatus).where(InventorySecurityStatus.endpoint_id == eid)
    )
    from app.db.models.inventory_bitlocker_volume import InventoryBitlockerVolume
    from app.db.models.inventory_firewall_profile import InventoryFirewallProfile

    await db.execute(
        delete(InventoryBitlockerVolume).where(InventoryBitlockerVolume.endpoint_id == eid)
    )
    await db.execute(
        delete(InventoryFirewallProfile).where(InventoryFirewallProfile.endpoint_id == eid)
    )

    sec = payload.security

    # Extract nested payloads (they can be None depending on collection success)
    def_data = sec.defender
    tpm_data = sec.tpm
    sb_data = sec.secure_boot
    uac_data = sec.uac
    sc_data = sec.security_center

    db.add(
        InventorySecurityStatus(
            endpoint_id=eid,
            # Defender
            defender_installed=def_data.installed if def_data else False,
            defender_enabled=def_data.enabled if def_data else False,
            defender_rtp=def_data.real_time_protection if def_data else False,
            defender_sig_version=def_data.antivirus_signature_version if def_data else None,
            defender_engine_version=def_data.engine_version if def_data else None,
            defender_last_sig_update=def_data.last_signature_update if def_data else None,
            defender_last_quick_scan=def_data.last_quick_scan if def_data else None,
            defender_last_full_scan=def_data.last_full_scan if def_data else None,
            defender_av_enabled=def_data.antivirus_enabled if def_data else None,
            defender_antispyware_enabled=def_data.antispyware_enabled if def_data else None,
            defender_nis_enabled=def_data.nis_enabled if def_data else None,
            defender_ioav_protection=def_data.ioav_protection if def_data else None,
            defender_behavior_monitoring=def_data.behavior_monitoring if def_data else None,
            defender_tamper_protection=def_data.tamper_protection if def_data else None,
            # TPM
            tpm_present=tpm_data.present if tpm_data else False,
            tpm_ready=tpm_data.ready if tpm_data else False,
            tpm_enabled=tpm_data.enabled if tpm_data else False,
            tpm_activated=tpm_data.activated if tpm_data else False,
            tpm_manufacturer=tpm_data.manufacturer if tpm_data else None,
            tpm_manufacturer_version=tpm_data.manufacturer_version if tpm_data else None,
            tpm_specification_version=tpm_data.specification_version if tpm_data else None,
            tpm_managed_auth_level=tpm_data.managed_authentication_level if tpm_data else None,
            # Secure Boot
            secure_boot_supported=sb_data.supported if sb_data else False,
            secure_boot_enabled=sb_data.enabled if sb_data else False,
            # UAC
            uac_enabled=uac_data.enabled if uac_data else False,
            uac_consent_prompt_behavior=uac_data.consent_prompt_behavior if uac_data else None,
            # Security Center
            security_center_status=sc_data.status if sc_data else None,
            security_center_registered_av=sc_data.registered_antivirus if sc_data else None,
            security_center_registered_fw=sc_data.registered_firewall if sc_data else None,
            security_center_registered_antispyware=sc_data.registered_antispyware
            if sc_data
            else None,
            security_center_product_state=sc_data.product_state if sc_data else None,
        )
    )

    for bv in sec.bitlocker_volumes:
        db.add(
            InventoryBitlockerVolume(
                endpoint_id=eid,
                drive_letter=bv.drive_letter,
                volume_type=bv.volume_type,
                protection_status=bv.protection_status,
                encryption_percentage=bv.encryption_percentage,
                encryption_method=bv.encryption_method,
                lock_status=bv.lock_status,
                auto_unlock=bv.auto_unlock,
                key_protector_count=bv.key_protector_count,
            )
        )

    for fp in sec.firewall_profiles:
        db.add(
            InventoryFirewallProfile(
                endpoint_id=eid,
                profile_name=fp.profile_name,
                enabled=fp.enabled,
                default_inbound_policy=fp.default_inbound_policy,
                default_outbound_policy=fp.default_outbound_policy,
            )
        )
    await _upsert_category_state(
        db, eid, category, payload.inventory_hash, payload.agent_version, payload.collected_at
    )
    await _write_sync_log(
        db,
        eid,
        category,
        "success",
        payload.inventory_hash,
        payload.agent_version,
        payload.collected_at,
        started_at,
    )
    await db.flush()
    return InventoryResponse(status="accepted", category=category)


# ---------------------------------------------------------------------------
# POST /inventory/network
# ---------------------------------------------------------------------------


@router.post(
    "/inventory/network",
    response_model=InventoryResponse,
    summary="Submit network adapter inventory",
)
async def submit_network(
    request: Request,
    payload: NetworkInventoryRequest,
    current_agent: Annotated[Endpoint, Depends(get_current_agent)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InventoryResponse:
    if (
        request.headers.get("content-length")
        and int(request.headers["content-length"]) > MAX_PAYLOAD_BYTES
    ):
        raise HTTPException(status_code=413, detail="Payload Too Large")

    started_at = datetime.now(UTC)
    category = "network"
    eid = current_agent.id

    existing = await _check_hash(db, eid, category, payload.inventory_hash, payload.collected_at)
    if existing:
        await _write_sync_log(
            db,
            eid,
            category,
            "skipped",
            payload.inventory_hash,
            payload.agent_version,
            payload.collected_at,
            started_at,
        )
        await db.flush()
        return InventoryResponse(status="skipped", category=category)

    # Cascade delete handles addresses, wifi, and vpn via FK
    await db.execute(
        delete(InventoryNetworkAdapter).where(InventoryNetworkAdapter.endpoint_id == eid)
    )
    from app.db.models.inventory_network_vpn import InventoryNetworkVpn
    from app.db.models.inventory_network_wifi import InventoryNetworkWifi

    # Update Network Identity on the Endpoint model
    if payload.identity:
        current_agent.fqdn = payload.identity.fqdn
        current_agent.domain_workgroup = payload.identity.domain_workgroup
        current_agent.primary_dns_suffix = payload.identity.primary_dns_suffix
        # DB flush will save this automatically since current_agent is attached to the session

    for adapter_data in payload.adapters:
        adapter = InventoryNetworkAdapter(
            endpoint_id=eid,
            name=adapter_data.name,
            friendly_name=adapter_data.friendly_name,
            description=adapter_data.description,
            interface_type=adapter_data.interface_type,
            adapter_type=adapter_data.adapter_type,
            manufacturer=adapter_data.manufacturer,
            mac_address=adapter_data.mac_address,
            is_physical=adapter_data.is_physical,
            is_virtual=adapter_data.is_virtual,
            status=adapter_data.status,
            admin_status=adapter_data.admin_status,
            link_speed_bps=adapter_data.link_speed_bps,
            mtu=adapter_data.mtu,
            driver_version=adapter_data.driver_version,
            driver_date=adapter_data.driver_date,
            interface_index=adapter_data.interface_index,
            interface_guid=adapter_data.interface_guid,
            dhcp_enabled=adapter_data.dhcp_enabled,
            dhcp_server=adapter_data.dhcp_server,
            dhcp_lease_obtained=adapter_data.dhcp_lease_obtained,
            dhcp_lease_expires=adapter_data.dhcp_lease_expires,
            default_gateways=adapter_data.default_gateways,
            dns_servers=adapter_data.dns_servers,
            dns_search_suffixes=adapter_data.dns_search_suffixes,
        )
        db.add(adapter)
        await db.flush()  # flush to get adapter.id

        for addr in adapter_data.addresses:
            db.add(
                InventoryNetworkAddress(
                    adapter_id=adapter.id,
                    address=addr.address,
                    family=addr.family,
                    prefix_length=addr.prefix_length,
                    subnet_mask=addr.subnet_mask,
                    is_loopback=addr.is_loopback,
                )
            )

        if adapter_data.wifi:
            db.add(
                InventoryNetworkWifi(
                    adapter_id=adapter.id,
                    ssid=adapter_data.wifi.ssid,
                    bssid=adapter_data.wifi.bssid,
                    signal_strength=adapter_data.wifi.signal_strength,
                    auth_type=adapter_data.wifi.auth_type,
                    radio_type=adapter_data.wifi.radio_type,
                    channel=adapter_data.wifi.channel,
                    frequency_mhz=adapter_data.wifi.frequency_mhz,
                )
            )

        if adapter_data.vpn:
            db.add(
                InventoryNetworkVpn(
                    adapter_id=adapter.id,
                    connection_status=adapter_data.vpn.connection_status,
                    tunnel_type=adapter_data.vpn.tunnel_type,
                )
            )

    await _upsert_category_state(
        db, eid, category, payload.inventory_hash, payload.agent_version, payload.collected_at
    )
    await _write_sync_log(
        db,
        eid,
        category,
        "success",
        payload.inventory_hash,
        payload.agent_version,
        payload.collected_at,
        started_at,
    )
    await db.flush()
    return InventoryResponse(status="accepted", category=category)


# ---------------------------------------------------------------------------
# POST /inventory/storage
# ---------------------------------------------------------------------------


@router.post(
    "/inventory/storage", response_model=InventoryResponse, summary="Submit storage inventory"
)
async def submit_storage(
    request: Request,
    payload: StorageInventoryRequest,
    current_agent: Annotated[Endpoint, Depends(get_current_agent)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InventoryResponse:
    if (
        request.headers.get("content-length")
        and int(request.headers["content-length"]) > MAX_PAYLOAD_BYTES
    ):
        raise HTTPException(status_code=413, detail="Payload Too Large")

    started_at = datetime.now(UTC)
    category = "storage"
    eid = current_agent.id

    existing = await _check_hash(db, eid, category, payload.inventory_hash, payload.collected_at)
    if existing:
        await _write_sync_log(
            db,
            eid,
            category,
            "skipped",
            payload.inventory_hash,
            payload.agent_version,
            payload.collected_at,
            started_at,
        )
        await db.flush()
        return InventoryResponse(status="skipped", category=category)

    await db.execute(delete(InventoryDisk).where(InventoryDisk.endpoint_id == eid))
    await db.execute(delete(InventoryVolume).where(InventoryVolume.endpoint_id == eid))
    for d in payload.disks:
        db.add(
            InventoryDisk(
                endpoint_id=eid,
                model=d.model,
                serial_number=d.serial_number,
                size_bytes=d.size_bytes,
                interface_type=d.interface_type,
            )
        )
    for v in payload.volumes:
        db.add(
            InventoryVolume(
                endpoint_id=eid,
                drive_letter=v.drive_letter,
                label=v.label,
                filesystem=v.filesystem,
                size_bytes=v.size_bytes,
                free_bytes=v.free_bytes,
            )
        )

    await _upsert_category_state(
        db, eid, category, payload.inventory_hash, payload.agent_version, payload.collected_at
    )
    await _write_sync_log(
        db,
        eid,
        category,
        "success",
        payload.inventory_hash,
        payload.agent_version,
        payload.collected_at,
        started_at,
    )
    await db.flush()
    return InventoryResponse(status="accepted", category=category)


# ---------------------------------------------------------------------------
# POST /inventory/software
# ---------------------------------------------------------------------------


@router.post(
    "/inventory/software",
    response_model=InventoryResponse,
    summary="Submit installed software inventory",
)
async def submit_software(
    request: Request,
    payload: SoftwareInventoryRequest,
    current_agent: Annotated[Endpoint, Depends(get_current_agent)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InventoryResponse:
    if (
        request.headers.get("content-length")
        and int(request.headers["content-length"]) > MAX_PAYLOAD_BYTES
    ):
        raise HTTPException(status_code=413, detail="Payload Too Large")

    started_at = datetime.now(UTC)
    category = "software"
    eid = current_agent.id

    existing = await _check_hash(db, eid, category, payload.inventory_hash, payload.collected_at)
    if existing:
        await _write_sync_log(
            db,
            eid,
            category,
            "skipped",
            payload.inventory_hash,
            payload.agent_version,
            payload.collected_at,
            started_at,
        )
        await db.flush()
        return InventoryResponse(status="skipped", category=category)

    await db.execute(delete(InventorySoftware).where(InventorySoftware.endpoint_id == eid))
    for s in payload.software:
        db.add(
            InventorySoftware(
                endpoint_id=eid,
                name=s.name,
                version=s.version,
                publisher=s.publisher,
                install_date=s.install_date,
            )
        )

    await _upsert_category_state(
        db, eid, category, payload.inventory_hash, payload.agent_version, payload.collected_at
    )
    await _write_sync_log(
        db,
        eid,
        category,
        "success",
        payload.inventory_hash,
        payload.agent_version,
        payload.collected_at,
        started_at,
    )
    await db.flush()
    return InventoryResponse(status="accepted", category=category)


# ---------------------------------------------------------------------------
# POST /inventory/windows-updates
# ---------------------------------------------------------------------------


@router.post(
    "/inventory/windows-updates",
    response_model=InventoryResponse,
    summary="Submit Windows Update inventory",
)
async def submit_windows_updates(
    request: Request,
    payload: WindowsUpdatesInventoryRequest,
    current_agent: Annotated[Endpoint, Depends(get_current_agent)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InventoryResponse:
    if (
        request.headers.get("content-length")
        and int(request.headers["content-length"]) > MAX_PAYLOAD_BYTES
    ):
        raise HTTPException(status_code=413, detail="Payload Too Large")

    started_at = datetime.now(UTC)
    category = "windows-updates"
    eid = current_agent.id

    existing = await _check_hash(db, eid, category, payload.inventory_hash, payload.collected_at)
    if existing:
        await _write_sync_log(
            db,
            eid,
            category,
            "skipped",
            payload.inventory_hash,
            payload.agent_version,
            payload.collected_at,
            started_at,
        )
        await db.flush()
        return InventoryResponse(status="skipped", category=category)

    await db.execute(
        delete(InventoryWindowsUpdate).where(InventoryWindowsUpdate.endpoint_id == eid)
    )
    for u in payload.updates:
        db.add(
            InventoryWindowsUpdate(
                endpoint_id=eid,
                kb_id=u.kb_id,
                title=u.title,
                install_date=u.install_date,
                status=u.status,
            )
        )

    await _upsert_category_state(
        db, eid, category, payload.inventory_hash, payload.agent_version, payload.collected_at
    )
    await _write_sync_log(
        db,
        eid,
        category,
        "success",
        payload.inventory_hash,
        payload.agent_version,
        payload.collected_at,
        started_at,
    )
    await db.flush()
    return InventoryResponse(status="accepted", category=category)


# ---------------------------------------------------------------------------
# POST /inventory/services
# ---------------------------------------------------------------------------


@router.post(
    "/inventory/services", response_model=InventoryResponse, summary="Submit services inventory"
)
async def submit_services(
    request: Request,
    payload: ServicesInventoryRequest,
    current_agent: Annotated[Endpoint, Depends(get_current_agent)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InventoryResponse:
    if (
        request.headers.get("content-length")
        and int(request.headers["content-length"]) > MAX_PAYLOAD_BYTES
    ):
        raise HTTPException(status_code=413, detail="Payload Too Large")

    started_at = datetime.now(UTC)
    category = "services"
    eid = current_agent.id

    existing = await _check_hash(db, eid, category, payload.inventory_hash, payload.collected_at)
    if existing:
        await _write_sync_log(
            db,
            eid,
            category,
            "skipped",
            payload.inventory_hash,
            payload.agent_version,
            payload.collected_at,
            started_at,
        )
        await db.flush()
        return InventoryResponse(status="skipped", category=category)

    await db.execute(delete(InventoryService).where(InventoryService.endpoint_id == eid))
    for svc in payload.services:
        db.add(
            InventoryService(
                endpoint_id=eid,
                name=svc.name,
                display_name=svc.display_name,
                startup_type=svc.startup_type,
                status=svc.status,
            )
        )

    await _upsert_category_state(
        db, eid, category, payload.inventory_hash, payload.agent_version, payload.collected_at
    )
    await _write_sync_log(
        db,
        eid,
        category,
        "success",
        payload.inventory_hash,
        payload.agent_version,
        payload.collected_at,
        started_at,
    )
    await db.flush()
    return InventoryResponse(status="accepted", category=category)


# ---------------------------------------------------------------------------
# POST /inventory/local-users
# ---------------------------------------------------------------------------


@router.post(
    "/inventory/local-users",
    response_model=InventoryResponse,
    summary="Submit local users inventory",
)
async def submit_local_users(
    request: Request,
    payload: LocalUsersInventoryRequest,
    current_agent: Annotated[Endpoint, Depends(get_current_agent)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InventoryResponse:
    if (
        request.headers.get("content-length")
        and int(request.headers["content-length"]) > MAX_PAYLOAD_BYTES
    ):
        raise HTTPException(status_code=413, detail="Payload Too Large")

    started_at = datetime.now(UTC)
    category = "local-users"
    eid = current_agent.id

    existing = await _check_hash(db, eid, category, payload.inventory_hash, payload.collected_at)
    if existing:
        await _write_sync_log(
            db,
            eid,
            category,
            "skipped",
            payload.inventory_hash,
            payload.agent_version,
            payload.collected_at,
            started_at,
        )
        await db.flush()
        return InventoryResponse(status="skipped", category=category)

    await db.execute(delete(InventoryLocalUser).where(InventoryLocalUser.endpoint_id == eid))
    for u in payload.users:
        db.add(
            InventoryLocalUser(
                endpoint_id=eid,
                username=u.username,
                is_active=u.is_active,
                privilege=u.privilege,
                last_login=u.last_login,
            )
        )

    await _upsert_category_state(
        db, eid, category, payload.inventory_hash, payload.agent_version, payload.collected_at
    )
    await _write_sync_log(
        db,
        eid,
        category,
        "success",
        payload.inventory_hash,
        payload.agent_version,
        payload.collected_at,
        started_at,
    )
    await db.flush()
    return InventoryResponse(status="accepted", category=category)
