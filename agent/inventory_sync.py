"""
Hardware inventory synchronization orchestrator.

Ties together collection, serialization, hashing, and upload into a single
``sync_hardware()`` call that can be invoked from the agent main loop or
scheduled independently.

Workflow
--------
1.  Log collection started
2.  Collect hardware inventory → :class:`~models.inventory.HardwareInventory`
3.  Log collection completed + duration
4.  Serialize inventory → ``dict``
5.  Compute SHA-256 hash
6.  Log payload size + hash
7.  Build the full ``HardwareInventoryRequest`` body (inventory + metadata)
8.  Upload via :func:`~api.inventory.submit_hardware`
9.  Log upload result

Safety
------
The entire function is wrapped in a broad ``try/except`` so that **no** error
— however unexpected — can propagate to the agent main loop.
"""

import json
import time
from datetime import UTC, datetime

import structlog

from api.inventory import submit_hardware, submit_os, submit_security
from collectors.hardware import collect as collect_hardware
from collectors.operating_system import collect as collect_os
from collectors.security import collect as collect_security
from config.settings import AgentConfig, agent_settings
from utils.hashing import compute_inventory_hash
from utils.serialization import serialize_hardware, serialize_os, serialize_security

logger = structlog.get_logger(__name__)


def sync_hardware(config: AgentConfig | None = None) -> None:
    """
    Run the complete hardware inventory synchronization cycle.

    Parameters
    ----------
    config:
        Agent configuration instance.  Defaults to the module-level
        ``agent_settings`` singleton when ``None``.

    Returns
    -------
    None
        Always.  The function never raises or propagates exceptions.
    """
    cfg = config or agent_settings

    try:
        _run_sync_hardware(cfg)
    except Exception as exc:  # noqa: BLE001
        # Safety net — should never be reached given inner try/except blocks,
        # but prevents any unforeseen path from crashing the agent.
        logger.error(
            "Unexpected error in hardware inventory sync — agent continues",
            error=str(exc),
        )


def _run_sync_hardware(cfg: AgentConfig) -> None:
    """Internal sync implementation — called by :func:`sync_hardware`."""
    log = logger.bind(category="hardware", agent_version=cfg.agent_version)

    # ── 1. Collection ────────────────────────────────────────────────────────
    log.info("Hardware inventory collection started")
    t0 = time.monotonic()

    inventory = collect_hardware()

    collection_duration_ms = int((time.monotonic() - t0) * 1000)
    log.info(
        "Hardware inventory collection completed",
        duration_ms=collection_duration_ms,
        cpu_model=inventory.cpu_model,
        cpu_cores=inventory.cpu_cores,
        cpu_threads=inventory.cpu_threads,
        total_ram_gb=round(inventory.total_ram_bytes / (1024**3), 2),
    )

    # ── 2. Serialization ─────────────────────────────────────────────────────
    hardware_dict = serialize_hardware(inventory)

    payload_bytes = len(json.dumps(hardware_dict).encode("utf-8"))
    log.info("Hardware inventory payload serialized", payload_bytes=payload_bytes)

    # ── 3. Hashing ───────────────────────────────────────────────────────────
    inventory_hash = compute_inventory_hash(hardware_dict)
    log.info("Hardware inventory hash computed", inventory_hash=inventory_hash)

    # ── 4. Build request body ────────────────────────────────────────────────
    collected_at = datetime.now(UTC).isoformat()

    request_body: dict = {
        "collected_at": collected_at,
        "agent_version": cfg.agent_version,
        "inventory_hash": inventory_hash,
        "hardware": hardware_dict,
    }

    # ── 5. Upload ────────────────────────────────────────────────────────────
    log.info("Hardware inventory upload started", inventory_hash=inventory_hash)
    t1 = time.monotonic()

    submit_hardware(body=request_body, config=cfg)

    upload_duration_ms = int((time.monotonic() - t1) * 1000)
    log.info("Hardware inventory sync cycle finished", upload_duration_ms=upload_duration_ms)


