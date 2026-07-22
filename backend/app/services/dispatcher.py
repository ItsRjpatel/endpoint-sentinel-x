import asyncio
from datetime import UTC, datetime, timedelta
from typing import Protocol

import structlog
from shared.constants.ws_events import CommandStatus, WSEventType

from app.repositories.command import CommandRepository
from app.schemas.command import CommandResponse
from app.schemas.ws import WSEnvelope

logger = structlog.get_logger()


class IConnectionManager(Protocol):
    """Protocol defining the required methods for a WebSocket connection manager."""
    def is_online(self, endpoint_id: str) -> bool: ...
    async def send(self, endpoint_id: str, message: dict) -> bool: ...


class CommandDispatcher:
    """
    Async Dispatcher for delivering queued commands to connected endpoints.
    Uses row-level locking (FOR UPDATE SKIP LOCKED) to safely claim commands.
    """

    def __init__(self, db_session_factory, connection_manager: IConnectionManager, command_timeout_seconds: int = 60):
        self.db_session_factory = db_session_factory
        self.connection_manager = connection_manager
        self.command_timeout_seconds = command_timeout_seconds
        self._running = False
        self._task = None

    def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._poll_loop())
            logger.info("Command Dispatcher started")

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
        logger.info("Command Dispatcher stopped")

    async def _poll_loop(self):
        while self._running:
            try:
                await self._process_pending_commands()
                await self._process_timeouts()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in dispatcher loop", error=str(e))
            await asyncio.sleep(2)  # Poll interval

    async def _process_pending_commands(self):
        async with self.db_session_factory() as db:
            repo = CommandRepository(db)

            # Atomically claims PENDING -> QUEUED
            commands = await repo.claim_pending_commands()

            if commands:
                await db.commit() # Commit the lock transition first

            for command in commands:
                endpoint_id = str(command.endpoint_id)

                if not self.connection_manager.is_online(endpoint_id):
                    # We leave it as QUEUED. The timeout loop will eventually clean it up.
                    continue

                # Update status to SENT
                command.status = CommandStatus.SENT
                command.sent_at = datetime.now(UTC)
                await repo.update(command)
                await db.commit()

                # Dispatch over WS
                envelope = WSEnvelope(
                    event=WSEventType.CMD_REQUEST,
                    payload=CommandResponse.model_validate(command)
                )

                success = await self.connection_manager.send(endpoint_id, envelope.model_dump(mode="json"))

                if success:
                    logger.info("Command dispatched", command_id=str(command.id), endpoint_id=endpoint_id)
                else:
                    # Connection dropped exactly during send
                    command.status = CommandStatus.QUEUED
                    command.sent_at = None
                    await repo.update(command)
                    await db.commit()
                    logger.warning("Failed to dispatch command, reverted to QUEUED", command_id=str(command.id))

    async def _process_timeouts(self):
        async with self.db_session_factory() as db:
            repo = CommandRepository(db)
            threshold = datetime.now(UTC) - timedelta(seconds=self.command_timeout_seconds)
            timed_out_commands = await repo.get_timed_out_commands(threshold)

            for command in timed_out_commands:
                command.status = CommandStatus.TIMEOUT
                command.completed_at = datetime.now(UTC)
                command.error = f"Command timed out after {self.command_timeout_seconds} seconds"
                await repo.update(command)

            if timed_out_commands:
                await db.commit()
                logger.warning("Processed command timeouts", count=len(timed_out_commands))
