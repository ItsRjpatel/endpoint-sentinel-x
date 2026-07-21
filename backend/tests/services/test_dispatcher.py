import pytest
import uuid
from datetime import datetime, UTC, timedelta

from app.services.dispatcher import CommandDispatcher, IConnectionManager
from app.db.models.command import Command
from shared.constants.ws_events import CommandStatus

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


@pytest.mark.asyncio
async def test_dispatcher_timeout(db_session):
    """Verify timeout processing transitions SENT commands to TIMEOUT if threshold passed."""
    
    # Create an old command
    cmd_id = uuid.uuid4()
    old_command = Command(
        id=cmd_id,
        endpoint_id=uuid.uuid4(),
        command_type="ping",
        status=CommandStatus.SENT,
        created_at=datetime.now(UTC) - timedelta(hours=1),
        updated_at=datetime.now(UTC) - timedelta(hours=1)
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
