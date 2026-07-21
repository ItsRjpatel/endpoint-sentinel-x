from datetime import date, datetime

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
    edition: str | None = None
    version: str
    build_number: str | None = None
    display_version: str | None = None
    architecture: str
    install_date: datetime | None = None
    last_boot_time: datetime | None = None
    system_uptime_seconds: int | None = None
    computer_name: str | None = None
    domain: str | None = None
    registered_owner: str | None = None
    time_zone: str | None = None
    system_locale: str | None = None


class OSInventoryRequest(InventoryMeta):
    os: OSPayload


# ---------------------------------------------------------------------------
# Security Status
# ---------------------------------------------------------------------------


class DefenderPayload(BaseModel):
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


class TPMPayload(BaseModel):
    present: bool = False
    ready: bool = False
    enabled: bool = False
    activated: bool = False
    manufacturer: str | None = None
    manufacturer_version: str | None = None
    specification_version: str | None = None
    managed_authentication_level: str | None = None


class SecureBootPayload(BaseModel):
    supported: bool = False
    enabled: bool = False


class UACPayload(BaseModel):
    enabled: bool = False
    consent_prompt_behavior: str | None = None


class SecurityCenterPayload(BaseModel):
    status: str | None = None
    registered_antivirus: str | None = None
    registered_firewall: str | None = None
    registered_antispyware: str | None = None
    product_state: int | None = None


class BitLockerVolumePayload(BaseModel):
    drive_letter: str
    volume_type: str | None = None
    protection_status: str | None = None
    encryption_percentage: float | None = None
    encryption_method: str | None = None
    lock_status: str | None = None
    auto_unlock: bool | None = None
    key_protector_count: int | None = None


class FirewallProfilePayload(BaseModel):
    profile_name: str
    enabled: bool = False
    default_inbound_policy: str | None = None
    default_outbound_policy: str | None = None


class SecurityPayload(BaseModel):
    defender: DefenderPayload | None = None
    tpm: TPMPayload | None = None
    secure_boot: SecureBootPayload | None = None
    uac: UACPayload | None = None
    security_center: SecurityCenterPayload | None = None
    bitlocker_volumes: list[BitLockerVolumePayload] = Field(default_factory=list)
    firewall_profiles: list[FirewallProfilePayload] = Field(default_factory=list)


class SecurityInventoryRequest(InventoryMeta):
    security: SecurityPayload


# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------


class NetworkIdentityPayload(BaseModel):
    fqdn: str | None = None
    domain_workgroup: str | None = None
    primary_dns_suffix: str | None = None


class NetworkAddressPayload(BaseModel):
    address: str
    family: str = Field(..., description="'ipv4' or 'ipv6'")
    prefix_length: int | None = None
    subnet_mask: str | None = None
    is_loopback: bool = False


class WifiPayload(BaseModel):
    ssid: str | None = None
    bssid: str | None = None
    signal_strength: int | None = None
    auth_type: str | None = None
    radio_type: str | None = None
    channel: int | None = None
    frequency_mhz: int | None = None


class VpnPayload(BaseModel):
    connection_status: str | None = None
    tunnel_type: str | None = None


class NetworkAdapterPayload(BaseModel):
    name: str
    friendly_name: str | None = None
    description: str | None = None
    interface_type: str | None = None
    adapter_type: str | None = None
    manufacturer: str | None = None
    mac_address: str | None = None
    is_physical: bool = True
    is_virtual: bool = False
    status: str | None = None
    admin_status: str | None = None
    link_speed_bps: int | None = None
    mtu: int | None = None
    driver_version: str | None = None
    driver_date: date | None = None
    interface_index: int | None = None
    interface_guid: str | None = None
    dhcp_enabled: bool | None = None
    dhcp_server: str | None = None
    dhcp_lease_obtained: datetime | None = None
    dhcp_lease_expires: datetime | None = None
    default_gateways: list[str] = Field(default_factory=list)
    dns_servers: list[str] = Field(default_factory=list)
    dns_search_suffixes: list[str] = Field(default_factory=list)

    addresses: list[NetworkAddressPayload] = Field(default_factory=list)
    wifi: WifiPayload | None = None
    vpn: VpnPayload | None = None


