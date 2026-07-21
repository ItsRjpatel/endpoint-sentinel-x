"""
Integration tests for the inventory collection endpoints.

Covers: hash deduplication, data persistence, cascade delete, auth checks,
payload validation, stale payload rejection, network normalization, and sync log audit.
"""

import json
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.endpoint import Endpoint
from app.db.models.inventory_hardware import InventoryHardware
from app.db.models.inventory_network_adapter import InventoryNetworkAdapter
from app.db.models.inventory_network_address import InventoryNetworkAddress
from app.db.models.inventory_os import InventoryOS
from app.db.models.inventory_service import InventoryService
from app.db.models.inventory_software import InventorySoftware
from app.db.models.inventory_sync_log import InventorySyncLog
from app.db.models.inventory_windows_update import InventoryWindowsUpdate
from app.db.models.organization import Organization
from app.db.session import AsyncSessionLocal
from app.dependencies.database import get_db
from app.main import app
from app.repositories.organization import OrganizationRepository

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(autouse=True)
async def override_db(db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def test_org(db_session: AsyncSession) -> Organization:
    org_repo = OrganizationRepository(db_session)
    return await org_repo.create(
        Organization(
            name="Inventory Test Org", slug="inventory-test-org", description="For inventory tests"
        )
    )


@pytest.fixture
async def enrolled_agent(db_session: AsyncSession, test_org: Organization) -> tuple[Endpoint, str]:
    secret = "esx_as_inventory_test_secret_key"
    secret_hash = sha256(secret.encode()).hexdigest()
    agent_id = uuid4()
    endpoint = Endpoint(
        organization_id=test_org.id,
        hostname="inv-test-host",
        os_platform="windows",
        os_version="10.0.19045",
        hardware_uuid=f"hw-{uuid4()}",
        ip_address="10.0.0.99",
        agent_id=agent_id,
        agent_secret_hash=secret_hash,
        lifecycle_state="ONLINE",
        last_seen=datetime.now(UTC),
    )
    db_session.add(endpoint)
    await db_session.flush()
    return endpoint, secret


def _agent_headers(endpoint: Endpoint, secret: str) -> dict:
    return {"X-Agent-ID": str(endpoint.agent_id), "X-Agent-Secret": secret}


def _make_hash(payload: dict) -> str:
    return sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


# ---------------------------------------------------------------------------
# Hardware tests
# ---------------------------------------------------------------------------


HW_PAYLOAD = {
    "cpu_model": "Intel Core i7-12700K",
    "cpu_cores": 12,
    "cpu_threads": 20,
    "total_ram_bytes": 34359738368,
    "system_manufacturer": "ASUS",
    "system_model": "PRIME Z690-P",
    "bios_version": "2.5.0",
}


@pytest.mark.anyio
async def test_hardware_inventory_accepted(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str], db_session: AsyncSession
) -> None:
    endpoint, secret = enrolled_agent
    inv_hash = _make_hash(HW_PAYLOAD)
    response = await client.post(
        "/api/v1/inventory/hardware",
        headers=_agent_headers(endpoint, secret),
        json={
            "collected_at": datetime.now(UTC).isoformat(),
            "agent_version": "1.0.0",
            "inventory_hash": inv_hash,
            "hardware": HW_PAYLOAD,
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"

    # Verify data persisted
    result = await db_session.execute(
        select(InventoryHardware).where(InventoryHardware.endpoint_id == endpoint.id)
    )
    hw = result.scalar_one_or_none()
    assert hw is not None
    assert hw.cpu_model == "Intel Core i7-12700K"
    assert hw.cpu_cores == 12


@pytest.mark.anyio
async def test_hardware_inventory_skipped_on_same_hash(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str]
) -> None:
    """Submitting the same hash twice should return 'skipped' on the second call."""
    endpoint, secret = enrolled_agent
    inv_hash = _make_hash(HW_PAYLOAD)
    request_body = {
        "collected_at": datetime.now(UTC).isoformat(),
        "agent_version": "1.0.0",
        "inventory_hash": inv_hash,
        "hardware": HW_PAYLOAD,
    }
    headers = _agent_headers(endpoint, secret)

    r1 = await client.post("/api/v1/inventory/hardware", headers=headers, json=request_body)
    assert r1.json()["status"] == "accepted"

    r2 = await client.post("/api/v1/inventory/hardware", headers=headers, json=request_body)
    assert r2.json()["status"] == "skipped"


@pytest.mark.anyio
async def test_hardware_stale_payload_rejected(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str]
) -> None:
    """A payload with an older collected_at than the stored state should be rejected with 409."""
    endpoint, secret = enrolled_agent
    headers = _agent_headers(endpoint, secret)
    now = datetime.now(UTC)

    # First: submit with recent timestamp
    await client.post(
        "/api/v1/inventory/hardware",
        headers=headers,
        json={
            "collected_at": now.isoformat(),
            "agent_version": "1.0.0",
            "inventory_hash": _make_hash(HW_PAYLOAD),
            "hardware": HW_PAYLOAD,
        },
    )

    # Second: submit with an older timestamp and different hash
    old_payload = {**HW_PAYLOAD, "cpu_model": "Old CPU"}
    r = await client.post(
        "/api/v1/inventory/hardware",
        headers=headers,
        json={
            "collected_at": (now - timedelta(hours=1)).isoformat(),
            "agent_version": "1.0.0",
            "inventory_hash": _make_hash(old_payload),
            "hardware": old_payload,
        },
    )
    assert r.status_code == 409


