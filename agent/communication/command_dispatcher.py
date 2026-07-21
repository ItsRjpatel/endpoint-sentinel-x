import time
import structlog
from typing import Callable, Awaitable

from shared.constants.ws_events import WSEventType, CommandStatus
from commands.registry import get_command_executor

logger = structlog.get_logger(__name__)


async def dispatch_command(payload: dict, send_envelope: Callable[[WSEventType, dict], Awaitable[None]]):
    """
    Parses an incoming command payload, executes the registered handler,
    and streams ACK and RESULT back to the backend.
    """
    command_id = payload.get("id")
    command_type = payload.get("command_type")
    
    if not command_id or not command_type:
        logger.error("Received command request missing ID or Type", payload=payload)
        return

    # 1. Send ACK
    logger.info("Acknowledging command", command_id=command_id, command_type=command_type)
    await send_envelope(WSEventType.CMD_ACK, {
        "command_id": command_id,
        "status": CommandStatus.ACKNOWLEDGED.value
    })

    # 2. Resolve Executor
    executor_class = get_command_executor(command_type)
    if not executor_class:
        logger.error("No registered executor for command type", command_type=command_type)
        await send_envelope(WSEventType.CMD_RESULT, {
            "command_id": command_id,
            "status": CommandStatus.FAILED.value,
            "error": f"Unsupported command type: {command_type}",
            "execution_duration": 0
        })
        return

    # 3. Mark RUNNING
    await send_envelope(WSEventType.CMD_ACK, {
        "command_id": command_id,
        "status": CommandStatus.RUNNING.value
    })

    # 4. Execute
    t0 = time.monotonic()
    executor = executor_class(payload)
    
    try:
        result_json = await executor.execute()
        status = CommandStatus.SUCCESS
        error = None
    except Exception as e:
        logger.error("Command execution failed", command_id=command_id, error=str(e))
        result_json = None
        status = CommandStatus.FAILED
        error = str(e)

    duration_ms = int((time.monotonic() - t0) * 1000)

    # 5. Send RESULT
    await send_envelope(WSEventType.CMD_RESULT, {
        "command_id": command_id,
        "status": status.value,
        "error": error,
        "result_json": result_json,
        "execution_duration": duration_ms
    })
    
    logger.info(
        "Command completed",
        command_id=command_id,
        status=status.value,
        duration_ms=duration_ms
    )
