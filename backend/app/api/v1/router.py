import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.v1.endpoints import agent, auth, health
from app.api.v1.ws.manager import ws_manager

logger = structlog.get_logger()
api_router = APIRouter()

# Include REST routes
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(agent.router, tags=["Agent"])


@api_router.websocket("/ws/{endpoint_id}")
async def websocket_endpoint(websocket: WebSocket, endpoint_id: str):
    """WebSocket communication endpoint for real-time agent/client streaming.
    Decoupled via centralized ConnectionManager to support horizontal scaling.
    """
    await ws_manager.connect(endpoint_id, websocket)
    try:
        while True:
            # Await data packet transmissions
            data = await websocket.receive_json()
            logger.debug(
                "WebSocket message received",
                endpoint_id=endpoint_id,
                payload=data,
            )
            # Acknowledge received packet back to the sender
            await ws_manager.send_json({"status": "acknowledged", "echo": data}, websocket)
    except WebSocketDisconnect:
        ws_manager.disconnect(endpoint_id, websocket)
    except Exception as e:
        logger.error(
            "Exception occurred in WebSocket lifecycle",
            endpoint_id=endpoint_id,
            error=str(e),
        )
        ws_manager.disconnect(endpoint_id, websocket)