@pytest.mark.anyio
async def test_inventory_unauthorized(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str]
) -> None:
    endpoint, _ = enrolled_agent
    r = await client.post(
        "/api/v1/inventory/hardware",
        headers={"X-Agent-ID": str(endpoint.agent_id), "X-Agent-Secret": "wrongsecret"},
        json={
            "collected_at": datetime.now(UTC).isoformat(),
            "agent_version": "1.0.0",
            "inventory_hash": "abc",
            "hardware": HW_PAYLOAD,
        },
    )
    assert r.status_code == 401


@pytest.mark.anyio
async def test_inventory_schema_validation_error(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str]
) -> None:
    endpoint, secret = enrolled_agent
    r = await client.post(
        "/api/v1/inventory/hardware",
        headers=_agent_headers(endpoint, secret),
        json={"hardware": {"cpu_model": "Missing required fields"}},
    )
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Sync log audit
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_sync_log_created_on_accept(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str], db_session: AsyncSession
) -> None:
    endpoint, secret = enrolled_agent
    inv_hash = _make_hash(HW_PAYLOAD)
    await client.post(
        "/api/v1/inventory/hardware",
        headers=_agent_headers(endpoint, secret),
        json={
            "collected_at": datetime.now(UTC).isoformat(),
            "agent_version": "1.0.0",
            "inventory_hash": inv_hash,
            "hardware": HW_PAYLOAD,
        },
    )
    logs = await db_session.execute(
        select(InventorySyncLog).where(
            InventorySyncLog.endpoint_id == endpoint.id,
            InventorySyncLog.category == "hardware",
        )
    )
    log = logs.scalar_one_or_none()
    assert log is not None
    assert log.status == "success"
    assert log.inventory_hash == inv_hash


# ---------------------------------------------------------------------------
# Network normalization
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_network_normalized_addresses(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str], db_session: AsyncSession
) -> None:
    """An adapter with 3 IP addresses should create 3 rows in inventory_network_addresses."""
    endpoint, secret = enrolled_agent
    network_payload = {
        "identity": {
            "fqdn": "test.local",
            "domain_workgroup": "local",
            "primary_dns_suffix": "local",
        },
        "adapters": [
            {
                "name": "Ethernet0",
                "mac_address": "AA:BB:CC:DD:EE:FF",
                "is_physical": True,
                "is_virtual": False,
                "adapter_type": "ethernet",
                "status": "up",
                "addresses": [
                    {
                        "address": "192.168.1.100",
                        "family": "ipv4",
                        "prefix_length": 24,
                        "is_loopback": False,
                    },
                    {
                        "address": "10.0.0.5",
                        "family": "ipv4",
                        "prefix_length": 16,
                        "is_loopback": False,
                    },
                    {
                        "address": "fe80::1",
                        "family": "ipv6",
                        "prefix_length": 64,
                        "is_loopback": False,
                    },
                ],
            }
        ],
    }
    r = await client.post(
        "/api/v1/inventory/network",
        headers=_agent_headers(endpoint, secret),
        json={
            "collected_at": datetime.now(UTC).isoformat(),
            "agent_version": "1.0.0",
            "inventory_hash": _make_hash(network_payload),
            **network_payload,
        },
    )
    assert r.status_code == 200
    assert r.json()["status"] == "accepted"

    adapters = await db_session.execute(
        select(InventoryNetworkAdapter).where(InventoryNetworkAdapter.endpoint_id == endpoint.id)
    )
    adapter = adapters.scalar_one()
    assert adapter.name == "Ethernet0"

    addresses = await db_session.execute(
        select(InventoryNetworkAddress).where(InventoryNetworkAddress.adapter_id == adapter.id)
    )
    addr_list = addresses.scalars().all()
    assert len(addr_list) == 3
    families = {a.family for a in addr_list}
    assert "ipv4" in families
    assert "ipv6" in families


