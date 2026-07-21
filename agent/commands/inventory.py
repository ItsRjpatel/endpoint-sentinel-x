import asyncio
from commands.base import BaseCommandExecutor

class CollectInventoryCommand(BaseCommandExecutor):
    """
    Forces an immediate collection and REST upload of a specific inventory category.
    Does not use the WebSocket for the payload, preserving the REST architecture.
    """
    async def execute(self) -> dict:
        category = self.parameters.get("category", "all")
        
        # We run the REST sync functions in a thread to not block the WS loop
        import inventory_sync
        loop = asyncio.get_running_loop()
        
        sync_map = {
            "hardware": inventory_sync.sync_hardware,
            "os": inventory_sync.sync_os,
            "security": inventory_sync.sync_security,
            "network": inventory_sync.sync_network,
            "storage": inventory_sync.sync_storage,
            "software": inventory_sync.sync_software,
            "updates": inventory_sync.sync_windows_updates,
            "services": inventory_sync.sync_services,
            "local_users": inventory_sync.sync_local_users,
        }
        
        if category == "all":
            for func in sync_map.values():
                await loop.run_in_executor(None, func)
        elif category in sync_map:
            await loop.run_in_executor(None, sync_map[category])
        else:
            raise ValueError(f"Unknown inventory category: {category}")
            
        return {"message": f"Inventory sync for '{category}' triggered successfully."}
