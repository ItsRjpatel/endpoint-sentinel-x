import uuid
from datetime import UTC, datetime, timedelta

import pytest
from shared.constants.ws_events import CommandStatus

from app.db.models.command import Command
from app.services.dispatcher import CommandDispatcher, IConnectionManager


class MockConnectionManager(IConnectionManager):
    def __init__(self):
        self.online_endpoints = set()
        self.sent_messages = []

    def is_online(self, endpoint_id: str) -> bool:
        return endpoint_id in self.online_endpoints

    async def send(self, endpoint_id: str, message: dict) -> bool:
        if endpoint_id in self.online_endpoints:
            self.sent_messages.append((endpoint_id, message))
            return True
        return False


@pytest.mark.anyio
async def test_dispatcher_timeout(db_session):
    """Verify timeout processing transitions SENT commands to TIMEOUT if threshold passed."""

    # Create mock organization and endpoint to satisfy foreign key
    from hashlib import sha256

    from app.db.models.endpoint import Endpoint
    from app.db.models.organization import Organization

    org_slug = f"test-org-{uuid.uuid4().hex[:8]}"
    org = Organization(name=f"Test Org {uuid.uuid4().hex[:8]}", slug=org_slug)
    db_session.add(org)
    await db_session.flush()

    endpoint = Endpoint(
        organization_id=org.id,
        hostname="test-host",
        os_platform="windows",
        os_version="10",
        hardware_uuid=str(uuid.uuid4()),
        ip_address="127.0.0.1",
        agent_id=uuid.uuid4(),
        agent_secret_hash=sha256(b"secret").hexdigest(),
        lifecycle_state="ONLINE"
    )
    db_session.add(endpoint)
    await db_session.flush()

    # Create an old command
    cmd_id = uuid.uuid4()
    old_command = Command(
        id=cmd_id,
        endpoint_id=endpoint.id,
        command_type="ping",
        status=CommandStatus.SENT,
        created_at=datetime.now(UTC) - timedelta(hours=1)
    )
    db_session.add(old_command)
    await db_session.commit()

    mock_ws = MockConnectionManager()

    # We pass a simple async function generator mock for db_session_factory
    from contextlib import asynccontextmanager
    @asynccontextmanager
    async def mock_session_factory():
        yield db_session

    dispatcher = CommandDispatcher(mock_session_factory, mock_ws, command_timeout_seconds=60)

    # Execute timeout logic
    await dispatcher._process_timeouts()

    # Refresh command
    await db_session.refresh(old_command)

    assert old_command.status == CommandStatus.TIMEOUT
    assert "Command timed out" in old_command.error
