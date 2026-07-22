# ruff: noqa: E501
"""
Network Inventory Collector for Endpoint Sentinel X.

Collects network adapters, IP addresses, DNS, Wi-Fi, VPN, and Identity.
"""

import json
from datetime import datetime, timezone

import structlog

from config.settings import agent_settings
from models.inventory import (
    AdapterPayload,
    AddressPayload,
    NetworkIdentityPayload,
    NetworkInventoryRequest,
    VpnPayload,
    WifiPayload,
)
from utils.hashing import compute_inventory_hash
from utils.powershell import run_powershell
from utils.serialization import serialize_network

logger = structlog.get_logger(__name__)


def collect_network_identity() -> NetworkIdentityPayload:
    """Collects FQDN, Domain/Workgroup, Primary DNS Suffix."""
    script = r"""
    $info = Get-ComputerInfo
    $net = Get-WmiObject Win32_ComputerSystem
    $dns = (Get-ItemProperty "HKLM:\System\CurrentControlSet\Services\TCPIP\Parameters" -Name "NV Domain" -ErrorAction SilentlyContinue)."NV Domain"  # noqa: E501
    if (-not $dns) {
        $dns = (Get-ItemProperty "HKLM:\System\CurrentControlSet\Services\TCPIP\Parameters" -Name "Domain" -ErrorAction SilentlyContinue).Domain  # noqa: E501
    }

    $result = @{
        fqdn = "$($net.Name).$($net.Domain)"
        domain_workgroup = $net.Domain
        primary_dns_suffix = $dns
    }
    # Clean up trailing dot if domain is empty
    if ($result.fqdn -match "\.$") {
        $result.fqdn = $net.Name
    }
    $result | ConvertTo-Json -Depth 2
    """
    try:
        output = run_powershell(script)
        data = json.loads(output)
        return NetworkIdentityPayload(
            fqdn=data.get("fqdn"),
            domain_workgroup=data.get("domain_workgroup"),
            primary_dns_suffix=data.get("primary_dns_suffix"),
        )
    except Exception as e:
        logger.error("Failed to collect network identity", error=str(e))
        return NetworkIdentityPayload()


