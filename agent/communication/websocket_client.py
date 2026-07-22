import asyncio
import json
import uuid
import structlog
from datetime import datetime, UTC

import websockets
from websockets.exceptions import ConnectionClosed

from config.settings import agent_settings
from shared.constants.ws_events import WSEventType
from communication.command_dispatcher import dispatch_command

logger = structlog.get_logger(__name__)


class WebSocketClient:
    """
    Persistent WebSocket client for real-time orchestration.
    Maintains connection, handles authentication, ping/pong heartbeats, 
    and routes incoming commands.
    """

    def __init__(self):
        # Convert HTTP URL to WS URL
        base_url = agent_settings.api_base_url.replace("http://", "ws://").replace("https://", "wss://")
        self.uri = f"{base_url}/api/v1/ws"
        self.headers = {
            "X-Agent-ID": str(agent_settings.agent_id),
            "X-Agent-Secret": agent_settings.agent_secret,
            "X-Agent-Version": agent_settings.agent_version,
        }
        self.connection = None
        self._running = False
        self._reconnect_delay = 1.0
        self._max_delay = 60.0

    async def start(self):
        """Starts the persistent connection loop."""
        self._running = True
        logger.info("Starting WebSocket client loop", uri=self.uri)
        
        while self._running:
            try:
                async with websockets.connect(self.uri, additional_headers=self.headers) as websocket:
                    self.connection = websocket
                    self._reconnect_delay = 1.0  # Reset delay on successful connect
                    logger.info("WebSocket connected successfully")
                    
                    # Start receiver and heartbeat loops concurrently
                    receiver_task = asyncio.create_task(self._receive_loop())
                    heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                    
                    done, pending = await asyncio.wait(
                        [receiver_task, heartbeat_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    for task in pending:
                        task.cancel()
                        
            except ConnectionClosed as e:
                logger.warning("WebSocket connection closed", code=e.code, reason=e.reason)
            except Exception as e:
                logger.error("WebSocket connection error", error=str(e))
                
            if self._running:
                logger.info(f"Reconnecting in {self._reconnect_delay} seconds...")
                await asyncio.sleep(self._reconnect_delay)
                self._reconnect_delay = min(self._reconnect_delay * 2, self._max_delay)

    def stop(self):
        """Stops the client loop."""
        self._running = False
        if self.connection:
            asyncio.create_task(self.connection.close())

    async def send_envelope(self, event: WSEventType, payload: dict):
        """Sends a structured envelope to the backend."""
        if not self.connection:
            logger.error("Cannot send message, WebSocket is not connected")
            return

        envelope = {
            "schema_version": 1,
            "event": event.value,
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "payload": payload
        }
        await self.connection.send(json.dumps(envelope))

    async def _heartbeat_loop(self):
        """Periodically sends PING to the backend."""
        while self._running and self.connection:
            try:
                await self.send_envelope(WSEventType.PING, {})
                await asyncio.sleep(30)
            except Exception as e:
                logger.error("Error in heartbeat loop", error=str(e))
                break

    async def _receive_loop(self):
        """Listens for incoming messages from the backend."""
        async for message in self.connection:
            try:
                data = json.loads(message)
                event = data.get("event")
                payload = data.get("payload", {})
                
                if event == WSEventType.AUTH_OK:
                    logger.info("WebSocket authenticated successfully")
                elif event == WSEventType.PONG:
                    logger.debug("Received PONG from backend")
                elif event == WSEventType.CMD_REQUEST:
                    logger.info("Received command request", command_id=payload.get("id"))
                    # Dispatch to the executor registry without blocking the receive loop
                    asyncio.create_task(dispatch_command(payload, self.send_envelope))
                else:
                    logger.debug("Received unhandled event", event=event)
                    
            except json.JSONDecodeError:
                logger.error("Received malformed JSON message")
            except Exception as e:
                logger.error("Error processing incoming message", error=str(e))
