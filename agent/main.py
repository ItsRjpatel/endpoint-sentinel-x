import asyncio
import sys

import structlog

# Set up logging for agent
logging_processors = [
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.add_log_level,
    structlog.processors.format_exc_info,
    structlog.dev.ConsoleRenderer(colors=True),
]
structlog.configure(processors=logging_processors)
logger = structlog.get_logger()


async def main() -> None:
    logger.info("Initializing Endpoint Sentinel X Agent...")
    logger.info("Operating System Platform detected", platform=sys.platform)

    # Placeholder for configuration and websocket loops
    try:
        while True:
            logger.debug("Agent heartbeat: telemetry collectors active.")
            await asyncio.sleep(10)
    except asyncio.CancelledError:
        logger.info("Shutting down agent gracefully...")
    except Exception as e:
        logger.error("Unexpected error in agent core event loop", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Agent stopped by user interrupt.")
