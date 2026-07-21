"""
Inventory data models for the Endpoint Sentinel X Windows Agent.

These Pydantic models mirror the backend HardwarePayload / HardwareInventoryRequest
schemas so that validation happens on the agent before any bytes leave the host.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class HardwareInventory(BaseModel):
    """
    Strongly-typed model for hardware inventory data collected from the host.

    Fields that cannot be read (WMI unavailable, missing permissions, etc.)
    are represented as ``None`` rather than raising.  The required backend
    fields ``cpu_model``, ``cpu_cores``, ``cpu_threads``, and
    ``total_ram_bytes`` fall back to sentinel values so the payload remains
    schema-valid even when partial data is collected.
    """

    # CPU — always required by the backend schema
    cpu_model: str = Field(default="Unknown", description="Processor brand/model string.")
    cpu_cores: int = Field(default=0, ge=0, description="Physical CPU core count.")
    cpu_threads: int = Field(default=0, ge=0, description="Logical CPU thread count.")

    # RAM — always required by the backend schema
    total_ram_bytes: int = Field(default=0, ge=0, description="Total installed RAM in bytes.")

    # System identity — optional in the backend schema
    system_manufacturer: str | None = Field(
        default=None, description="OEM manufacturer name from CIM (e.g. 'Dell Inc.')."
    )
    system_model: str | None = Field(
        default=None, description="System product name from CIM (e.g. 'Latitude 7420')."
    )
    bios_version: str | None = Field(default=None, description="BIOS/UEFI version string from CIM.")


class InventoryMeta(BaseModel):
    """Metadata injected into every inventory upload request."""

    collected_at: datetime = Field(description="UTC timestamp when collection completed.")
    agent_version: str = Field(description="Semver string of the agent that collected the data.")
    inventory_hash: str = Field(description="SHA-256 hex digest of the canonical payload JSON.")


class HardwareInventoryRequest(InventoryMeta):
    """
    Full request body sent to ``POST /api/v1/inventory/hardware``.

    Matches the backend ``HardwareInventoryRequest`` schema exactly so that
    Pydantic serialisation on the agent side produces a wire-compatible JSON body.
    """

    hardware: HardwareInventory
