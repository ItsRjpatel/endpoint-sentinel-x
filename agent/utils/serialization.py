"""
Serialization helpers for inventory payloads.

Converts Pydantic inventory models to JSON-safe primitive types suitable for
hashing and HTTP transmission.  Serialization must produce deterministic output
so that the SHA-256 hash remains stable between runs when data is unchanged.
"""

import structlog

from models.inventory import (
    HardwareInventory,
    OperatingSystemInventory,
    SecurityInventory,
    SoftwareInventoryRequest,
    StorageInventoryRequest,
)

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


def serialize_os(inventory: OperatingSystemInventory) -> dict:
    """
    Convert an :class:`OperatingSystemInventory` to a JSON-serializable ``dict``.

    Parameters
    ----------
    inventory:
        Validated :class:`OperatingSystemInventory` instance returned by the collector.

    Returns
    -------
    dict
        A plain dictionary ready for JSON encoding and hashing.
    """
    return {
        "name": inventory.name,
        "edition": inventory.edition,
        "version": inventory.version,
        "build_number": inventory.build_number,
        "display_version": inventory.display_version,
        "architecture": inventory.architecture,
        # Convert datetime to ISO string if present
        "install_date": inventory.install_date.isoformat() if inventory.install_date else None,
        "last_boot_time": inventory.last_boot_time.isoformat()
        if inventory.last_boot_time
        else None,
        "system_uptime_seconds": inventory.system_uptime_seconds,
        "computer_name": inventory.computer_name,
        "domain": inventory.domain,
        "registered_owner": inventory.registered_owner,
        "time_zone": inventory.time_zone,
        "system_locale": inventory.system_locale,
    }


def serialize_security(inventory: "SecurityInventory") -> dict:
    """
    Convert a :class:`SecurityInventory` to a JSON-serializable ``dict``.

    Parameters
    ----------
    inventory:
        Validated :class:`SecurityInventory` instance returned by the collector.

    Returns
    -------
    dict
        A plain dictionary ready for JSON encoding and hashing.
    """

    def _format_date(dt):
        return dt.isoformat() if dt else None

    payload = {
        "defender": None,
        "tpm": None,
        "secure_boot": None,
        "uac": None,
        "security_center": None,
        "bitlocker_volumes": [],
        "firewall_profiles": [],
    }

    if inventory.defender:
        payload["defender"] = {
            "installed": inventory.defender.installed,
            "enabled": inventory.defender.enabled,
            "real_time_protection": inventory.defender.real_time_protection,
            "antivirus_signature_version": inventory.defender.antivirus_signature_version,
            "engine_version": inventory.defender.engine_version,
            "last_signature_update": _format_date(inventory.defender.last_signature_update),
            "last_quick_scan": _format_date(inventory.defender.last_quick_scan),
            "last_full_scan": _format_date(inventory.defender.last_full_scan),
            "antivirus_enabled": inventory.defender.antivirus_enabled,
            "antispyware_enabled": inventory.defender.antispyware_enabled,
            "nis_enabled": inventory.defender.nis_enabled,
            "ioav_protection": inventory.defender.ioav_protection,
            "behavior_monitoring": inventory.defender.behavior_monitoring,
            "tamper_protection": inventory.defender.tamper_protection,
        }

    if inventory.tpm:
        payload["tpm"] = {
            "present": inventory.tpm.present,
            "ready": inventory.tpm.ready,
            "enabled": inventory.tpm.enabled,
            "activated": inventory.tpm.activated,
            "manufacturer": inventory.tpm.manufacturer,
            "manufacturer_version": inventory.tpm.manufacturer_version,
            "specification_version": inventory.tpm.specification_version,
            "managed_authentication_level": inventory.tpm.managed_authentication_level,
        }

    if inventory.secure_boot:
        payload["secure_boot"] = {
            "supported": inventory.secure_boot.supported,
            "enabled": inventory.secure_boot.enabled,
        }

    if inventory.uac:
        payload["uac"] = {
            "enabled": inventory.uac.enabled,
            "consent_prompt_behavior": inventory.uac.consent_prompt_behavior,
        }

    if inventory.security_center:
        payload["security_center"] = {
            "status": inventory.security_center.status,
            "registered_antivirus": inventory.security_center.registered_antivirus,
            "registered_firewall": inventory.security_center.registered_firewall,
            "registered_antispyware": inventory.security_center.registered_antispyware,
            "product_state": inventory.security_center.product_state,
        }

    payload["bitlocker_volumes"] = [
        {
            "drive_letter": v.drive_letter,
            "volume_type": v.volume_type,
            "protection_status": v.protection_status,
            "encryption_percentage": v.encryption_percentage,
            "encryption_method": v.encryption_method,
            "lock_status": v.lock_status,
            "auto_unlock": v.auto_unlock,
            "key_protector_count": v.key_protector_count,
        }
        for v in inventory.bitlocker_volumes
    ]

    payload["firewall_profiles"] = [
        {
            "profile_name": p.profile_name,
            "enabled": p.enabled,
            "default_inbound_policy": p.default_inbound_policy,
            "default_outbound_policy": p.default_outbound_policy,
        }
        for p in inventory.firewall_profiles
    ]

    return payload