def sync_os(config: AgentConfig | None = None) -> None:
    """
    Run the complete operating system inventory synchronization cycle.

    Parameters
    ----------
    config:
        Agent configuration instance.  Defaults to the module-level
        ``agent_settings`` singleton when ``None``.

    Returns
    -------
    None
        Always.  The function never raises or propagates exceptions.
    """
    cfg = config or agent_settings

    try:
        _run_sync_os(cfg)
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Unexpected error in OS inventory sync — agent continues",
            error=str(exc),
        )


def _run_sync_os(cfg: AgentConfig) -> None:
    """Internal sync implementation — called by :func:`sync_os`."""
    log = logger.bind(category="os", agent_version=cfg.agent_version)

    # ── 1. Collection ────────────────────────────────────────────────────────
    log.info("OS inventory collection started")
    t0 = time.monotonic()

    inventory = collect_os()

    collection_duration_ms = int((time.monotonic() - t0) * 1000)
    log.info(
        "OS inventory collection completed",
        duration_ms=collection_duration_ms,
        os_name=inventory.name,
        os_version=inventory.version,
    )

    # ── 2. Serialization ─────────────────────────────────────────────────────
    os_dict = serialize_os(inventory)

    payload_bytes = len(json.dumps(os_dict).encode("utf-8"))
    log.info("OS inventory payload serialized", payload_bytes=payload_bytes)

    # ── 3. Hashing ───────────────────────────────────────────────────────────
    inventory_hash = compute_inventory_hash(os_dict)
    log.info("OS inventory hash computed", inventory_hash=inventory_hash)

    # ── 4. Build request body ────────────────────────────────────────────────
    collected_at = datetime.now(UTC).isoformat()

    request_body: dict = {
        "collected_at": collected_at,
        "agent_version": cfg.agent_version,
        "inventory_hash": inventory_hash,
        "os": os_dict,
    }

    # ── 5. Upload ────────────────────────────────────────────────────────────
    log.info("OS inventory upload started", inventory_hash=inventory_hash)
    t1 = time.monotonic()

    submit_os(body=request_body, config=cfg)

    upload_duration_ms = int((time.monotonic() - t1) * 1000)
    log.info("OS inventory sync cycle finished", upload_duration_ms=upload_duration_ms)


def sync_security(config: AgentConfig | None = None) -> None:
    """
    Run the complete security inventory synchronization cycle.

    Parameters
    ----------
    config:
        Agent configuration instance.  Defaults to the module-level
        ``agent_settings`` singleton when ``None``.

    Returns
    -------
    None
        Always.  The function never raises or propagates exceptions.
    """
    cfg = config or agent_settings

    try:
        _run_sync_security(cfg)
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Unexpected error in Security inventory sync — agent continues",
            error=str(exc),
        )


def _run_sync_security(cfg: AgentConfig) -> None:
    """Internal sync implementation — called by :func:`sync_security`."""
    log = logger.bind(category="security", agent_version=cfg.agent_version)

    # ── 1. Collection ────────────────────────────────────────────────────────
    log.info("Security inventory collection started")
    t0 = time.monotonic()

    inventory = collect_security()

    collection_duration_ms = int((time.monotonic() - t0) * 1000)
    log.info(
        "Security inventory collection completed",
        duration_ms=collection_duration_ms,
        defender_success=inventory.defender is not None,
        tpm_success=inventory.tpm is not None,
        secure_boot_success=inventory.secure_boot is not None,
        uac_success=inventory.uac is not None,
        security_center_success=inventory.security_center is not None,
        bitlocker_volumes=len(inventory.bitlocker_volumes),
        firewall_profiles=len(inventory.firewall_profiles),
    )

    # ── 2. Serialization ─────────────────────────────────────────────────────
    sec_dict = serialize_security(inventory)

    payload_bytes = len(json.dumps(sec_dict).encode("utf-8"))
    log.info("Security inventory payload serialized", payload_bytes=payload_bytes)

    # ── 3. Hashing ───────────────────────────────────────────────────────────
    inventory_hash = compute_inventory_hash(sec_dict)
    log.info("Security inventory hash computed", inventory_hash=inventory_hash)

    # ── 4. Build request body ────────────────────────────────────────────────
    collected_at = datetime.now(UTC).isoformat()

    request_body: dict = {
        "collected_at": collected_at,
        "agent_version": cfg.agent_version,
        "inventory_hash": inventory_hash,
        "security": sec_dict,
    }

    # ── 5. Upload ────────────────────────────────────────────────────────────
    log.info("Security inventory upload started", inventory_hash=inventory_hash)
    t1 = time.monotonic()

    submit_security(body=request_body, config=cfg)

    upload_duration_ms = int((time.monotonic() - t1) * 1000)
    log.info("Security inventory sync cycle finished", upload_duration_ms=upload_duration_ms)