def collect_adapters() -> list[AdapterPayload]:
    """Collects network adapters and their IP configurations."""
    # This combines Get-NetAdapter, Get-NetIPAddress, and Get-DnsClientServerAddress
    script = r"""
    $adapters = Get-NetAdapter -IncludeHidden | Select-Object Name, InterfaceDescription, InterfaceType, MacAddress, Status, AdminStatus, LinkSpeed, Mtu, DriverVersion, DriverDate, ifIndex, InterfaceGuid, Virtual, MediaType  # noqa: E501
    $ipConfigs = Get-NetIPConfiguration -All -Detailed
    $ipAddresses = Get-NetIPAddress
    $routes = Get-NetRoute -DestinationPrefix "0.0.0.0/0", "::/0" -ErrorAction SilentlyContinue

    $results = @()

    foreach ($adapter in $adapters) {
        $config = $ipConfigs | Where-Object { $_.InterfaceAlias -eq $adapter.Name }
        $addrs = $ipAddresses | Where-Object { $_.InterfaceAlias -eq $adapter.Name }
        $adapterRoutes = $routes | Where-Object { $_.InterfaceAlias -eq $adapter.Name }

        $addresses = @()
        foreach ($a in $addrs) {
            # Map AddressFamily 2 -> IPv4, 23 -> IPv6
            $family = if ($a.AddressFamily -eq 2) { "ipv4" } elseif ($a.AddressFamily -eq 23) { "ipv6" } else { "unknown" }  # noqa: E501
            $addresses += @{
                address = $a.IPAddress
                family = $family
                prefix_length = $a.PrefixLength
                subnet_mask = if ($family -eq "ipv4") {
                    # Approximate subnet mask for IPv4 from prefix length
                    $len = $a.PrefixLength
                    if ($len -ge 0 -and $len -le 32) {
                        $mask = [Math]::Pow(2, $len) - 1
                        $mask = $mask -shl (32 - $len)
                        $bytes = [BitConverter]::GetBytes([uint32]$mask)
                        [Array]::Reverse($bytes)
                        ($bytes -join ".")
                    } else { $null }
                } else { $null }
                is_loopback = ($adapter.InterfaceType -eq 24 -or $a.IPAddress -eq "127.0.0.1" -or $a.IPAddress -eq "::1")  # noqa: E501
            }
        }

        $gateways = @()
        if ($config.IPv4DefaultGateway) {
            $gateways += $config.IPv4DefaultGateway.NextHop
        }
        if ($config.IPv6DefaultGateway) {
            $gateways += $config.IPv6DefaultGateway.NextHop
        }

        $dns = @()
        if ($config.DNSServer) {
            $dns = $config.DNSServer.ServerAddresses
        }

        # Parse driver date
        $driverDate = $null
        if ($adapter.DriverDate) {
            $driverDate = $adapter.DriverDate.ToString("yyyy-MM-dd")
        }

        $results += @{
            name = $adapter.Name
            friendly_name = $adapter.Name
            description = $adapter.InterfaceDescription
            interface_type = [string]$adapter.InterfaceType
            adapter_type = if ($adapter.Virtual) { "Virtual" } elseif ($adapter.MediaType -match "802.3") { "Ethernet" } elseif ($adapter.MediaType -match "802.11") { "Wi-Fi" } else { "Other" }  # noqa: E501
            manufacturer = $adapter.InterfaceDescription # Best effort for manufacturer without CIM
            mac_address = $adapter.MacAddress
            is_physical = -not $adapter.Virtual
            is_virtual = $adapter.Virtual
            status = $adapter.Status
            admin_status = $adapter.AdminStatus
            link_speed_bps = $null # LinkSpeed is returned as string like "1 Gbps", so skipping it here or parse in python  # noqa: E501
            link_speed_str = $adapter.LinkSpeed
            mtu = $adapter.Mtu
            driver_version = $adapter.DriverVersion
            driver_date = $driverDate
            interface_index = $adapter.ifIndex
            interface_guid = $adapter.InterfaceGuid
            dhcp_enabled = $config.NetIPv4Interface.DHCP -eq "Enabled"
            dhcp_server = $null # Not easily available without CIM
            default_gateways = $gateways
            dns_servers = $dns
            dns_search_suffixes = @()
            addresses = $addresses
        }
    }

    $results | ConvertTo-Json -Depth 4
    """
    adapters_out = []
    try:
        output = run_powershell(script)
        if not output.strip():
            return []
        data = json.loads(output)
        if isinstance(data, dict):
            data = [data]

        for d in data:
            # Parse link speed from "1 Gbps" to integer bits per second
            speed_bps = None
            speed_str = d.get("link_speed_str")
            if speed_str:
                parts = str(speed_str).strip().split()
                if len(parts) == 2:
                    val, unit = parts[0], parts[1].upper()
                    try:
                        val = float(val)
                        if unit == "BPS":
                            speed_bps = int(val)
                        elif unit == "KBPS":
                            speed_bps = int(val * 1000)
                        elif unit == "MBPS":
                            speed_bps = int(val * 1_000_000)
                        elif unit == "GBPS":
                            speed_bps = int(val * 1_000_000_000)
                    except ValueError:
                        pass

            driver_dt = None
            if d.get("driver_date"):
                try:
                    driver_dt = datetime.strptime(d["driver_date"], "%yyyy-%MM-%dd").date()
                except Exception:
                    pass

            addrs = []
            for a in d.get("addresses", []):
                addrs.append(
                    AddressPayload(
                        address=a.get("address"),
                        family=a.get("family"),
                        prefix_length=a.get("prefix_length"),
                        subnet_mask=a.get("subnet_mask"),
                        is_loopback=a.get("is_loopback", False),
                    )
                )

            adapters_out.append(
                AdapterPayload(
                    name=d.get("name"),
                    friendly_name=d.get("friendly_name"),
                    description=d.get("description"),
                    interface_type=d.get("interface_type"),
                    adapter_type=d.get("adapter_type"),
                    mac_address=d.get("mac_address"),
                    is_physical=bool(d.get("is_physical", True)),
                    is_virtual=bool(d.get("is_virtual", False)),
                    status=str(d.get("status")) if d.get("status") is not None else None,
                    admin_status=str(d.get("admin_status")) if d.get("admin_status") is not None else None,
                    link_speed_bps=speed_bps,
                    mtu=d.get("mtu"),
                    driver_version=d.get("driver_version"),
                    driver_date=driver_dt,
                    interface_index=d.get("interface_index"),
                    interface_guid=d.get("interface_guid"),
                    dhcp_enabled=d.get("dhcp_enabled"),
                    default_gateways=d.get("default_gateways") or [],
                    dns_servers=d.get("dns_servers") or [],
                    dns_search_suffixes=d.get("dns_search_suffixes") or [],
                    addresses=addrs,
                )
            )

    except Exception as e:
        logger.error("Failed to collect network adapters", error=str(e))

    return adapters_out


