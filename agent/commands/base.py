from abc import ABC, abstractmethod
import structlog

logger = structlog.get_logger(__name__)


class BaseCommandExecutor(ABC):
    """
    Abstract base class for all hardcoded remote commands.
    Ensures a uniform signature for execution.
    """

    def __init__(self, payload: dict):
        self.payload = payload
        self.command_id = payload.get("id")
        self.parameters = payload.get("parameters") or {}

    @abstractmethod
    async def execute(self) -> dict | None:
        """
        Executes the command logic.
        Should return a JSON-serializable dictionary on success, 
        or None if no specific data needs returning.
        Must raise an Exception on failure.
        """
        pass
