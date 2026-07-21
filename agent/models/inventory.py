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


class OperatingSystemInventory(BaseModel):
    """Strongly-typed model for OS inventory data collected from the host."""

    name: str = Field(
        default="Unknown", description="Operating System Name (e.g., Microsoft Windows 11 Pro)"
    )
    edition: str | None = Field(default=None, description="OS Edition")
    version: str = Field(default="Unknown", description="OS Version string")
    build_number: str | None = Field(default=None, description="OS Build Number")
    display_version: str | None = Field(
        default=None, description="Display Version (e.g., 22H2, 23H2)"
    )
    architecture: str = Field(default="Unknown", description="OS Architecture (e.g., 64-bit)")
    install_date: datetime | None = Field(default=None, description="Installation Date")
    last_boot_time: datetime | None = Field(default=None, description="Last Boot Time")
    system_uptime_seconds: int | None = Field(
        default=None, ge=0, description="System Uptime in seconds"
    )
    computer_name: str | None = Field(default=None, description="Computer Name")
    domain: str | None = Field(default=None, description="Domain or Workgroup")
    registered_owner: str | None = Field(default=None, description="Registered Owner")
    time_zone: str | None = Field(default=None, description="Time Zone Caption")
    system_locale: str | None = Field(default=None, description="System Locale / Language")


class OSInventoryRequest(InventoryMeta):
    """Full request body sent to ``POST /api/v1/inventory/operating-system``."""

    os: OperatingSystemInventory
