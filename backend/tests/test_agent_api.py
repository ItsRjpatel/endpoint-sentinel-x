from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.endpoint import Endpoint
from app.db.models.enrollment_token import EnrollmentToken
from app.db.models.organization import Organization
from app.db.session import AsyncSessionLocal
from app.dependencies.database import get_db
from app.main import app
from app.repositories.organization import OrganizationRepository


@pytest.fixture
async def db_session() -> AsyncSession:
    """Fixture providing a transactional session that rolls back after each test."""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(autouse=True)
async def override_db(db_session: AsyncSession):
    """Automatically overrides get_db dependency to use the transactional test session."""
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def test_org(db_session: AsyncSession) -> Organization:
    """Creates a test organization."""
    org_repo = OrganizationRepository(db_session)
    org = await org_repo.create(
        Organization(
            name="Agent Test Org",
            slug="agent-test-org",
            description="Testing agent parameters",
        )
    )
    return org


@pytest.fixture
async def test_token(db_session: AsyncSession, test_org: Organization) -> EnrollmentToken:
    """Creates a valid test enrollment token."""
    token = EnrollmentToken(
        organization_id=test_org.id,
        token_value="esx_et_testtoken123",
        expires_at=datetime.now(UTC) + timedelta(days=1),
        max_uses=5,
        uses_count=0,
        is_active=True,
    )
    db_session.add(token)
    await db_session.flush()
    return token


@pytest.fixture
async def enrolled_agent(db_session: AsyncSession, test_org: Organization) -> tuple[Endpoint, str]:
    """Creates a pre-enrolled test endpoint in the database."""
    secret = "esx_as_testsecretkey999"
    secret_hash = sha256(secret.encode("utf-8")).hexdigest()
    agent_id = uuid4()

    endpoint = Endpoint(
        organization_id=test_org.id,
        hostname="test-host",
        os_platform="windows",
        os_version="10.0.19045",
        hardware_uuid="550e8400-e29b-41d4-a716-446655440000",
        ip_address="192.168.1.15",
        agent_id=agent_id,
        agent_secret_hash=secret_hash,
        lifecycle_state="REGISTERED",
        last_seen=None,
    )
    db_session.add(endpoint)
    await db_session.flush()
    return endpoint, secret


@pytest.mark.anyio
async def test_agent_registration_success(client: AsyncClient, test_token: EnrollmentToken) -> None:
    """Tests successful agent registration via enrollment token."""
    response = await client.post(
        "/api/v1/agent/register",
        json={
            "enrollment_token": test_token.token_value,
            "hostname": "new-host",
            "os_platform": "linux",
            "os_version": "Ubuntu 22.04",
            "hardware_uuid": "550e8400-e29b-41d4-a716-446655441111",
            "ip_address": "10.0.0.5",
        },
    )
    assert response.status_code == 201
    json_data = response.json()
    assert "agent_id" in json_data
    assert "agent_secret" in json_data
    assert json_data["lifecycle_state"] == "REGISTERED"


