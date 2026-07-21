from hashlib import sha256
from uuid import UUID
import structlog

from fastapi import Depends, Header, HTTPException, status, WebSocketException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.endpoint import Endpoint
from app.dependencies.database import get_db

logger = structlog.get_logger()


async def get_current_agent(
    x_agent_id: UUID = Header(..., alias="X-Agent-ID"),
    x_agent_secret: str = Header(..., alias="X-Agent-Secret"),
    db: AsyncSession = Depends(get_db),
) -> Endpoint:
    """Authenticates the agent using X-Agent-ID and X-Agent-Secret headers."""
    stmt = select(Endpoint).where(Endpoint.agent_id == x_agent_id)
    result = await db.execute(stmt)
    endpoint = result.scalar_one_or_none()

    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Agent ID or Secret",
        )

    if endpoint.lifecycle_state == "DECOMMISSIONED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent is decommissioned",
        )

    # Verify secret hash
    expected_hash = sha256(x_agent_secret.encode("utf-8")).hexdigest()
    if endpoint.agent_secret_hash != expected_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Agent ID or Secret",
        )

    return endpoint


async def get_current_agent_ws(
    x_agent_id: UUID = Header(..., alias="X-Agent-ID"),
    x_agent_secret: str = Header(..., alias="X-Agent-Secret"),
    db: AsyncSession = Depends(get_db),
) -> Endpoint:
    """Authenticates the agent for WebSocket upgrades, raising WebSocketException on failure."""
    stmt = select(Endpoint).where(Endpoint.agent_id == x_agent_id)
    result = await db.execute(stmt)
    endpoint = result.scalar_one_or_none()

    if not endpoint:
        logger.warning("WS Auth Failed: Invalid Agent ID", agent_id=str(x_agent_id))
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid Agent ID or Secret")

    if endpoint.lifecycle_state == "DECOMMISSIONED":
        logger.warning("WS Auth Failed: Decommissioned", agent_id=str(x_agent_id))
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Agent is decommissioned")

    # Verify secret hash
    expected_hash = sha256(x_agent_secret.encode("utf-8")).hexdigest()
    if endpoint.agent_secret_hash != expected_hash:
        logger.warning("WS Auth Failed: Invalid Secret", agent_id=str(x_agent_id))
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid Agent ID or Secret")

    logger.info("WS Auth Success", agent_id=str(x_agent_id))
    return endpoint
