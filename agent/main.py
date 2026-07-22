import asyncio
import sys

import structlog

from communication.websocket_client import WebSocketClient
from inventory_sync import (
    sync_hardware,
    sync_os,
    sync_security,
    sync_network,
    sync_storage,
    sync_software,
    sync_windows_updates,
    sync_services,
    sync_services,
    sync_local_users,
)
from collectors.performance import collect as collect_performance
from api.heartbeat import submit_heartbeat

# Set up logging for agent
logging_processors = [
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.add_log_level,
    structlog.processors.format_exc_info,
    structlog.dev.ConsoleRenderer(colors=True),
]
structlog.configure(processors=logging_processors)
logger = structlog.get_logger()


async def scheduled_inventory_loop():
    """Periodically triggers REST inventory syncs."""
    logger.info("Starting scheduled REST inventory sync loop")
    
    # Run an initial full sync
    sync_list = [
        sync_hardware,
        sync_os,
        sync_security,
        sync_network,
        sync_storage,
        sync_software,
        sync_windows_updates,
        sync_services,
        sync_local_users,
    ]
    
    while True:
        try:
            logger.info("Executing scheduled inventory sync batch")
            for sync_func in sync_list:
                # Run sync functions in thread pool since they are currently blocking
                await asyncio.to_thread(sync_func)
                await asyncio.sleep(2)  # Stagger to avoid bursting API
                
            logger.info("Inventory sync batch completed. Sleeping until next schedule.")
            # Sleep for an hour before next full sync (example schedule)
            await asyncio.sleep(3600)
            
        except asyncio.CancelledError:
            logger.info("Inventory sync loop cancelled.")
            break
        except Exception as e:
            logger.error("Error in scheduled inventory loop", error=str(e))
            await asyncio.sleep(60)


async def scheduled_heartbeat_loop():
    """Periodically sends REST heartbeats with live performance data."""
    logger.info("Starting scheduled heartbeat loop")
    while True:
        try:
            perf = await asyncio.to_thread(collect_performance)
            await asyncio.to_thread(
                submit_heartbeat, 
                status="healthy",
                cpu=perf.cpu_usage_percent,
                ram=perf.memory_usage_percent,
                disk=perf.disk_usage_percent,
                net_in=perf.network_in_bytes,
                net_out=perf.network_out_bytes
            )
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            logger.info("Heartbeat loop cancelled.")
            break
        except Exception as e:
            logger.error("Error in scheduled heartbeat loop", error=str(e))
            await asyncio.sleep(30)


async def main() -> None:
    logger.info("Initializing Endpoint Sentinel X Agent Sprint 4...")
    logger.info("Operating System Platform detected", platform=sys.platform)

    ws_client = WebSocketClient()
    
    try:
        # Run WebSocket client and scheduled inventory concurrently
        await asyncio.gather(
            ws_client.start(),
            scheduled_inventory_loop(),
            scheduled_heartbeat_loop()
        )
    except asyncio.CancelledError:
        logger.info("Shutting down agent gracefully...")
        ws_client.stop()
    except Exception as e:
        logger.error("Unexpected error in agent core event loop", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Agent stopped by user interrupt.")
