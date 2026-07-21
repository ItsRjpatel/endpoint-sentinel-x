import uuid
from datetime import datetime, UTC
import structlog

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.command import Command
from app.repositories.command import CommandRepository
from app.schemas.command import CommandCreate
from shared.constants.ws_events import CommandStatus

logger = structlog.get_logger()


class CommandService:
    """Service layer for Commands. 
    Handles validation, orchestration, and business rules."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CommandRepository(db)

    async def create_command(self, endpoint_id: uuid.UUID, command_in: CommandCreate) -> Command:
        """Creates a new command in PENDING state."""
        cmd = Command(
            endpoint_id=endpoint_id,
            command_type=command_in.command_type,
            command_version=command_in.command_version,
            parameters=command_in.parameters,
            status=CommandStatus.PENDING,
            created_at=datetime.now(UTC),
            queued_at=datetime.now(UTC)
        )
        
        created = await self.repo.create(cmd)
        logger.info("Command queued", command_id=str(created.id), endpoint_id=str(endpoint_id), command_type=created.command_type)
        return created

    async def get_commands_for_endpoint(self, endpoint_id: uuid.UUID) -> list[Command]:
        """Fetch command history for an endpoint."""
        commands = await self.repo.get_by_endpoint(endpoint_id)
        return list(commands)
    
    async def get_command_by_id(self, command_id: uuid.UUID) -> Command | None:
        """Fetch a specific command."""
        return await self.repo.get_by_id(command_id)

    async def update_command_status(
        self, 
        command_id: uuid.UUID, 
        status: str, 
        timestamp: datetime,
        error: str | None = None,
        result_json: dict | None = None,
        execution_duration: int | None = None
    ) -> Command | None:
        """Update command state based on Agent ACKs/Results."""
        command = await self.repo.get_by_id(command_id)
        if not command:
            return None

        command.status = status
        
        if status == CommandStatus.ACKNOWLEDGED:
            command.acknowledged_at = timestamp
        elif status == CommandStatus.RUNNING:
            command.started_at = timestamp
        elif status in [CommandStatus.SUCCESS, CommandStatus.FAILED, CommandStatus.TIMEOUT]:
            command.completed_at = timestamp

        if error is not None:
            command.error = error
        if result_json is not None:
            command.result_json = result_json
        if execution_duration is not None:
            command.execution_duration = execution_duration

        updated = await self.repo.update(command)
        
        logger.info(
            "Command status updated",
            command_id=str(command_id),
            status=status,
            endpoint_id=str(command.endpoint_id)
        )
        
        return updated
