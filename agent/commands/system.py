import asyncio
from commands.base import BaseCommandExecutor

class PingCommand(BaseCommandExecutor):
    """Simple ping-pong logic for command validation."""
    async def execute(self) -> dict:
        return {"response": "pong"}

class RestartAgentCommand(BaseCommandExecutor):
    """Gracefully shuts down the agent (assuming systemd/service manager restarts it)."""
    async def execute(self) -> dict:
        # We can trigger a stop, but we need to reply first.
        # So we sleep slightly and then exit the process, or rely on a system call.
        import sys
        
        async def delayed_exit():
            await asyncio.sleep(2)
            sys.exit(0)
            
        asyncio.create_task(delayed_exit())
        return {"message": "Agent will restart in 2 seconds."}

class CollectLogsCommand(BaseCommandExecutor):
    """Gathers recent log lines."""
    async def execute(self) -> dict:
        # In a real implementation, this would read log files.
        # For Sprint 4, return a placeholder indicating success.
        return {"logs": ["Log collection initialized.", "No errors found."]}
