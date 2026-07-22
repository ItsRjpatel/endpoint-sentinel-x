import secrets
import uuid
from datetime import UTC, datetime
from hashlib import sha256
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.endpoint import Endpoint
from app.db.models.enrollment_token import EnrollmentToken
from app.dependencies.agent import get_current_agent
from app.dependencies.database import get_db
from app.schemas.agent import (
    AgentConfigResponse,
    AgentHeartbeatRequest,
    AgentHeartbeatResponse,
    AgentRegisterRequest,
    AgentRegisterResponse,
    AgentRotateSecretResponse,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=AgentRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new agent endpoint using an enrollment token",
)
async def register_agent(
    payload: AgentRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AgentRegisterResponse:
    """Validates enrollment token, checks for duplicates, and provisions new agent credentials."""
    # 1. Validate Enrollment Token
    stmt = select(EnrollmentToken).where(EnrollmentToken.token_value == payload.enrollment_token)
    result = await db.execute(stmt)
    token = result.scalar_one_or_none()

    if not token or not token.is_active or token.expires_at < datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired enrollment token",
        )

    if token.uses_count >= token.max_uses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enrollment token usage limit reached",
        )

    # 2. Check for duplicate hardware_uuid
    dup_stmt = select(Endpoint).where(Endpoint.hardware_uuid == payload.hardware_uuid)
    dup_result = await db.execute(dup_stmt)
    if dup_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Endpoint hardware already registered",
        )

    # 3. Generate credentials
    agent_id = uuid.uuid4()
    agent_secret = "esx_as_" + secrets.token_hex(32)
    agent_secret_hash = sha256(agent_secret.encode("utf-8")).hexdigest()

    # 4. Create Endpoint record
    endpoint = Endpoint(
        organization_id=token.organization_id,
        hostname=payload.hostname,
        os_platform=payload.os_platform,
        os_version=payload.os_version,
        hardware_uuid=payload.hardware_uuid,
        ip_address=payload.ip_address,
        agent_id=agent_id,
        agent_secret_hash=agent_secret_hash,
        lifecycle_state="REGISTERED",
        last_seen=None,
    )
    db.add(endpoint)

    # Increment token usage
    token.uses_count += 1
    db.add(token)

    await db.flush()

    return AgentRegisterResponse(
        agent_id=agent_id,
        agent_secret=agent_secret,
        lifecycle_state="REGISTERED",
    )


@router.post(
    "/heartbeat",
    response_model=AgentHeartbeatResponse,
    summary="Record periodic agent heartbeat and update connection status",
)
async def agent_heartbeat(
    payload: AgentHeartbeatRequest,
    current_agent: Annotated[Endpoint, Depends(get_current_agent)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AgentHeartbeatResponse:
    """Updates last_seen, records health metrics, and transitions state to ONLINE."""
    current_agent.last_seen = datetime.now(UTC)

    if current_agent.lifecycle_state in ("REGISTERED", "OFFLINE"):
        current_agent.lifecycle_state = "ONLINE"

    db.add(current_agent)
    await db.flush()

    return AgentHeartbeatResponse(
        status="success",
        next_heartbeat_seconds=30,
    )


@router.post(
    "/rotate-secret",
    response_model=AgentRotateSecretResponse,
    summary="Rotate the authenticated agent secret API key",
)
async def rotate_agent_secret(
    current_agent: Annotated[Endpoint, Depends(get_current_agent)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AgentRotateSecretResponse:
    """Generates and registers a new secure agent secret key, invalidating the old one."""
    new_secret = "esx_as_" + secrets.token_hex(32)
    current_agent.agent_secret_hash = sha256(new_secret.encode("utf-8")).hexdigest()

    db.add(current_agent)
    await db.flush()

    return AgentRotateSecretResponse(new_agent_secret=new_secret)


@router.get(
    "/config",
    response_model=AgentConfigResponse,
    summary="Fetch runtime configurations and policy metrics for the agent",
)
async def get_agent_config(
    current_agent: Annotated[Endpoint, Depends(get_current_agent)],
) -> AgentConfigResponse:
    """Returns interval policies and commands setup mapping for the active host."""
    return AgentConfigResponse(
        heartbeat_interval_seconds=30,
        policy={},
    )
