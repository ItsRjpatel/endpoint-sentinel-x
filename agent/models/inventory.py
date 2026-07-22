"""
Inventory data models for the Endpoint Sentinel X Windows Agent.

These Pydantic models mirror the backend HardwarePayload / HardwareInventoryRequest
schemas so that validation happens on the agent before any bytes leave the host.
"""

from datetime import date, datetime

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
    exploit_protection: bool | None = None
    controlled_folder_access: bool | None = None
    boot_protection: bool | None = None


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


class NetworkIdentityPayload(BaseModel):
    fqdn: str | None = None
    domain_workgroup: str | None = None
    primary_dns_suffix: str | None = None


class AddressPayload(BaseModel):
    address: str
    family: str
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


class AdapterPayload(BaseModel):
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

    addresses: list[AddressPayload] = Field(default_factory=list)
    wifi: WifiPayload | None = None
    vpn: VpnPayload | None = None


class NetworkInventoryRequest(InventoryMeta):
    identity: NetworkIdentityPayload
    adapters: list[AdapterPayload]


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
    software: list[SoftwarePayload]


class WindowsUpdatePayload(BaseModel):
    hotfix_id: str | None = None
    title: str | None = None
    description: str | None = None
    classification: str | None = None
    installed_by: str | None = None
    installed_on: datetime | None = None
    installation_state: str | None = None
    support_url: str | None = None
    update_id: str | None = None
    revision_number: int | None = None
    deployment_source: str | None = None
    package_identity: str | None = None
    is_security_update: bool = False
    is_critical_update: bool = False
    is_cumulative_update: bool = False
    is_driver_update: bool = False
    is_feature_update: bool = False
    is_preview_update: bool = False
    is_servicing_stack_update: bool = False


class WindowsUpdatesInventoryRequest(InventoryMeta):
    updates: list[WindowsUpdatePayload] = Field(default_factory=list)


class ServicePayload(BaseModel):
    name: str
    display_name: str | None = None
    description: str | None = None
    status: str | None = None
    startup_type: str | None = None
    service_type: str | None = None
    binary_path: str | None = None
    service_account: str | None = None
    delayed_auto_start: bool | None = None
    process_id: int | None = None
    dependencies: list[str] | None = None
    dependent_services: list[str] | None = None
    accept_stop: bool | None = None
    accept_pause: bool | None = None
    can_shutdown: bool | None = None
    exit_code: int | None = None
    service_flags: int | None = None
    error_control: str | None = None
    load_order_group: str | None = None
    tag_id: int | None = None
    trigger_start: bool | None = None


class ServicesInventoryRequest(InventoryMeta):
    services: list[ServicePayload] = Field(default_factory=list)


class LocalUserPayload(BaseModel):
    sid: str
    username: str
    full_name: str | None = None
    description: str | None = None
    account_type: str | None = None
    is_enabled: bool | None = None
    is_locked: bool | None = None
    is_password_required: bool | None = None
    is_password_change_allowed: bool | None = None
    password_expires: bool | None = None
    password_never_expires: bool | None = None
    password_last_set: datetime | None = None
    last_logon: datetime | None = None
    last_logoff: datetime | None = None
    account_created: datetime | None = None
    account_expires: datetime | None = None
    bad_logon_count: int | None = None
    home_directory: str | None = None
    profile_path: str | None = None
    script_path: str | None = None
    primary_group: str | None = None
    local_groups: list[str] = Field(default_factory=list)
    is_builtin_account: bool | None = None
    is_administrator: bool | None = None
    is_guest: bool | None = None


class LocalUsersInventoryRequest(InventoryMeta):
    users: list[LocalUserPayload] = Field(default_factory=list)