@pytest.mark.anyio
async def test_agent_registration_expired_token(
    client: AsyncClient, test_token: EnrollmentToken, db_session: AsyncSession
) -> None:
    """Tests registration failure with expired token."""
    test_token.expires_at = datetime.now(UTC) - timedelta(hours=1)
    db_session.add(test_token)
    await db_session.flush()

    response = await client.post(
        "/api/v1/agent/register",
        json={
            "enrollment_token": test_token.token_value,
            "hostname": "new-host",
            "os_platform": "linux",
            "os_version": "Ubuntu 22.04",
            "hardware_uuid": "550e8400-e29b-41d4-a716-446655441111",
            "ip_address": "10.0.0.5",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired enrollment token"


@pytest.mark.anyio
async def test_agent_registration_exhausted_token(
    client: AsyncClient, test_token: EnrollmentToken, db_session: AsyncSession
) -> None:
    """Tests registration failure with exhausted token usages."""
    test_token.uses_count = test_token.max_uses
    db_session.add(test_token)
    await db_session.flush()

    response = await client.post(
        "/api/v1/agent/register",
        json={
            "enrollment_token": test_token.token_value,
            "hostname": "new-host",
            "os_platform": "linux",
            "os_version": "Ubuntu 22.04",
            "hardware_uuid": "550e8400-e29b-41d4-a716-446655441111",
            "ip_address": "10.0.0.5",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Enrollment token usage limit reached"


@pytest.mark.anyio
async def test_agent_registration_duplicate_hardware(
    client: AsyncClient, test_token: EnrollmentToken, enrolled_agent: tuple[Endpoint, str]
) -> None:
    """Tests registration rejection for duplicate hardware UUID."""
    endpoint, _ = enrolled_agent
    response = await client.post(
        "/api/v1/agent/register",
        json={
            "enrollment_token": test_token.token_value,
            "hostname": "another-host",
            "os_platform": "windows",
            "os_version": "11.0",
            "hardware_uuid": endpoint.hardware_uuid,
            "ip_address": "192.168.1.50",
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Endpoint hardware already registered"


@pytest.mark.anyio
async def test_agent_heartbeat_success(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str]
) -> None:
    """Tests successful heartbeat signal from agent."""
    endpoint, secret = enrolled_agent
    headers = {
        "X-Agent-ID": str(endpoint.agent_id),
        "X-Agent-Secret": secret,
    }
    response = await client.post(
        "/api/v1/agent/heartbeat",
        headers=headers,
        json={"status": "healthy", "cpu_pct": 12.5, "ram_pct": 45.2},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["next_heartbeat_seconds"] == 30

    # Verify updated DB fields
    assert endpoint.lifecycle_state == "ONLINE"
    assert endpoint.last_seen is not None


@pytest.mark.anyio
async def test_agent_heartbeat_unauthorized(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str]
) -> None:
    """Tests heartbeat rejection with invalid credentials."""
    endpoint, _ = enrolled_agent
    headers = {
        "X-Agent-ID": str(endpoint.agent_id),
        "X-Agent-Secret": "wrongsecretkey",
    }
    response = await client.post(
        "/api/v1/agent/heartbeat",
        headers=headers,
        json={"status": "healthy", "cpu_pct": 12.5, "ram_pct": 45.2},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Agent ID or Secret"


@pytest.mark.anyio
async def test_agent_rotate_secret_success(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str], db_session: AsyncSession
) -> None:
    """Tests secret rotation API."""
    endpoint, secret = enrolled_agent
    headers = {
        "X-Agent-ID": str(endpoint.agent_id),
        "X-Agent-Secret": secret,
    }
    response = await client.post("/api/v1/agent/rotate-secret", headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    new_secret = json_data["new_agent_secret"]
    assert new_secret != secret
    assert new_secret.startswith("esx_as_")

    # Verify that old secret no longer works
    response_heartbeat_old = await client.post(
        "/api/v1/agent/heartbeat",
        headers=headers,
        json={"status": "healthy", "cpu_pct": 5.0, "ram_pct": 5.0},
    )
    assert response_heartbeat_old.status_code == 401

    # Verify that new secret works
    headers_new = {
        "X-Agent-ID": str(endpoint.agent_id),
        "X-Agent-Secret": new_secret,
    }
    response_heartbeat_new = await client.post(
        "/api/v1/agent/heartbeat",
        headers=headers_new,
        json={"status": "healthy", "cpu_pct": 5.0, "ram_pct": 5.0},
    )
    assert response_heartbeat_new.status_code == 200


@pytest.mark.anyio
async def test_get_agent_config(client: AsyncClient, enrolled_agent: tuple[Endpoint, str]) -> None:
    """Tests agent config retrieval."""
    endpoint, secret = enrolled_agent
    headers = {
        "X-Agent-ID": str(endpoint.agent_id),
        "X-Agent-Secret": secret,
    }
    response = await client.get("/api/v1/agent/config", headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["heartbeat_interval_seconds"] == 30
    assert "policy" in json_data


@pytest.mark.anyio
async def test_decommissioned_agent_rejection(
    client: AsyncClient, enrolled_agent: tuple[Endpoint, str], db_session: AsyncSession
) -> None:
    """Tests that DECOMMISSIONED agents are rejected by the get_current_agent dependency."""
    endpoint, secret = enrolled_agent
    endpoint.lifecycle_state = "DECOMMISSIONED"
    db_session.add(endpoint)
    await db_session.flush()

    headers = {
        "X-Agent-ID": str(endpoint.agent_id),
        "X-Agent-Secret": secret,
    }
    response = await client.post(
        "/api/v1/agent/heartbeat",
        headers=headers,
        json={"status": "healthy", "cpu_pct": 12.5, "ram_pct": 45.2},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Agent is decommissioned"