class NetworkInventoryRequest(InventoryMeta):
    identity: NetworkIdentityPayload
    adapters: list[NetworkAdapterPayload] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------


class SmartPayload(BaseModel):
    predict_failure: bool | None = None
    temperature: int | None = None
    wear_level: int | None = None
    remaining_life: int | None = None
    reallocated_sector_count: int | None = None


class PartitionPayload(BaseModel):
    partition_number: int | None = None
    partition_style: str | None = None
    partition_type: str | None = None
    size_bytes: int | None = None
    offset_bytes: int | None = None
    drive_letter: str | None = None
    is_boot: bool | None = None
    is_active: bool | None = None
    is_hidden: bool | None = None
    is_read_only: bool | None = None
    volume_id_ref: str | None = None


class DiskPayload(BaseModel):
    device_name: str | None = None
    friendly_name: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    firmware_version: str | None = None
    interface_type: str | None = None
    bus_type: str | None = None
    media_type: str | None = None
    health_status: str | None = None
    operational_status: str | None = None
    size_bytes: int | None = None
    logical_sector_size: int | None = None
    physical_sector_size: int | None = None
    rotation_rate: int | None = None
    is_removable: bool | None = None
    is_boot_disk: bool | None = None
    is_system_disk: bool | None = None
    unique_id: str | None = None
    location: str | None = None
    partition_style: str | None = None
    is_offline: bool | None = None
    is_read_only: bool | None = None
    can_pool: bool | None = None
    smart: SmartPayload | None = None
    partitions: list[PartitionPayload] = Field(default_factory=list)


class VolumeMountPayload(BaseModel):
    mount_path: str


class VolumePayload(BaseModel):
    volume_id_ref: str | None = None
    drive_letter: str | None = None
    volume_name: str | None = None
    file_system: str | None = None
    file_system_label: str | None = None
    file_system_version: str | None = None
    allocation_unit_size: int | None = None
    total_size: int | None = None
    free_space: int | None = None
    used_space: int | None = None
    percentage_used: float | None = None
    percentage_free: float | None = None
    health_status: str | None = None
    compression_enabled: bool | None = None
    deduplication_enabled: bool | None = None
    shadow_copies_enabled: bool | None = None
    mounts: list[VolumeMountPayload] = Field(default_factory=list)


class VirtualDiskPayload(BaseModel):
    virtual_disk_name: str
    resiliency_type: str | None = None
    provisioning_type: str | None = None
    health_status: str | None = None
    operational_status: str | None = None
    size_bytes: int | None = None


class StoragePoolPayload(BaseModel):
    pool_name: str
    health_status: str | None = None
    operational_status: str | None = None
    total_capacity: int | None = None
    free_capacity: int | None = None
    virtual_disks: list[VirtualDiskPayload] = Field(default_factory=list)


class StorageInventoryRequest(InventoryMeta):
    disks: list[DiskPayload] = Field(default_factory=list)
    volumes: list[VolumePayload] = Field(default_factory=list)
    storage_pools: list[StoragePoolPayload] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Software
# ---------------------------------------------------------------------------


class SoftwarePayload(BaseModel):
    name: str
    version: str | None = None
    publisher: str | None = None
    install_date: str | None = None
    install_location: str | None = None
    install_source: str | None = None
    estimated_size_bytes: int | None = None
    uninstall_string: str | None = None
    quiet_uninstall_string: str | None = None
    install_scope: str | None = None
    architecture: str | None = None
    product_code: str | None = None
    help_link: str | None = None
    url_info_about: str | None = None
    url_update_info: str | None = None
    display_icon: str | None = None
    language: str | None = None
    release_type: str | None = None
    parent_application: str | None = None
    parent_version: str | None = None
    system_component: bool = False
    windows_installer: bool = False
    no_remove: bool = False
    no_modify: bool = False
    no_repair: bool = False
    classification: str | None = None


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
