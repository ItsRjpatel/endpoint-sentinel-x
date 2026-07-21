from typing import Type
from shared.constants.ws_events import CommandType
from commands.base import BaseCommandExecutor

# We will import the actual executors here, mapping them to the CommandType enums.
from commands.system import PingCommand, RestartAgentCommand, CollectLogsCommand
from commands.service import RestartServiceCommand, StopServiceCommand, GetServicesCommand
from commands.inventory import CollectInventoryCommand
from commands.process import GetProcessesCommand

_COMMAND_REGISTRY: dict[str, Type[BaseCommandExecutor]] = {
    CommandType.PING.value: PingCommand,
    CommandType.RESTART_AGENT.value: RestartAgentCommand,
    CommandType.RESTART_SERVICE.value: RestartServiceCommand,
    CommandType.STOP_SERVICE.value: StopServiceCommand,
    CommandType.GET_SERVICES.value: GetServicesCommand,
    CommandType.COLLECT_INVENTORY.value: CollectInventoryCommand,
    CommandType.GET_PROCESSES.value: GetProcessesCommand,
    CommandType.COLLECT_LOGS.value: CollectLogsCommand,
}


def get_command_executor(command_type: str) -> Type[BaseCommandExecutor] | None:
    """Returns the executor class for a given command type string, or None if not registered."""
    return _COMMAND_REGISTRY.get(command_type)
