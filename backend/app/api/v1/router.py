import structlog
from datetime import datetime, UTC
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.api.v1.endpoints import agent, auth, health, inventory, commands
from app.api.v1.ws.manager import ws_manager
from app.dependencies.agent import get_current_agent_ws
from app.dependencies.database import get_db
from app.db.models.endpoint import Endpoint
from app.schemas.ws import WSEnvelope
from shared.constants.ws_events import WSEventType
from app.services.command import CommandService

logger = structlog.get_logger()
api_router = APIRouter()

# Include REST routes
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(agent.router, tags=["Agent"])
api_router.include_router(inventory.router, tags=["Inventory"])
api_router.include_router(commands.router, tags=["Commands"])


@api_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    current_agent: Endpoint = Depends(get_current_agent_ws),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticated WebSocket endpoint for real-time agent streams.
    The agent must send X-Agent-ID and X-Agent-Secret headers during the upgrade request.
    """
    endpoint_id_str = str(current_agent.id)
    
    # Extract agent version from headers if available
    agent_version = websocket.headers.get("x-agent-version", "unknown")
    
    await websocket.accept()
    ws_manager.register(endpoint_id_str, websocket, agent_version=agent_version)
    
    # Send AUTH_OK envelope
    await ws_manager.send(endpoint_id_str, WSEnvelope(
        event=WSEventType.AUTH_OK,
        payload={"message": "Authentication successful"}
    ).model_dump(mode="json"))

    service = CommandService(db)

    try:
        while True:
            # Await strict envelope structured data
            data = await websocket.receive_json()
            
            try:
                envelope = WSEnvelope.model_validate(data)
            except ValidationError as ve:
                logger.warning("Invalid WebSocket envelope received", endpoint_id=endpoint_id_str, error=str(ve))
                await ws_manager.send(endpoint_id_str, WSEnvelope(
                    event=WSEventType.ERROR,
                    payload={"error": "Invalid envelope format"}
                ).model_dump(mode="json"))
                continue

            if envelope.event == WSEventType.PING:
                ws_manager.heartbeat(endpoint_id_str)
                await ws_manager.send(endpoint_id_str, WSEnvelope(
                    event=WSEventType.PONG,
                    payload={"acknowledged_request": str(envelope.request_id)}
                ).model_dump(mode="json"))

            elif envelope.event == WSEventType.CMD_ACK:
                payload = envelope.payload
                if payload and isinstance(payload, dict):
                    cmd_id_str = payload.get("command_id")
                    status = payload.get("status")
                    if cmd_id_str and status:
                        await service.update_command_status(
                            command_id=UUID(cmd_id_str),
                            status=status,
                            timestamp=datetime.now(UTC)
                        )
                        await db.commit()

            elif envelope.event == WSEventType.CMD_RESULT:
                payload = envelope.payload
                if payload and isinstance(payload, dict):
                    cmd_id_str = payload.get("command_id")
                    status = payload.get("status")
                    error = payload.get("error")
                    result_json = payload.get("result_json")
                    execution_duration = payload.get("execution_duration")
                    
                    if cmd_id_str and status:
                        await service.update_command_status(
                            command_id=UUID(cmd_id_str),
                            status=status,
                            timestamp=datetime.now(UTC),
                            error=error,
                            result_json=result_json,
                            execution_duration=execution_duration
                        )
                        await db.commit()

            else:
                logger.debug("Received unhandled WS event", event=envelope.event, endpoint_id=endpoint_id_str)

    except WebSocketDisconnect:
        logger.info("Agent disconnected normally", endpoint_id=endpoint_id_str)
    except Exception as e:
        logger.error(
            "Exception occurred in WebSocket lifecycle",
            endpoint_id=endpoint_id_str,
            error=str(e),
        )
    finally:
        ws_manager.unregister(endpoint_id_str)
