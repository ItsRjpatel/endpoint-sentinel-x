import asyncio
import json
from commands.base import BaseCommandExecutor
from utils.powershell import run_powershell

class GetProcessesCommand(BaseCommandExecutor):
    """Retrieves a list of running processes on the endpoint."""
    async def execute(self) -> dict:
        # Get-Process is a safe read-only cmdlet.
        # Compress removes extra whitespace.
        script = """
        $ErrorActionPreference = 'Stop'
        Get-Process | Select-Object Id, ProcessName, CPU, WorkingSet | ConvertTo-Json -Compress
        """
        loop = asyncio.get_running_loop()
        
        # run_powershell returns str | None
        output = await loop.run_in_executor(None, run_powershell, script)
        
        if output is None:
            raise RuntimeError("Failed to get processes or PowerShell timed out.")
            
        try:
            processes = json.loads(output)
            # PowerShell's ConvertTo-Json might return a single object if there's only 1 process
            if not isinstance(processes, list):
                processes = [processes]
        except json.JSONDecodeError:
            raise RuntimeError("Failed to parse process output from PowerShell.")
            
        return {"processes": processes}