def collect_wifi_status() -> dict[str, WifiPayload]:
    """Collects Wi-Fi profiles and returns a mapping of interface name to WifiPayload."""
    script = r"""
    $interfaces = netsh wlan show interfaces
    if ($LASTEXITCODE -ne 0 -or -not $interfaces) { return "{}" }

    $results = @{}
    $currentIf = $null
    $wifiData = @{}

    foreach ($line in $interfaces -split "`r`n") {
        if ($line -match "^\s*Name\s*:\s*(.*)$") {
            if ($currentIf -and $wifiData.SSID) {
                $results[$currentIf] = $wifiData
            }
            $currentIf = $matches[1].Trim()
            $wifiData = @{}
        } elseif ($currentIf) {
            if ($line -match "^\s*SSID\s*:\s*(.*)$") { $wifiData.SSID = $matches[1].Trim() }
            if ($line -match "^\s*BSSID\s*:\s*(.*)$") { $wifiData.BSSID = $matches[1].Trim() }
            if ($line -match "^\s*Signal\s*:\s*(.*)%$") { $wifiData.Signal = [int]$matches[1].Trim() }  # noqa: E501
            if ($line -match "^\s*Authentication\s*:\s*(.*)$") { $wifiData.Auth = $matches[1].Trim() }  # noqa: E501
            if ($line -match "^\s*Radio type\s*:\s*(.*)$") { $wifiData.Radio = $matches[1].Trim() }
            if ($line -match "^\s*Channel\s*:\s*(.*)$") { $wifiData.Channel = [int]$matches[1].Trim() }  # noqa: E501
        }
    }
    if ($currentIf -and $wifiData.SSID) {
        $results[$currentIf] = $wifiData
    }

    $results | ConvertTo-Json -Depth 2
    """
    try:
        output = run_powershell(script)
        if not output.strip():
            return {}
        data = json.loads(output)

        out = {}
        for iface, w in data.items():
            out[iface] = WifiPayload(
                ssid=w.get("SSID"),
                bssid=w.get("BSSID"),
                signal_strength=w.get("Signal"),
                auth_type=w.get("Auth"),
                radio_type=w.get("Radio"),
                channel=w.get("Channel"),
            )
        return out
    except Exception as e:
        logger.error("Failed to collect wifi status", error=str(e))
        return {}


def collect_vpn_status() -> dict[str, VpnPayload]:
    """Collects VPN profiles and returns a mapping of interface name to VpnPayload."""
    script = r"""
    try {
        $vpns = Get-VpnConnection -ErrorAction SilentlyContinue
        $results = @{}
        foreach ($v in $vpns) {
            $results[$v.Name] = @{
                connection_status = [string]$v.ConnectionStatus
                tunnel_type = [string]$v.TunnelType
            }
        }
        $results | ConvertTo-Json -Depth 2
    } catch {
        "{}"
    }
    """
    try:
        output = run_powershell(script)
        if not output.strip():
            return {}
        data = json.loads(output)

        out = {}
        for iface, v in data.items():
            out[iface] = VpnPayload(
                connection_status=v.get("connection_status"),
                tunnel_type=v.get("tunnel_type"),
            )
        return out
    except Exception as e:
        logger.error("Failed to collect vpn status", error=str(e))
        return {}


def collect_network() -> NetworkInventoryRequest:
    """Orchestrates network collection."""
    logger.info("Starting network inventory collection")

    identity = collect_network_identity()
    adapters = collect_adapters()

    # Fault tolerance: Wi-Fi and VPN errors must not fail the run
    wifi_map = collect_wifi_status()
    vpn_map = collect_vpn_status()

    for a in adapters:
        if a.name in wifi_map:
            a.wifi = wifi_map[a.name]
        if a.name in vpn_map:
            a.vpn = vpn_map[a.name]

    payload = serialize_network(identity, adapters)
    inv_hash = compute_inventory_hash(payload)

    return NetworkInventoryRequest(
        collected_at=datetime.now(timezone.utc),
        agent_version=agent_settings.agent_version,
        inventory_hash=inv_hash,
        identity=identity,
        adapters=adapters,
    )
