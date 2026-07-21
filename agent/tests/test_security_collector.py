"""
Unit tests for the Security inventory collector.
"""

from unittest.mock import patch

from collectors.security import _parse_ps_date, collect


def test_parse_ps_date_handles_json_dates():
    # \/Date(1721532000000)\/ -> 2024-07-21T03:20:00+00:00
    dt = _parse_ps_date(r"\/Date(1721532000000)\/")
    assert dt is not None
    assert dt.year == 2024
    assert dt.isoformat() == "2024-07-21T03:20:00+00:00"


def test_collect_security_success():
    """Verify full successful collection when all PowerShell APIs return valid data."""

    def mock_run_powershell(cmd: str) -> str | None:
        if "Get-MpComputerStatus" in cmd:
            return (
                '{"AMServiceEnabled": true, "RealTimeProtectionEnabled": true, '
                '"AMProductVersion": "4.18", "AntivirusSignatureLastUpdated": '
                '"\\\\/Date(1721532000000)\\\\/", "IsTamperProtected": true}'
            )
        elif "Get-Tpm" in cmd:
            return '{"TpmPresent": true, "TpmReady": true, "TpmEnabled": true, "ManufacturerId": "INTC"}'
        elif "Confirm-SecureBootUEFI" in cmd:
            return '{"supported": true, "enabled": true}'
        elif "Policies\\System" in cmd:
            return '{"enabled": true, "consent": "2"}'
        elif "SecurityCenter2" in cmd:
            return '{"av": "Windows Defender", "fw": "Windows Firewall", "ps": 397568}'
        elif "Get-BitLockerVolume" in cmd:
            return (
                '[{"MountPoint": "C:", "ProtectionStatus": 1, "EncryptionPercentage": 100, '
                '"AutoUnlockEnabled": false, "KeyProtectorCount": 2}]'
            )
        elif "Get-NetFirewallProfile" in cmd:
            return '[{"Name": "Domain", "Enabled": true}, {"Name": "Private", "Enabled": false}]'
        elif "IsInRole" in cmd:
            return "True"
        return None

    with patch("collectors.security.run_powershell", side_effect=mock_run_powershell):
        inventory = collect()

        assert inventory.defender is not None
        assert inventory.defender.enabled is True
        assert inventory.defender.real_time_protection is True
        assert inventory.defender.antivirus_signature_version == "4.18"
        assert inventory.defender.tamper_protection is True

        assert inventory.tpm is not None
        assert inventory.tpm.present is True
        assert inventory.tpm.manufacturer == "INTC"

        assert inventory.secure_boot is not None
        assert inventory.secure_boot.supported is True
        assert inventory.secure_boot.enabled is True

        assert inventory.uac is not None
        assert inventory.uac.enabled is True

        assert inventory.security_center is not None
        assert inventory.security_center.registered_antivirus == "Windows Defender"

        assert len(inventory.bitlocker_volumes) == 1
        assert inventory.bitlocker_volumes[0].drive_letter == "C:"
        assert inventory.bitlocker_volumes[0].encryption_percentage == 100.0

        assert len(inventory.firewall_profiles) == 2
        assert inventory.firewall_profiles[0].profile_name == "Domain"
        assert inventory.firewall_profiles[0].enabled is True
        assert inventory.firewall_profiles[1].profile_name == "Private"
        assert inventory.firewall_profiles[1].enabled is False


def test_collect_security_partial_failure():
    """Verify that exceptions in individual collection functions don't crash the entire collection."""

    def mock_run_powershell(cmd: str) -> str | None:
        if "IsInRole" in cmd:
            return "True"
        elif "Get-BitLockerVolume" in cmd:
            raise RuntimeError("Access Denied")
        # Let other commands return None/empty
        return None

    with patch("collectors.security.run_powershell", side_effect=mock_run_powershell):
        inventory = collect()
        # Should gracefully return empty values without crashing
        assert inventory.defender is not None
        assert inventory.defender.installed is False
        assert inventory.bitlocker_volumes == []
        assert inventory.tpm is None


def test_collect_security_no_admin():
    """Verify safe defaults when running without admin privileges."""

    def mock_run_powershell(cmd: str) -> str | None:
        if "IsInRole" in cmd:
            return "False"  # Not admin
        if "Get-MpComputerStatus" in cmd:
            return '{"AMServiceEnabled": true}'
        return None

    with patch("collectors.security.run_powershell", side_effect=mock_run_powershell):
        inventory = collect()

        # Defender doesn't strictly need admin depending on env, so it collected
        assert inventory.defender is not None

        # But TPM, Secure Boot, and BitLocker immediately return None/[] if not admin
        assert inventory.tpm is None
        assert inventory.secure_boot is None
        assert inventory.bitlocker_volumes == []