def sync_network(config: AgentConfig | None = None) -> None:
    """
    Run the complete network inventory synchronization cycle.

    Parameters
    ----------
    config:
        Agent configuration instance.  Defaults to the module-level
        ``agent_settings`` singleton when ``None``.

    Returns
    -------
    None
        Always.  The function never raises or propagates exceptions.
    """
    cfg = config or agent_settings

    try:
        _run_sync_network(cfg)
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Unexpected error in Network inventory sync — agent continues",
            error=str(exc),
        )


def _run_sync_network(cfg: AgentConfig) -> None:
    """Internal sync implementation — called by :func:`sync_network`."""
    from api.inventory import submit_network
    from collectors.network import collect_network

    log = logger.bind(category="network", agent_version=cfg.agent_version)

    # ── 1. Collection ────────────────────────────────────────────────────────
    log.info("Network inventory collection started")
    t0 = time.monotonic()

    inventory = collect_network()

    collection_duration_ms = int((time.monotonic() - t0) * 1000)
    log.info(
        "Network inventory collection completed",
        duration_ms=collection_duration_ms,
        identity_fqdn=inventory.identity.fqdn,
        adapters_count=len(inventory.adapters),
    )

    # ── 2. Serialization ─────────────────────────────────────────────────────
    # Serialization and Hashing already done in the collector for Network, but to keep with architecture:  # noqa: E501
    from utils.serialization import serialize_network

    net_dict = serialize_network(inventory.identity, inventory.adapters)

    payload_bytes = len(json.dumps(net_dict).encode("utf-8"))
    log.info("Network inventory payload serialized", payload_bytes=payload_bytes)

    # ── 3. Hashing ───────────────────────────────────────────────────────────
    from utils.hashing import compute_inventory_hash

    inventory_hash = compute_inventory_hash(net_dict)
    log.info("Network inventory hash computed", inventory_hash=inventory_hash)

    # ── 4. Build request body ────────────────────────────────────────────────
    collected_at = datetime.now(UTC).isoformat()

    request_body: dict = {
        "collected_at": collected_at,
        "agent_version": cfg.agent_version,
        "inventory_hash": inventory_hash,
        "identity": net_dict["identity"],
        "adapters": net_dict["adapters"],
    }

    # ── 5. Upload ────────────────────────────────────────────────────────────
    log.info("Network inventory upload started", inventory_hash=inventory_hash)
    t1 = time.monotonic()

    submit_network(body=request_body, config=cfg)

    upload_duration_ms = int((time.monotonic() - t1) * 1000)
    log.info("Network inventory sync cycle finished", upload_duration_ms=upload_duration_ms)


def sync_storage(config: AgentConfig | None = None) -> None:
    """
    Run the complete storage inventory synchronization cycle.

    Parameters
    ----------
    config:
        Agent configuration instance.  Defaults to the module-level
        ``agent_settings`` singleton when ``None``.
    """
    cfg = config or agent_settings

    try:
        _run_sync_storage(cfg)
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Unexpected error in Storage inventory sync — agent continues",
            error=str(exc),
        )


