from datetime import datetime
from unittest.mock import patch

from collectors.operating_system import collect


def test_collect_os_success():
    """Verify that a fully successful collection returns all expected fields."""

    def mock_run_powershell(cmd: str) -> str | None:
        if "Win32_OperatingSystem).Caption" in cmd:
            return "Microsoft Windows 11 Pro"
        if "EditionID" in cmd:
            return "Professional"
        if "Win32_OperatingSystem).Version" in cmd:
            return "10.0.22631"
        if "Win32_OperatingSystem).BuildNumber" in cmd:
            return "22631"
        if "DisplayVersion" in cmd:
            return "23H2"
        if "OSArchitecture" in cmd:
            return "64-bit"
        if "InstallDate" in cmd:
            return "2024-01-01T12:00:00.0000000+00:00"
        if "Win32_OperatingSystem).CSName" in cmd:
            return "DESKTOP-1234"
        if "Win32_ComputerSystem).Domain" in cmd:
            return "WORKGROUP"
        if "RegisteredUser" in cmd:
            return "Admin"
        if "Win32_TimeZone).Caption" in cmd:
            return "(UTC-05:00) Eastern Time (US & Canada)"
        if "Get-Culture" in cmd:
            return "en-US"
        return None

    def mock_boot_time() -> float:
        return 1700000000.0

    def mock_time() -> float:
        return 1700000100.0

    with (
        patch("collectors.operating_system.run_powershell", side_effect=mock_run_powershell),
        patch("collectors.operating_system._psutil.boot_time", side_effect=mock_boot_time),
        patch("collectors.operating_system.time.time", side_effect=mock_time),
        patch("collectors.operating_system._PSUTIL_AVAILABLE", True),
        patch("collectors.operating_system.platform.node", return_value="DESKTOP-1234"),
        patch("collectors.operating_system.platform.machine", return_value="AMD64"),
    ):
        inventory = collect()

        assert inventory.name == "Microsoft Windows 11 Pro"
        assert inventory.edition == "Professional"
        assert inventory.version == "10.0.22631"
        assert inventory.build_number == "22631"
        assert inventory.display_version == "23H2"
        assert inventory.architecture == "64-bit"
        # Since it parses the string, we should check it as datetime or string if validation isn't strict in our test,  # noqa: E501
        # but Pydantic parses it to datetime.
        assert isinstance(inventory.install_date, datetime)
        assert inventory.install_date.isoformat() == "2024-01-01T12:00:00+00:00"

        assert isinstance(inventory.last_boot_time, datetime)
        assert inventory.system_uptime_seconds == 100
        assert inventory.computer_name == "DESKTOP-1234"
        assert inventory.domain == "WORKGROUP"
        assert inventory.registered_owner == "Admin"
        assert inventory.time_zone == "(UTC-05:00) Eastern Time (US & Canada)"
        assert inventory.system_locale == "en-US"


def test_collect_os_partial_failure():
    """Verify that exceptions in individual collection functions don't crash."""

    def mock_run_powershell(cmd: str) -> str | None:
        if "Win32_OperatingSystem).Caption" in cmd:
            raise RuntimeError("CIM failure")
        if "Win32_OperatingSystem).Version" in cmd:
            return "10.0.19045"
        return None

    with (
        patch("collectors.operating_system.run_powershell", side_effect=mock_run_powershell),
        patch("collectors.operating_system._PSUTIL_AVAILABLE", False),
        patch("collectors.operating_system.platform.node", return_value=""),
    ):
        inventory = collect()

        assert inventory.name == "Unknown"
        assert inventory.version == "10.0.19045"
        assert inventory.build_number is None
        assert inventory.edition is None
        assert inventory.display_version is None
        # Default architecture from platform.machine
        assert inventory.architecture is not None
        assert inventory.install_date is None
        assert inventory.last_boot_time is None
        assert inventory.system_uptime_seconds is None
        assert inventory.computer_name is None
        assert inventory.domain is None


def test_collect_os_psutil_error():
    """Verify that an exception in psutil (e.g. permission error) doesn't crash."""

    def mock_run_powershell(cmd: str) -> str | None:
        return None

    def mock_boot_time() -> float:
        raise PermissionError("Access Denied")

    with (
        patch("collectors.operating_system.run_powershell", side_effect=mock_run_powershell),
        patch("collectors.operating_system._psutil.boot_time", side_effect=mock_boot_time),
        patch("collectors.operating_system._PSUTIL_AVAILABLE", True),
    ):
        inventory = collect()
        assert inventory.last_boot_time is None
        assert inventory.system_uptime_seconds is None