@pytest.mark.asyncio
async def test_submit_windows_updates(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str], db_session: AsyncSession
):
    endpoint, secret = enrolled_agent
    now = datetime.now(UTC).isoformat()
    payload = {
        "collected_at": now,
        "agent_version": "1.0.0",
        "inventory_hash": "testhash-windows-updates-123",
        "updates": [
            {
                "hotfix_id": "KB5027303",
                "title": "2023-06 Cumulative Update",
                "installation_state": "Installed",
                "is_security_update": True,
                "is_cumulative_update": True,
            }
        ],
    }

    headers = _agent_headers(endpoint, secret)

    # 1. First submission (accepted)
    response = await client.post("/api/v1/inventory/windows-updates", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "accepted"

    # Verify DB
    result = await db_session.execute(
        select(InventoryWindowsUpdate).where(InventoryWindowsUpdate.endpoint_id == endpoint.id)
    )
    updates = result.scalars().all()
    assert len(updates) == 1
    assert updates[0].hotfix_id == "KB5027303"
    assert updates[0].is_security_update is True
    assert updates[0].installation_state == "Installed"

    # 2. Second submission with same hash (skipped)
    response2 = await client.post(
        "/api/v1/inventory/windows-updates", json=payload, headers=headers
    )
    assert response2.status_code == 200
    assert response2.json()["status"] == "skipped"

    # Verify sync log has skipped entry
    log_result = await db_session.execute(
        select(InventorySyncLog)
        .where(InventorySyncLog.endpoint_id == endpoint.id)
        .where(InventorySyncLog.category == "windows_updates")
        .order_by(InventorySyncLog.started_at.desc())
    )
    logs = log_result.scalars().all()
    assert logs[0].status == "skipped"


# ---------------------------------------------------------------------------
# Software inventory
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Services inventory
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_submit_services(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str], db_session: AsyncSession
):
    endpoint, secret = enrolled_agent
    payload = {
        "inventory_hash": "a" * 64,
        "agent_version": "1.0.0",
        "collected_at": "2024-01-01T00:00:00Z",
        "services": [
            {
                "name": "wuauserv",
                "display_name": "Windows Update",
                "status": "Running",
                "startup_type": "Auto",
                "binary_path": "C:\\Windows\\system32\\svchost.exe -k netsvcs -p",
                "service_account": "LocalSystem",
                "delayed_auto_start": True,
                "process_id": 1234,
                "dependencies": ["rpcss"],
                "dependent_services": [],
            }
        ],
    }

    headers = _agent_headers(endpoint, secret)

    response = await client.post(
        "/api/v1/inventory/services",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"

    # Verify db
    result = await db_session.execute(
        select(InventoryService).where(InventoryService.endpoint_id == endpoint.id)
    )
    services = result.scalars().all()
    assert len(services) == 1
    assert services[0].name == "wuauserv"
    assert services[0].process_id == 1234

    # Test idempotency
    response2 = await client.post(
        "/api/v1/inventory/services",
        json=payload,
        headers=headers,
    )
    assert response2.status_code == 200
    assert response2.json()["status"] == "skipped"


# ---------------------------------------------------------------------------
# OS inventory
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_os_inventory_accepted(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str], db_session: AsyncSession
) -> None:
    endpoint, secret = enrolled_agent
    os_data = {
        "name": "Windows 11",
        "version": "11.0",
        "build_number": "22621",
        "architecture": "x86_64",
    }
    r = await client.post(
        "/api/v1/inventory/os",
        headers=_agent_headers(endpoint, secret),
        json={
            "collected_at": datetime.now(UTC).isoformat(),
            "agent_version": "1.0.0",
            "inventory_hash": _make_hash(os_data),
            "os": os_data,
        },
    )
    assert r.status_code == 200
    assert r.json()["status"] == "accepted"

    result = await db_session.execute(
        select(InventoryOS).where(InventoryOS.endpoint_id == endpoint.id)
    )
    os_row = result.scalar_one_or_none()
    assert os_row is not None
    assert os_row.name == "Windows 11"
    assert os_row.build_number == "22621"