def _run_sync_storage(cfg: AgentConfig) -> None:
    """Internal sync implementation — called by :func:`sync_storage`."""
    from api.inventory import submit_storage
    from collectors.storage import collect_storage

    log = logger.bind(category="storage", agent_version=cfg.agent_version)

    # ── 1. Collection ────────────────────────────────────────────────────────
    log.info("Storage inventory collection started")
    t0 = time.monotonic()

    inventory = collect_storage()

    collection_duration_ms = int((time.monotonic() - t0) * 1000)
    log.info(
        "Storage inventory collection completed",
        duration_ms=collection_duration_ms,
        disks_count=len(inventory.disks),
        volumes_count=len(inventory.volumes),
        pools_count=len(inventory.storage_pools),
    )

    # ── 2. Serialization ─────────────────────────────────────────────────────
    from utils.serialization import serialize_storage

    storage_dict = serialize_storage(inventory)
    payload_bytes = len(json.dumps(storage_dict).encode("utf-8"))
    log.info("Storage inventory payload serialized", payload_bytes=payload_bytes)

    # ── 3. Hashing ───────────────────────────────────────────────────────────
    from utils.hashing import compute_inventory_hash

    inventory_hash = compute_inventory_hash(storage_dict)
    log.info("Storage inventory hash computed", inventory_hash=inventory_hash)

    # ── 4. Build request body ────────────────────────────────────────────────
    collected_at = datetime.now(UTC).isoformat()

    request_body: dict = {
        "collected_at": collected_at,
        "agent_version": cfg.agent_version,
        "inventory_hash": inventory_hash,
        "disks": storage_dict["disks"],
        "volumes": storage_dict["volumes"],
        "storage_pools": storage_dict["storage_pools"],
    }

    # ── 5. Upload ────────────────────────────────────────────────────────────
    log.info("Storage inventory upload started", inventory_hash=inventory_hash)
    t1 = time.monotonic()

    submit_storage(body=request_body, config=cfg)

    upload_duration_ms = int((time.monotonic() - t1) * 1000)
    log.info("Storage inventory sync cycle finished", upload_duration_ms=upload_duration_ms)


def sync_software(config: AgentConfig | None = None) -> None:
    """
    Run the complete software inventory synchronization cycle.

    Parameters
    ----------
    config:
        Agent configuration instance.  Defaults to the module-level
        ``agent_settings`` singleton when ``None``.
    """
    cfg = config or agent_settings

    try:
        _run_sync_software(cfg)
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Unexpected error in Software inventory sync — agent continues",
            error=str(exc),
        )


def _run_sync_software(cfg: AgentConfig) -> None:
    """Internal sync implementation — called by :func:`sync_software`."""
    from api.inventory import submit_software
    from collectors.software import collect_software

    log = logger.bind(category="software", agent_version=cfg.agent_version)

    # ── 1. Collection ────────────────────────────────────────────────────────
    log.info("Software inventory collection started")
    t0 = time.monotonic()

    inventory = collect_software()

    collection_duration_ms = int((time.monotonic() - t0) * 1000)
    log.info(
        "Software inventory collection completed",
        duration_ms=collection_duration_ms,
        software_count=len(inventory.software),
    )

    # ── 2. Serialization ─────────────────────────────────────────────────────
    from utils.serialization import serialize_software

    software_dict = serialize_software(inventory)
    payload_bytes = len(json.dumps(software_dict).encode("utf-8"))
    log.info("Software inventory payload serialized", payload_bytes=payload_bytes)

    # ── 3. Hashing ───────────────────────────────────────────────────────────
    from utils.hashing import compute_inventory_hash

    inventory_hash = compute_inventory_hash(software_dict)
    log.info("Software inventory hash computed", inventory_hash=inventory_hash)

    # ── 4. Build request body ────────────────────────────────────────────────
    collected_at = datetime.now(UTC).isoformat()

    request_body: dict = {
        "collected_at": collected_at,
        "agent_version": cfg.agent_version,
        "inventory_hash": inventory_hash,
        "software": software_dict["software"],
    }

    # ── 5. Upload ────────────────────────────────────────────────────────────
    log.info("Software inventory upload started", inventory_hash=inventory_hash)
    t1 = time.monotonic()

    submit_software(body=request_body, config=cfg)

    upload_duration_ms = int((time.monotonic() - t1) * 1000)
    log.info("Software inventory sync cycle finished", upload_duration_ms=upload_duration_ms)
