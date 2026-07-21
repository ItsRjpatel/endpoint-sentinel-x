import asyncio
import re
import subprocess
from commands.base import BaseCommandExecutor

# Strict regex to ensure no shell injection or weird characters.
# Windows service names can contain letters, numbers, spaces, dashes, and underscores.
SERVICE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\- ]+$")

class ServiceCommandBase(BaseCommandExecutor):
    """Base class for service commands providing validation and existence checks."""

    def _validate_service_name(self, service_name: str | None) -> str:
        if not service_name:
            raise ValueError("Missing 'service_name' parameter.")
        
        service_name = service_name.strip()
        
        if not SERVICE_NAME_PATTERN.match(service_name):
            raise ValueError("Invalid 'service_name'. Contains forbidden characters.")
            
        return service_name

    async def _check_service_exists(self, service_name: str) -> bool:
        loop = asyncio.get_running_loop()
        try:
            # sc.exe query returns non-zero if the service does not exist
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    ["sc.exe", "query", service_name],
                    capture_output=True,
                    text=True
                )
            )
            return result.returncode == 0
        except FileNotFoundError:
            raise RuntimeError("Windows Service Control Manager (sc.exe) not found.")
        except Exception as e:
            raise RuntimeError(f"Error checking service existence: {str(e)}")


class RestartServiceCommand(ServiceCommandBase):
    """Restarts a specified Windows service."""
    async def execute(self) -> dict:
        service_name = self._validate_service_name(self.parameters.get("service_name"))
        
        if not await self._check_service_exists(service_name):
            raise ValueError(f"Service '{service_name}' does not exist.")

        # Note: sc.exe does not have a direct "restart" command. 
        # We must stop and then start the service.
        loop = asyncio.get_running_loop()
        
        def run_sc(action: str):
            return subprocess.run(
                ["sc.exe", action, service_name],
                capture_output=True,
                text=True
            )

        # Stop the service
        stop_result = await loop.run_in_executor(None, run_sc, "stop")
        if stop_result.returncode != 0 and "1062" not in stop_result.stdout:
            # 1062 is ERROR_SERVICE_NOT_ACTIVE
            raise RuntimeError(f"Failed to stop service: {stop_result.stderr.strip() or stop_result.stdout.strip()}")
            
        # Give it a tiny bit of time to fully stop before starting
        await asyncio.sleep(1)
            
        # Start the service
        start_result = await loop.run_in_executor(None, run_sc, "start")
        if start_result.returncode != 0 and "1056" not in start_result.stdout:
            # 1056 is ERROR_SERVICE_ALREADY_RUNNING
            raise RuntimeError(f"Failed to start service: {start_result.stderr.strip() or start_result.stdout.strip()}")
            
        return {"message": f"Service '{service_name}' restarted successfully."}


class StopServiceCommand(ServiceCommandBase):
    """Stops a specified Windows service."""
    async def execute(self) -> dict:
        service_name = self._validate_service_name(self.parameters.get("service_name"))
        
        if not await self._check_service_exists(service_name):
            raise ValueError(f"Service '{service_name}' does not exist.")
            
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                ["sc.exe", "stop", service_name],
                capture_output=True,
                text=True
            )
        )
        
        if result.returncode != 0 and "1062" not in result.stdout:
            # 1062 is ERROR_SERVICE_NOT_ACTIVE, which is functionally a success for a stop command
            raise RuntimeError(f"Failed to stop service: {result.stderr.strip() or result.stdout.strip()}")
            
        return {"message": f"Service '{service_name}' stopped successfully."}


class GetServicesCommand(BaseCommandExecutor):
    """Retrieves a list of Windows services (ad-hoc)."""
    async def execute(self) -> dict:
        from collectors.services import collect_services
        
        loop = asyncio.get_running_loop()
        inventory_request = await loop.run_in_executor(None, collect_services)
        
        return {"services": [s.model_dump(mode="json") for s in inventory_request.services]}
