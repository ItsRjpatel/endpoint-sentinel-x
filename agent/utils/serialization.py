"""
Serialization helpers for inventory payloads.

Converts Pydantic inventory models to JSON-safe primitive types suitable for
hashing and HTTP transmission.  Serialization must produce deterministic output
so that the SHA-256 hash remains stable between runs when data is unchanged.
"""

import structlog

from models.inventory import HardwareInventory, OperatingSystemInventory, SecurityInventory

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
