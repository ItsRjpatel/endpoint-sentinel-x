"""
WebSocket Event Envelopes and Constants.

This file defines the strict event types supported over the WebSocket transport.
Shared between the FastAPI backend and the Python Agent.
"""

from enum import Enum


class WSEventType(str, Enum):
    """Core WebSocket envelope event types."""
    AUTH = "AUTH"
    AUTH_OK = "AUTH_OK"
    AUTH_FAILED = "AUTH_FAILED"
    PING = "PING"
    PONG = "PONG"
    HEARTBEAT = "HEARTBEAT"
    CMD_REQUEST = "CMD_REQUEST"
    CMD_ACK = "CMD_ACK"
    CMD_RESULT = "CMD_RESULT"
    STATUS = "STATUS"
    ALERT = "ALERT"
    NOTIFICATION = "NOTIFICATION"
    POLICY_CHANGED = "POLICY_CHANGED"
    INVENTORY_CHANGED = "INVENTORY_CHANGED"
    ERROR = "ERROR"
    DISCONNECT = "DISCONNECT"


class CommandType(str, Enum):
    """Supported hardcoded commands for Sprint 4."""
    PING = "Ping"
    RESTART_AGENT = "Restart Agent"
    RESTART_SERVICE = "Restart Service"
    STOP_SERVICE = "Stop Service"
    COLLECT_INVENTORY = "Collect Inventory"
    COLLECT_LOGS = "Collect Logs"
    GET_SERVICES = "Get Services"
    GET_PROCESSES = "Get Processes"


class CommandStatus(str, Enum):
    """Lifecycle statuses for a command."""
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    SENT = "SENT"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