def serialize_network(identity_payload, adapters_payload) -> dict:
    """
    Convert network inventory to a JSON-serializable ``dict``.

    Parameters
    ----------
    identity_payload: NetworkIdentityPayload
    adapters_payload: list[AdapterPayload]

    Returns
    -------
    dict
    """

    def _format_date(dt):
        return dt.isoformat() if dt else None

    payload = {
        "identity": {
            "fqdn": identity_payload.fqdn,
            "domain_workgroup": identity_payload.domain_workgroup,
            "primary_dns_suffix": identity_payload.primary_dns_suffix,
        },
        "adapters": [],
    }

    # Sort adapters by name for deterministic hashing
    sorted_adapters = sorted(adapters_payload, key=lambda a: a.name)

    for adapter in sorted_adapters:
        adapter_dict = {
            "name": adapter.name,
            "friendly_name": adapter.friendly_name,
            "description": adapter.description,
            "interface_type": adapter.interface_type,
            "adapter_type": adapter.adapter_type,
            "manufacturer": adapter.manufacturer,
            "mac_address": adapter.mac_address,
            "is_physical": adapter.is_physical,
            "is_virtual": adapter.is_virtual,
            "status": adapter.status,
            "admin_status": adapter.admin_status,
            "link_speed_bps": adapter.link_speed_bps,
            "mtu": adapter.mtu,
            "driver_version": adapter.driver_version,
            "driver_date": _format_date(adapter.driver_date),
            "interface_index": adapter.interface_index,
            "interface_guid": adapter.interface_guid,
            "dhcp_enabled": adapter.dhcp_enabled,
            "dhcp_server": adapter.dhcp_server,
            "dhcp_lease_obtained": _format_date(adapter.dhcp_lease_obtained),
            "dhcp_lease_expires": _format_date(adapter.dhcp_lease_expires),
            # Sort simple lists
            "default_gateways": sorted(adapter.default_gateways),
            "dns_servers": sorted(adapter.dns_servers),
            "dns_search_suffixes": sorted(adapter.dns_search_suffixes),
            "addresses": [],
            "wifi": None,
            "vpn": None,
        }

        sorted_addresses = sorted(adapter.addresses, key=lambda addr: addr.address)
        for addr in sorted_addresses:
            adapter_dict["addresses"].append(
                {
                    "address": addr.address,
                    "family": addr.family,
                    "prefix_length": addr.prefix_length,
                    "subnet_mask": addr.subnet_mask,
                    "is_loopback": addr.is_loopback,
                }
            )

        if adapter.wifi:
            adapter_dict["wifi"] = {
                "ssid": adapter.wifi.ssid,
                "bssid": adapter.wifi.bssid,
                "signal_strength": adapter.wifi.signal_strength,
                "auth_type": adapter.wifi.auth_type,
                "radio_type": adapter.wifi.radio_type,
                "channel": adapter.wifi.channel,
                "frequency_mhz": adapter.wifi.frequency_mhz,
            }

        if adapter.vpn:
            adapter_dict["vpn"] = {
                "connection_status": adapter.vpn.connection_status,
                "tunnel_type": adapter.vpn.tunnel_type,
            }

        payload["adapters"].append(adapter_dict)

    return payload