# ---------------------------------------------------------------------------
# Storage inventory
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_storage_inventory_accepted(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str], db_session: AsyncSession
) -> None:
    from app.db.models.inventory_disk import InventoryDisk
    from app.db.models.inventory_volume import InventoryVolume

    endpoint, secret = enrolled_agent
    storage_data = {
        "disks": [
            {
                "device_name": "PhysicalDrive0",
                "model": "Samsung SSD 980",
                "size_bytes": 1000204886016,
                "interface_type": "NVMe",
                "is_boot_disk": True,
                "partitions": [
                    {"partition_number": 1, "size_bytes": 524288000, "drive_letter": "C"}
                ],
            }
        ],
        "volumes": [
            {
                "drive_letter": "C",
                "file_system": "NTFS",
                "total_size": 999000000000,
                "free_space": 500000000000,
            }
        ],
        "storage_pools": [],
    }
    r = await client.post(
        "/api/v1/inventory/storage",
        headers=_agent_headers(endpoint, secret),
        json={
            "collected_at": datetime.now(UTC).isoformat(),
            "agent_version": "1.0.0",
            "inventory_hash": _make_hash(storage_data),
            **storage_data,
        },
    )
    assert r.status_code == 200
    assert r.json()["status"] == "accepted"

    disks = await db_session.execute(
        select(InventoryDisk).where(InventoryDisk.endpoint_id == endpoint.id)
    )
    disk_list = disks.scalars().all()
    assert len(disk_list) == 1
    assert disk_list[0].model == "Samsung SSD 980"

    vols = await db_session.execute(
        select(InventoryVolume).where(InventoryVolume.endpoint_id == endpoint.id)
    )
    vol_list = vols.scalars().all()
    assert len(vol_list) == 1
    assert vol_list[0].drive_letter == "C"


# ---------------------------------------------------------------------------
# Software inventory
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_software_inventory_accepted(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str], db_session: AsyncSession
) -> None:

    endpoint, secret = enrolled_agent
    sw_list = [
        {
            "name": "Google Chrome",
            "version": "120.0",
            "publisher": "Google LLC",
            "install_date": "2024-01-15",
            "install_scope": "Machine",
            "architecture": "x64",
        },
        {
            "name": "Visual Studio Code",
            "version": "1.85.0",
            "publisher": "Microsoft Corporation",
            "install_date": None,
            "install_scope": "User",
            "architecture": "x64",
        },
    ]
    r = await client.post(
        "/api/v1/inventory/software",
        headers=_agent_headers(endpoint, secret),
        json={
            "collected_at": datetime.now(UTC).isoformat(),
            "agent_version": "1.0.0",
            "inventory_hash": _make_hash({"software": sw_list}),
            "software": sw_list,
        },
    )
    assert r.status_code == 200
    assert r.json()["status"] == "accepted"

    softwares = await db_session.execute(
        select(InventorySoftware).where(InventorySoftware.endpoint_id == endpoint.id)
    )
    software_list = softwares.scalars().all()
    assert len(software_list) == 2
    assert any(s.name == "Google Chrome" and s.install_scope == "Machine" for s in software_list)
    assert any(s.name == "Visual Studio Code" and s.install_scope == "User" for s in software_list)
