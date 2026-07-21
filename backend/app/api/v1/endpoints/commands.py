import uuid
from typing import Sequence
import structlog

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.command import Command
from app.dependencies.database import get_db
from app.schemas.command import CommandCreate, CommandResponse
from app.services.command import CommandService

logger = structlog.get_logger()
router = APIRouter(prefix="/commands")


@router.post("", response_model=CommandResponse, status_code=status.HTTP_201_CREATED)
async def create_command(
    endpoint_id: uuid.UUID,
    command_in: CommandCreate,
    db: AsyncSession = Depends(get_db),
) -> Command:
    """Queue a new remote command for an endpoint."""
    service = CommandService(db)
    command = await service.create_command(endpoint_id, command_in)
    await db.commit()
    return command


@router.get("/endpoint/{endpoint_id}", response_model=list[CommandResponse])
async def get_endpoint_commands(
    endpoint_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Sequence[Command]:
    """Fetch the command history for a specific endpoint."""
    service = CommandService(db)
    return await service.get_commands_for_endpoint(endpoint_id)


@router.get("/{command_id}", response_model=CommandResponse)
async def get_command(
    command_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Command:
    """Fetch the status of a specific command."""
    service = CommandService(db)
    command = await service.get_command_by_id(command_id)
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    return command