def serialize_storage(inventory: "StorageInventoryRequest") -> dict:
    """
    Convert storage inventory to a JSON-serializable ``dict``.
    """
    payload = {
        "disks": [],
        "volumes": [],
        "storage_pools": [],
    }

    # Sort disks by device name
    sorted_disks = sorted(inventory.disks, key=lambda d: str(d.device_name))
    for disk in sorted_disks:
        disk_dict = {
            "device_name": disk.device_name,
            "friendly_name": disk.friendly_name,
            "manufacturer": disk.manufacturer,
            "model": disk.model,
            "serial_number": disk.serial_number,
            "firmware_version": disk.firmware_version,
            "interface_type": disk.interface_type,
            "bus_type": disk.bus_type,
            "media_type": disk.media_type,
            "health_status": disk.health_status,
            "operational_status": disk.operational_status,
            "size_bytes": disk.size_bytes,
            "logical_sector_size": disk.logical_sector_size,
            "physical_sector_size": disk.physical_sector_size,
            "rotation_rate": disk.rotation_rate,
            "is_removable": disk.is_removable,
            "is_boot_disk": disk.is_boot_disk,
            "is_system_disk": disk.is_system_disk,
            "unique_id": disk.unique_id,
            "location": disk.location,
            "partition_style": disk.partition_style,
            "is_offline": disk.is_offline,
            "is_read_only": disk.is_read_only,
            "can_pool": disk.can_pool,
            "smart": None,
            "partitions": [],
        }

        if disk.smart:
            disk_dict["smart"] = {
                "predict_failure": disk.smart.predict_failure,
                "temperature": disk.smart.temperature,
                "wear_level": disk.smart.wear_level,
                "remaining_life": disk.smart.remaining_life,
                "reallocated_sector_count": disk.smart.reallocated_sector_count,
            }

        sorted_parts = sorted(disk.partitions, key=lambda p: p.partition_number or 0)
        for part in sorted_parts:
            disk_dict["partitions"].append(
                {
                    "partition_number": part.partition_number,
                    "partition_style": part.partition_style,
                    "partition_type": part.partition_type,
                    "size_bytes": part.size_bytes,
                    "offset_bytes": part.offset_bytes,
                    "drive_letter": part.drive_letter,
                    "is_boot": part.is_boot,
                    "is_active": part.is_active,
                    "is_hidden": part.is_hidden,
                    "is_read_only": part.is_read_only,
                    "volume_id_ref": part.volume_id_ref,
                }
            )

        payload["disks"].append(disk_dict)

    # Sort volumes by volume_id_ref or drive letter
    sorted_volumes = sorted(
        inventory.volumes, key=lambda v: str(v.volume_id_ref or v.drive_letter or "")
    )
    for vol in sorted_volumes:
        vol_dict = {
            "volume_id_ref": vol.volume_id_ref,
            "drive_letter": vol.drive_letter,
            "volume_name": vol.volume_name,
            "file_system": vol.file_system,
            "file_system_label": vol.file_system_label,
            "file_system_version": vol.file_system_version,
            "allocation_unit_size": vol.allocation_unit_size,
            "total_size": vol.total_size,
            "free_space": vol.free_space,
            "used_space": vol.used_space,
            "percentage_used": vol.percentage_used,
            "percentage_free": vol.percentage_free,
            "health_status": vol.health_status,
            "compression_enabled": vol.compression_enabled,
            "deduplication_enabled": vol.deduplication_enabled,
            "shadow_copies_enabled": vol.shadow_copies_enabled,
            "mounts": [],
        }

        sorted_mounts = sorted(vol.mounts, key=lambda m: str(m.mount_path))
        for m in sorted_mounts:
            vol_dict["mounts"].append({"mount_path": m.mount_path})

        payload["volumes"].append(vol_dict)

    # Sort pools by pool_name
    sorted_pools = sorted(inventory.storage_pools, key=lambda p: str(p.pool_name))
    for pool in sorted_pools:
        pool_dict = {
            "pool_name": pool.pool_name,
            "health_status": pool.health_status,
            "operational_status": pool.operational_status,
            "total_capacity": pool.total_capacity,
            "free_capacity": pool.free_capacity,
            "virtual_disks": [],
        }

        sorted_vds = sorted(pool.virtual_disks, key=lambda vd: str(vd.virtual_disk_name))
        for vd in sorted_vds:
            pool_dict["virtual_disks"].append(
                {
                    "virtual_disk_name": vd.virtual_disk_name,
                    "resiliency_type": vd.resiliency_type,
                    "provisioning_type": vd.provisioning_type,
                    "health_status": vd.health_status,
                    "operational_status": vd.operational_status,
                    "size_bytes": vd.size_bytes,
                }
            )

        payload["storage_pools"].append(pool_dict)

    return payload


def serialize_software(inventory: "SoftwareInventoryRequest") -> dict:
    """
    Convert a :class:`SoftwareInventoryRequest` to a JSON-serializable ``dict``.

    The software items are sorted by Publisher, Display Name, Version, Architecture, Install Scope
    with strings converted to lowercase for deterministic serialization.
    """
    payload = {"software": []}

    def _sort_key(s):
        pub = str(s.publisher or "").strip().lower()
        name = str(s.name or "").strip().lower()
        ver = str(s.version or "").strip().lower()
        arch = str(s.architecture or "").strip().lower()
        scope = str(s.install_scope or "").strip().lower()
        return (pub, name, ver, arch, scope)

    sorted_software = sorted(inventory.software, key=_sort_key)
    for s in sorted_software:
        payload["software"].append(
            {
                "name": s.name,
                "version": s.version,
                "publisher": s.publisher,
                "install_date": s.install_date,
                "install_location": s.install_location,
                "install_source": s.install_source,
                "estimated_size_bytes": s.estimated_size_bytes,
                "uninstall_string": s.uninstall_string,
                "quiet_uninstall_string": s.quiet_uninstall_string,
                "install_scope": s.install_scope,
                "architecture": s.architecture,
                "product_code": s.product_code,
                "help_link": s.help_link,
                "url_info_about": s.url_info_about,
                "url_update_info": s.url_update_info,
                "display_icon": s.display_icon,
                "language": s.language,
                "release_type": s.release_type,
                "parent_application": s.parent_application,
                "parent_version": s.parent_version,
                "system_component": s.system_component,
                "windows_installer": s.windows_installer,
                "no_remove": s.no_remove,
                "no_modify": s.no_modify,
                "no_repair": s.no_repair,
                "classification": s.classification,
            }
        )

    return payload
