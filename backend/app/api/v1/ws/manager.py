import structlog
from fastapi import WebSocket

logger = structlog.get_logger()


class ConnectionManager:
    """Manages real-time WebSocket connections for Endpoint Sentinel X.
    Tracks active agents and clients to stream metrics and dispatch commands.
    """

    def __init__(self):
        # Maps endpoint_id -> set of active WebSockets (allows multiple views per endpoint)
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, endpoint_id: str, websocket: WebSocket) -> None:
        """Accepts a WebSocket connection and registers it under the endpoint ID."""
        await websocket.accept()
        if endpoint_id not in self.active_connections:
            self.active_connections[endpoint_id] = set()
        self.active_connections[endpoint_id].add(websocket)
        logger.info(
            "WebSocket connection established",
            endpoint_id=endpoint_id,
            active_sessions=len(self.active_connections[endpoint_id]),
        )

    def disconnect(self, endpoint_id: str, websocket: WebSocket) -> None:
        """Deregisters a WebSocket connection."""
        if endpoint_id in self.active_connections:
            self.active_connections[endpoint_id].remove(websocket)
            if not self.active_connections[endpoint_id]:
                del self.active_connections[endpoint_id]
            logger.info("WebSocket connection closed", endpoint_id=endpoint_id)

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        """Sends a direct message to a specific client/agent connection."""
        await websocket.send_text(message)

    async def send_json(self, data: dict, websocket: WebSocket) -> None:
        """Sends serialized JSON to a specific client/agent connection."""
        await websocket.send_json(data)

    async def send_to_endpoint(self, endpoint_id: str, message: dict) -> None:
        """Broadcasts a JSON message to all connections monitoring a specific endpoint."""
        if endpoint_id in self.active_connections:
            for connection in self.active_connections[endpoint_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(
                        "Failed to send message to connection",
                        endpoint_id=endpoint_id,
                        error=str(e),
                    )

    async def broadcast(self, message: dict) -> None:
        """Broadcasts a JSON message to all open connections across all endpoints."""
        for endpoint_id, connections in list(self.active_connections.items()):
            for connection in list(connections):
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(
                        "Failed to broadcast to connection",
                        endpoint_id=endpoint_id,
                        error=str(e),
                    )


# Global singleton instance
ws_manager = ConnectionManager()
