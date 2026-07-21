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


class DefenderInventory(BaseModel):
    installed: bool = False
    enabled: bool = False
    real_time_protection: bool = False
    antivirus_signature_version: str | None = None
    engine_version: str | None = None
    last_signature_update: datetime | None = None
    last_quick_scan: datetime | None = None
    last_full_scan: datetime | None = None
    antivirus_enabled: bool | None = None
    antispyware_enabled: bool | None = None
    nis_enabled: bool | None = None
    ioav_protection: bool | None = None
    behavior_monitoring: bool | None = None
    tamper_protection: bool | None = None


class TPMInventory(BaseModel):
    present: bool = False
    ready: bool = False
    enabled: bool = False
    activated: bool = False
    manufacturer: str | None = None
    manufacturer_version: str | None = None
    specification_version: str | None = None
    managed_authentication_level: str | None = None


class SecureBootInventory(BaseModel):
    supported: bool = False
    enabled: bool = False


class UACInventory(BaseModel):
    enabled: bool = False
    consent_prompt_behavior: str | None = None


class SecurityCenterInventory(BaseModel):
    status: str | None = None
    registered_antivirus: str | None = None
    registered_firewall: str | None = None
    registered_antispyware: str | None = None
    product_state: int | None = None


class BitLockerVolumeInventory(BaseModel):
    drive_letter: str
    volume_type: str | None = None
    protection_status: str | None = None
    encryption_percentage: float | None = None
    encryption_method: str | None = None
    lock_status: str | None = None
    auto_unlock: bool | None = None
    key_protector_count: int | None = None


class FirewallProfileInventory(BaseModel):
    profile_name: str
    enabled: bool = False
    default_inbound_policy: str | None = None
    default_outbound_policy: str | None = None


class SecurityInventory(BaseModel):
    defender: DefenderInventory | None = None
    tpm: TPMInventory | None = None
    secure_boot: SecureBootInventory | None = None
    uac: UACInventory | None = None
    security_center: SecurityCenterInventory | None = None
    bitlocker_volumes: list[BitLockerVolumeInventory] = Field(default_factory=list)
    firewall_profiles: list[FirewallProfileInventory] = Field(default_factory=list)


class SecurityInventoryRequest(InventoryMeta):
    security: SecurityInventory
