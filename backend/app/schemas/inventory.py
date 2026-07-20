from datetime import datetime

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Shared metadata carrier (injected into every inventory request)
# ---------------------------------------------------------------------------


class InventoryMeta(BaseModel):
    """Common metadata fields sent with every inventory payload."""

    collected_at: datetime = Field(..., description="UTC timestamp of collection on the agent")
    agent_version: str = Field(..., description="Version of the agent that collected this data")
    inventory_hash: str = Field(..., description="SHA-256 hex digest of the sorted payload JSON")


class InventoryResponse(BaseModel):
    """Uniform response returned after processing any inventory category."""

    status: str  # "accepted" | "skipped"
    category: str


# ---------------------------------------------------------------------------
# Hardware
# ---------------------------------------------------------------------------


class HardwarePayload(BaseModel):
    cpu_model: str
    cpu_cores: int
    cpu_threads: int
    total_ram_bytes: int
    system_manufacturer: str | None = None
    system_model: str | None = None
    bios_version: str | None = None


class HardwareInventoryRequest(InventoryMeta):
    hardware: HardwarePayload


# ---------------------------------------------------------------------------
# Operating System
# ---------------------------------------------------------------------------


class OSPayload(BaseModel):
    name: str
    version: str
    build_number: str | None = None
    architecture: str
    install_date: datetime | None = None


class OSInventoryRequest(InventoryMeta):
    os: OSPayload


# ---------------------------------------------------------------------------
# Security Status
# ---------------------------------------------------------------------------


class SecurityPayload(BaseModel):
    antivirus_name: str | None = None
    antivirus_status: str | None = None
    firewall_enabled: bool | None = None
    bitlocker_enabled: bool | None = None
    secure_boot_enabled: bool | None = None


class SecurityInventoryRequest(InventoryMeta):
    security: SecurityPayload


# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------


class NetworkAddressPayload(BaseModel):
    address: str
    family: str = Field(..., description="'ipv4' or 'ipv6'")
    prefix_length: int | None = None
    is_loopback: bool = False


class NetworkAdapterPayload(BaseModel):
    name: str
    mac_address: str | None = None
    is_physical: bool = True
    is_virtual: bool = False
    adapter_type: str | None = None
    status: str | None = None
    addresses: list[NetworkAddressPayload] = Field(default_factory=list)


class NetworkInventoryRequest(InventoryMeta):
    adapters: list[NetworkAdapterPayload] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------


class DiskPayload(BaseModel):
    model: str | None = None
    serial_number: str | None = None
    size_bytes: int | None = None
    interface_type: str | None = None


class VolumePayload(BaseModel):
    drive_letter: str | None = None
    label: str | None = None
    filesystem: str | None = None
    size_bytes: int | None = None
    free_bytes: int | None = None


class StorageInventoryRequest(InventoryMeta):
    disks: list[DiskPayload] = Field(default_factory=list)
    volumes: list[VolumePayload] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Software
# ---------------------------------------------------------------------------


class SoftwarePayload(BaseModel):
    name: str
    version: str | None = None
    publisher: str | None = None
    install_date: str | None = None


class SoftwareInventoryRequest(InventoryMeta):
    software: list[SoftwarePayload] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Windows Updates
# ---------------------------------------------------------------------------


class WindowsUpdatePayload(BaseModel):
    kb_id: str
    title: str | None = None
    install_date: datetime | None = None
    status: str | None = None


class WindowsUpdatesInventoryRequest(InventoryMeta):
    updates: list[WindowsUpdatePayload] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------


class ServicePayload(BaseModel):
    name: str
    display_name: str | None = None
    startup_type: str | None = None
    status: str | None = None


class ServicesInventoryRequest(InventoryMeta):
    services: list[ServicePayload] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Local Users
# ---------------------------------------------------------------------------


class LocalUserPayload(BaseModel):
    username: str
    is_active: bool | None = None
    privilege: str | None = None
    last_login: datetime | None = None


class LocalUsersInventoryRequest(InventoryMeta):
    users: list[LocalUserPayload] = Field(default_factory=list)
