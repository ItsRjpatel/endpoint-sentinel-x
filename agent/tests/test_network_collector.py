# ruff: noqa: E501
from unittest.mock import patch

from collectors.network import (
    collect_adapters,
    collect_network,
    collect_network_identity,
    collect_vpn_status,
    collect_wifi_status,
)
from models.inventory import AdapterPayload, NetworkIdentityPayload


def test_collect_network_identity():
    with patch("collectors.network.run_powershell") as mock_ps:
        mock_ps.return_value = (
            '{"fqdn": "test.local", "domain_workgroup": "local", "primary_dns_suffix": "local"}'
        )
        ident = collect_network_identity()
        assert ident.fqdn == "test.local"


def test_collect_adapters_empty():
    with patch("collectors.network.run_powershell") as mock_ps:
        mock_ps.return_value = ""
        adapters = collect_adapters()
        assert len(adapters) == 0


def test_collect_adapters_parsing():
    with patch("collectors.network.run_powershell") as mock_ps:
        mock_ps.return_value = """[
            {
                "name": "Ethernet",
                "is_physical": true,
                "is_virtual": false,
                "link_speed_str": "1 Gbps",
                "addresses": [{"address": "192.168.1.10", "family": "ipv4", "prefix_length": 24, "subnet_mask": "255.255.255.0", "is_loopback": false}]
            }
        ]"""
        adapters = collect_adapters()
        assert len(adapters) == 1
        assert adapters[0].name == "Ethernet"
        assert adapters[0].link_speed_bps == 1000000000
        assert adapters[0].addresses[0].address == "192.168.1.10"
        assert adapters[0].addresses[0].subnet_mask == "255.255.255.0"


def test_collect_wifi_status():
    with patch("collectors.network.run_powershell") as mock_ps:
        mock_ps.return_value = '{"Wi-Fi": {"SSID": "MyNet", "Signal": 99, "Auth": "WPA2"}}'
        wifi = collect_wifi_status()
        assert "Wi-Fi" in wifi
        assert wifi["Wi-Fi"].ssid == "MyNet"


def test_collect_vpn_status():
    with patch("collectors.network.run_powershell") as mock_ps:
        mock_ps.return_value = '{"VPN": {"connection_status": "Connected", "tunnel_type": "IKEv2"}}'
        vpn = collect_vpn_status()
        assert "VPN" in vpn
        assert vpn["VPN"].tunnel_type == "IKEv2"


def test_collect_network_orchestrator():
    with (
        patch("collectors.network.collect_network_identity") as m_id,
        patch("collectors.network.collect_adapters") as m_ad,
        patch("collectors.network.collect_wifi_status") as m_wifi,
        patch("collectors.network.collect_vpn_status") as m_vpn,
    ):
        m_id.return_value = NetworkIdentityPayload(
            fqdn="foo", domain_workgroup="bar", primary_dns_suffix="baz"
        )
        adapter = AdapterPayload(name="Ethernet", is_physical=True)
        m_ad.return_value = [adapter]
        m_wifi.return_value = {}
        m_vpn.return_value = {}

        req = collect_network()
        assert req.identity.fqdn == "foo"
        assert len(req.adapters) == 1
