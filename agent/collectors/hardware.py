"""
Hardware inventory collector for Windows hosts.

Gathers CPU, RAM, system identity, and BIOS information using ``psutil`` for
low-level OS statistics and ``Get-CimInstance`` PowerShell queries for
WMI/CIM data that ``psutil`` does not expose.

Every field is collected independently inside its own try/except block.
A failure to read one field does NOT prevent the remaining fields from being
collected; the failed field is set to ``None`` (or a safe default for
required integer fields).

Usage
-----
::

    from collectors.hardware import collect

    inventory = collect()   # always returns HardwareInventory, never raises
"""

import structlog

from models.inventory import HardwareInventory
from utils.powershell import run_powershell

logger = structlog.get_logger(__name__)

try:
    import psutil as _psutil

    _PSUTIL_AVAILABLE = True
except ImportError:  # pragma: no cover
    _PSUTIL_AVAILABLE = False
    logger.warning("psutil not available — RAM and logical CPU counts will default to 0")


# ---------------------------------------------------------------------------
# Internal field collectors
# ---------------------------------------------------------------------------


def _get_cpu_model() -> str:
    """
    Return the CPU brand string from CIM.

    Falls back to ``"Unknown"`` when PowerShell is unavailable or the query
    returns an empty result.
    """
    result = run_powershell("(Get-CimInstance Win32_Processor).Name")
    if result:
        # Normalise whitespace that some OEM strings carry
        return " ".join(result.split())
    return "Unknown"


def _get_cpu_cores() -> int:
    """Return the number of physical CPU cores via psutil."""
    if not _PSUTIL_AVAILABLE:
        return 0
    count = _psutil.cpu_count(logical=False)
    return int(count) if count is not None else 0


def _get_cpu_threads() -> int:
    """Return the number of logical CPU threads (including hyper-threading) via psutil."""
    if not _PSUTIL_AVAILABLE:
        return 0
    count = _psutil.cpu_count(logical=True)
    return int(count) if count is not None else 0


def _get_total_ram_bytes() -> int:
    """Return total installed RAM in bytes via psutil."""
    if not _PSUTIL_AVAILABLE:
        return 0
    try:
        return int(_psutil.virtual_memory().total)
    except Exception as exc:  # noqa: BLE001
        logger.debug("Failed to read RAM via psutil", error=str(exc))
        return 0


def _get_system_manufacturer() -> str | None:
    """Return OEM manufacturer name from CIM (e.g. ``'Dell Inc.'``)."""
    return run_powershell("(Get-CimInstance Win32_ComputerSystem).Manufacturer")


def _get_system_model() -> str | None:
    """Return product/model name from CIM (e.g. ``'Latitude 7420'``)."""
    return run_powershell("(Get-CimInstance Win32_ComputerSystem).Model")


def _get_bios_version() -> str | None:
    """Return the SMBIOS BIOS version string from CIM."""
    return run_powershell("(Get-CimInstance Win32_BIOS).SMBIOSBIOSVersion")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def collect() -> HardwareInventory:
    """
    Collect hardware inventory from the local Windows host.

    Each field is fetched inside an individual try/except so that a failure
    in one collection path (e.g. CIM unavailable) does not prevent the rest
    from succeeding.

    Returns
    -------
    HardwareInventory
        Validated inventory model.  Required integer fields (``cpu_cores``,
        ``cpu_threads``, ``total_ram_bytes``) default to ``0`` rather than
        ``None``.  Optional string fields default to ``None``.

    Raises
    ------
    This function never raises.  All exceptions are caught and logged.
    """
    logger.info("Hardware inventory collection started")

    # ── cpu_model ────────────────────────────────────────────────────────────
    cpu_model: str = "Unknown"
    try:
        cpu_model = _get_cpu_model()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect cpu_model", error=str(exc))

    # ── cpu_cores ────────────────────────────────────────────────────────────
    cpu_cores: int = 0
    try:
        cpu_cores = _get_cpu_cores()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect cpu_cores", error=str(exc))

    # ── cpu_threads ──────────────────────────────────────────────────────────
    cpu_threads: int = 0
    try:
        cpu_threads = _get_cpu_threads()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect cpu_threads", error=str(exc))

    # ── total_ram_bytes ──────────────────────────────────────────────────────
    total_ram_bytes: int = 0
    try:
        total_ram_bytes = _get_total_ram_bytes()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect total_ram_bytes", error=str(exc))

    # ── system_manufacturer ──────────────────────────────────────────────────
    system_manufacturer: str | None = None
    try:
        system_manufacturer = _get_system_manufacturer()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect system_manufacturer", error=str(exc))

    # ── system_model ─────────────────────────────────────────────────────────
    system_model: str | None = None
    try:
        system_model = _get_system_model()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect system_model", error=str(exc))

    # ── bios_version ─────────────────────────────────────────────────────────
    bios_version: str | None = None
    try:
        bios_version = _get_bios_version()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to collect bios_version", error=str(exc))

    inventory = HardwareInventory(
        cpu_model=cpu_model,
        cpu_cores=cpu_cores,
        cpu_threads=cpu_threads,
        total_ram_bytes=total_ram_bytes,
        system_manufacturer=system_manufacturer,
        system_model=system_model,
        bios_version=bios_version,
    )

    logger.info(
        "Hardware inventory collection completed",
        cpu_model=inventory.cpu_model,
        cpu_cores=inventory.cpu_cores,
        cpu_threads=inventory.cpu_threads,
        total_ram_gb=round(inventory.total_ram_bytes / (1024**3), 2),
        system_manufacturer=inventory.system_manufacturer,
        system_model=inventory.system_model,
    )

    return inventory
