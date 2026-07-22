import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from shared.constants.ws_events import CommandStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.command import Command


class CommandRepository:
    """Repository for managing Command entities in the database."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, command: Command) -> Command:
        self.db.add(command)
        await self.db.flush()
        return command

    async def get_by_id(self, command_id: uuid.UUID) -> Command | None:
        stmt = select(Command).where(Command.id == command_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_endpoint(self, endpoint_id: uuid.UUID) -> Sequence[Command]:
        stmt = select(Command).where(Command.endpoint_id == endpoint_id).order_by(Command.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def claim_pending_commands(self) -> Sequence[Command]:
        """
        Atomically fetches and transitions PENDING commands to QUEUED using row-level locking.
        This prevents duplicate dispatch in multi-worker environments.
        """
        # Select for update skip locked
        stmt = (
            select(Command)
            .where(Command.status == CommandStatus.PENDING)
            .with_for_update(skip_locked=True)
        )
        result = await self.db.execute(stmt)
        commands = result.scalars().all()

        now = datetime.now(UTC)
        for cmd in commands:
            cmd.status = CommandStatus.QUEUED
            cmd.queued_at = now

        await self.db.flush()
        return commands

    async def get_timed_out_commands(self, timeout_threshold: datetime) -> Sequence[Command]:
        """Fetch commands that have been SENT or RUNNING for too long."""
        stmt = (
            select(Command)
            .where(
                Command.status.in_([CommandStatus.SENT, CommandStatus.RUNNING]),
                Command.created_at < timeout_threshold
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, command: Command) -> Command:
        await self.db.flush()
        return command
