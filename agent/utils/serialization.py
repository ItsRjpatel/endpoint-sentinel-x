"""
Serialization helpers for inventory payloads.

Converts Pydantic inventory models to JSON-safe primitive types suitable for
hashing and HTTP transmission.  Serialization must produce deterministic output
so that the SHA-256 hash remains stable between runs when data is unchanged.
"""

import structlog

from models.inventory import HardwareInventory

logger = structlog.get_logger(__name__)


def serialize_hardware(inventory: HardwareInventory) -> dict:
    """
    Convert a :class:`HardwareInventory` to a JSON-serializable ``dict``.

    The output contains only built-in Python types (``str``, ``int``,
    ``None``), which means ``json.dumps`` can encode it without a custom
    ``default`` hook.  Producing JSON-safe primitives here — rather than
    relying on ``default=str`` inside the hasher — ensures that any
    type mismatch surfaces early and deterministically.

    Parameters
    ----------
    inventory:
        Validated :class:`HardwareInventory` instance returned by the collector.

    Returns
    -------
    dict
        A plain dictionary ready for JSON encoding and hashing.
    """
    return {
        "cpu_model": inventory.cpu_model,
        "cpu_cores": inventory.cpu_cores,
        "cpu_threads": inventory.cpu_threads,
        "total_ram_bytes": inventory.total_ram_bytes,
        "system_manufacturer": inventory.system_manufacturer,
        "system_model": inventory.system_model,
        "bios_version": inventory.bios_version,
    }
