from datetime import UTC, datetime

import structlog
from fastapi import WebSocket

logger = structlog.get_logger()


class ConnectionState:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.connected_since: datetime = datetime.now(UTC)
        self.last_seen: datetime = datetime.now(UTC)
        self.latency_ms: int = 0
        self.heartbeat_failures: int = 0
        self.agent_version: str = "unknown"

    def record_heartbeat(self, latency_ms: int = 0):
        self.last_seen = datetime.now(UTC)
        self.heartbeat_failures = 0
        self.latency_ms = latency_ms


class ConnectionManager:
    """Enterprise ConnectionManager.
    Tracks active agents and clients for real-time orchestration.
    Responsibilities: Register, unregister, get connection, send, broadcast, is_online.
    NO business logic.
    """

    def __init__(self):
        # Maps endpoint_id -> ConnectionState
        # Note: In a scaled environment, this would coordinate with Redis.
        self.active_connections: dict[str, ConnectionState] = {}

    def register(self, endpoint_id: str, websocket: WebSocket, agent_version: str = "unknown") -> None:
        """Registers a newly authenticated WebSocket connection."""
        state = ConnectionState(websocket)
        state.agent_version = agent_version
        self.active_connections[endpoint_id] = state

        logger.info(
            "Agent connected via WebSocket",
            endpoint_id=endpoint_id,
            agent_version=agent_version,
            active_sessions=len(self.active_connections),
        )

    def unregister(self, endpoint_id: str) -> None:
        """Deregisters a WebSocket connection."""
        if endpoint_id in self.active_connections:
            del self.active_connections[endpoint_id]
            logger.info("Agent disconnected", endpoint_id=endpoint_id)

    def get_connection(self, endpoint_id: str) -> ConnectionState | None:
        return self.active_connections.get(endpoint_id)

    def is_online(self, endpoint_id: str) -> bool:
        return endpoint_id in self.active_connections

    async def send(self, endpoint_id: str, message: dict) -> bool:
        """Sends a JSON message to a specific endpoint. Returns True if successful."""
        state = self.get_connection(endpoint_id)
        if state:
            try:
                await state.websocket.send_json(message)
                return True
            except Exception as e:
                logger.error(
                    "Failed to send message to connection",
                    endpoint_id=endpoint_id,
                    error=str(e),
                )
                self.unregister(endpoint_id)
        return False

    async def broadcast(self, message: dict) -> None:
        """Broadcasts a JSON message to all open connections."""
        for endpoint_id, state in list(self.active_connections.items()):
            try:
                await state.websocket.send_json(message)
            except Exception as e:
                logger.error(
                    "Failed to broadcast to connection",
                    endpoint_id=endpoint_id,
                    error=str(e),
                )
                self.unregister(endpoint_id)

    def heartbeat(self, endpoint_id: str, latency_ms: int = 0) -> None:
        state = self.get_connection(endpoint_id)
        if state:
            state.record_heartbeat(latency_ms)

    def last_seen(self, endpoint_id: str) -> datetime | None:
        state = self.get_connection(endpoint_id)
        if state:
            return state.last_seen
        return None


# Global singleton instance
ws_manager = ConnectionManager()
