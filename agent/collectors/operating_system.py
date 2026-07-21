"""
Operating System inventory collector for Windows hosts.

Gathers OS identity, versioning, uptime, and locale information using ``psutil``,
``platform``, and ``Get-CimInstance`` PowerShell queries.

Every field is collected independently inside its own try/except block.
A failure to read one field does NOT prevent the remaining fields from being
collected; the failed field is set to ``None``.

Usage
-----
::

    from collectors.operating_system import collect

    inventory = collect()   # always returns OperatingSystemInventory, never raises
"""

import platform
import time
from datetime import UTC, datetime

import structlog

from models.inventory import OperatingSystemInventory
from utils.powershell import run_powershell

logger = structlog.get_logger(__name__)

try:
    import psutil as _psutil

    _PSUTIL_AVAILABLE = True
except ImportError:  # pragma: no cover
    _PSUTIL_AVAILABLE = False
    logger.warning("psutil not available — boot time and uptime will default to None")


# ---------------------------------------------------------------------------
# Internal field collectors
# ---------------------------------------------------------------------------


def _get_os_name() -> str:
    """Return the OS brand string from CIM."""
    result = run_powershell("(Get-CimInstance Win32_OperatingSystem).Caption")
    if result:
        return " ".join(result.split())
    return "Unknown"


def _get_edition() -> str | None:
    """Return the OS edition from the registry."""
    return run_powershell(
        "Get-ItemPropertyValue -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion' -Name 'EditionID' -ErrorAction SilentlyContinue"  # noqa: E501
    )


def _get_version() -> str:
    """Return the OS version string from CIM."""
    result = run_powershell("(Get-CimInstance Win32_OperatingSystem).Version")
    return result if result else "Unknown"


def _get_build_number() -> str | None:
    """Return the OS build number from CIM."""
    return run_powershell("(Get-CimInstance Win32_OperatingSystem).BuildNumber")


def _get_display_version() -> str | None:
    """Return the OS display version (e.g., 22H2) from the registry."""
    return run_powershell(
        "Get-ItemPropertyValue -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion' -Name 'DisplayVersion' -ErrorAction SilentlyContinue"  # noqa: E501
    )


def _get_architecture() -> str:
    """Return the OS architecture from CIM."""
    result = run_powershell("(Get-CimInstance Win32_OperatingSystem).OSArchitecture")
    return result if result else platform.machine() or "Unknown"


def _get_install_date() -> str | None:
    """Return the OS installation date as an ISO 8601 string from CIM."""
    return run_powershell("(Get-CimInstance Win32_OperatingSystem).InstallDate.ToString('o')")


def _get_boot_info() -> tuple[datetime | None, int | None]:
    """Return the last boot time and system uptime in seconds via psutil."""
    if not _PSUTIL_AVAILABLE:
        return None, None
    try:
        boot_ts = _psutil.boot_time()
        uptime = max(0, int(time.time() - boot_ts))
        boot_dt = datetime.fromtimestamp(boot_ts, tz=UTC)
        return boot_dt, uptime
    except Exception as exc:  # noqa: BLE001
        logger.debug("Failed to read boot time via psutil", error=str(exc))
        return None, None


def _get_computer_name() -> str | None:
    """Return the local computer name."""
    # platform.node() is generally reliable and doesn't require a subprocess
    node = platform.node()
    if node:
        return node
    return run_powershell("(Get-CimInstance Win32_OperatingSystem).CSName")


def _get_domain() -> str | None:
    """Return the domain or workgroup name from CIM."""
    return run_powershell("(Get-CimInstance Win32_ComputerSystem).Domain")


def _get_registered_owner() -> str | None:
    """Return the registered owner name from CIM."""
    return run_powershell("(Get-CimInstance Win32_OperatingSystem).RegisteredUser")


def _get_time_zone() -> str | None:
    """Return the time zone caption from CIM."""
    return run_powershell("(Get-CimInstance Win32_TimeZone).Caption")


def _get_system_locale() -> str | None:
    """Return the system culture/locale string (e.g., en-US)."""
    return run_powershell("(Get-Culture).Name")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def collect() -> OperatingSystemInventory:
    """
    Collect operating system inventory from the local Windows host.

    Each field is fetched inside an individual try/except so that a failure
    in one collection path does not prevent the rest from succeeding.

    Returns
    -------
    OperatingSystemInventory
        Validated inventory model.

    Raises
    ------
    This function never raises.  All exceptions are caught and logged.
    """
    logger.info("OS inventory collection started")

    # ── name ─────────────────────────────────────────────────────────────────
    name: str = "Unknown"
    try:
        name = _get_os_name()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect OS name", error=str(exc))

    # ── edition ──────────────────────────────────────────────────────────────
    edition: str | None = None
    try:
        edition = _get_edition()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect OS edition", error=str(exc))

    # ── version ──────────────────────────────────────────────────────────────
    version: str = "Unknown"
    try:
        version = _get_version()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect OS version", error=str(exc))

    # ── build_number ─────────────────────────────────────────────────────────
    build_number: str | None = None
    try:
        build_number = _get_build_number()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect OS build_number", error=str(exc))

    # ── display_version ──────────────────────────────────────────────────────
    display_version: str | None = None
    try:
        display_version = _get_display_version()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect OS display_version", error=str(exc))

    # ── architecture ─────────────────────────────────────────────────────────
    architecture: str = "Unknown"
    try:
        architecture = _get_architecture()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect OS architecture", error=str(exc))

    # ── install_date ─────────────────────────────────────────────────────────
    install_date: datetime | None = None
    try:
        # We rely on Pydantic to parse the ISO 8601 string returned by CIM
        raw_install_date = _get_install_date()
        if raw_install_date:
            # We don't strictly parse it here, we pass it to the model.
            # But the variable is typed as datetime|None. We'll pass the string,
            # and the model instantiation will cast it.
            install_date = raw_install_date  # type: ignore
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect OS install_date", error=str(exc))

    # ── boot time & uptime ───────────────────────────────────────────────────
    last_boot_time: datetime | None = None
    system_uptime_seconds: int | None = None
    try:
        last_boot_time, system_uptime_seconds = _get_boot_info()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect boot info", error=str(exc))

    # ── computer_name ────────────────────────────────────────────────────────
    computer_name: str | None = None
    try:
        computer_name = _get_computer_name()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect computer_name", error=str(exc))

    # ── domain ───────────────────────────────────────────────────────────────
    domain: str | None = None
    try:
        domain = _get_domain()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect domain", error=str(exc))

    # ── registered_owner ─────────────────────────────────────────────────────
    registered_owner: str | None = None
    try:
        registered_owner = _get_registered_owner()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect registered_owner", error=str(exc))

    # ── time_zone ────────────────────────────────────────────────────────────
    time_zone: str | None = None
    try:
        time_zone = _get_time_zone()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect time_zone", error=str(exc))

    # ── system_locale ────────────────────────────────────────────────────────
    system_locale: str | None = None
    try:
        system_locale = _get_system_locale()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect system_locale", error=str(exc))

    inventory = OperatingSystemInventory(
        name=name,
        edition=edition,
        version=version,
        build_number=build_number,
        display_version=display_version,
        architecture=architecture,
        install_date=install_date,
        last_boot_time=last_boot_time,
        system_uptime_seconds=system_uptime_seconds,
        computer_name=computer_name,
        domain=domain,
        registered_owner=registered_owner,
        time_zone=time_zone,
        system_locale=system_locale,
    )

    logger.info(
        "OS inventory collection completed",
        os_name=inventory.name,
        os_version=inventory.version,
        computer_name=inventory.computer_name,
    )

    return inventory
