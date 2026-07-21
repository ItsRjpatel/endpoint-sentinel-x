"""
Windows Services Inventory Collector
====================================

Collects all Windows services metadata on the endpoint using a hybrid approach:
1. `Get-CimInstance Win32_Service` for high-performance retrieval of standard metadata.
2. `Get-ItemProperty` on `HKLM:\\SYSTEM\\CurrentControlSet\\Services\\*` for extended properties like `DelayedAutoStart` and `TriggerStart`.
3. `Get-Service` for dependencies (or just registry `DependOnService`). We will use registry to avoid expensive objects.
"""

import json
from datetime import datetime, timezone

import structlog

from config.settings import agent_settings
from models.inventory import ServicePayload, ServicesInventoryRequest
from utils.hashing import compute_inventory_hash
from utils.powershell import run_powershell
from utils.serialization import serialize_services

logger = structlog.get_logger(__name__)

# PowerShell script to collect services
_PS_SCRIPT = """
$ErrorActionPreference = 'SilentlyContinue'

# Read all services from CIM
$cimServices = Get-CimInstance -ClassName Win32_Service

# Read all service registry keys for extended metadata
$regPath = "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\*"
$regKeys = Get-ItemProperty -Path $regPath -ErrorAction SilentlyContinue

# Create a hashtable for fast registry lookups by name
$regMap = @{}
foreach ($r in $regKeys) {
    # The PSChildName is the exact service name
    $regMap[$r.PSChildName] = $r
}

$results = @()

foreach ($s in $cimServices) {
    $name = $s.Name
    $reg = $regMap[$name]

    # Resolve dependencies from registry
    $deps = @()
    if ($reg.DependOnService) {
        $deps = @($reg.DependOnService)
    }

    # Delayed Auto Start is sometimes 1 in registry
    $delayedAuto = $false
    if ($s.DelayedAutoStart -ne $null) {
        $delayedAuto = [bool]$s.DelayedAutoStart
    } elseif ($reg.DelayedAutostart -eq 1) {
        $delayedAuto = $true
    }

    # Trigger Start is indicated by the presence of a TriggerInfo subkey
    # We avoid querying every subkey by checking if it was collected, but Get-ItemProperty doesn't do recursive.
    # Instead, we just check if TriggerInfo key exists. This is slightly slow but acceptable for just services with trigger.
    # Actually, to be very fast, we can just test path.
    $triggerStart = Test-Path "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\$name\\TriggerInfo" -ErrorAction SilentlyContinue

    $results += @{
        name = $name
        display_name = $s.DisplayName
        description = $s.Description
        status = $s.State
        startup_type = $s.StartMode
        service_type = $s.ServiceType
        binary_path = $s.PathName
        service_account = $s.StartName
        delayed_auto_start = $delayedAuto
        process_id = $s.ProcessId
        dependencies = $deps
        dependent_services = @() # Dependent services are calculated in Python for speed
        accept_stop = $s.AcceptStop
        accept_pause = $s.AcceptPause
        exit_code = $s.ExitCode
        error_control = $s.ErrorControl
        tag_id = $s.TagId
        trigger_start = [bool]$triggerStart
    }
}

$results | ConvertTo-Json -Depth 5 -Compress
"""


def collect_services() -> ServicesInventoryRequest:
    """
    Executes the collection of Windows services.

    Returns
    -------
    ServicesInventoryRequest
        The complete, hashed payload.
    """
    log = logger.bind(component="collector", category="services")
    log.info("Starting windows services collection")

    raw_output = run_powershell(_PS_SCRIPT).strip()

    if not raw_output:
        log.warning("No output from PowerShell script")
        services_list = []
    else:
        try:
            services_list = json.loads(raw_output)
        except json.JSONDecodeError as e:
            log.error("Failed to parse services JSON", error=str(e), output=raw_output[:200])
            services_list = []

    # Ensure list
    if isinstance(services_list, dict):
        services_list = [services_list]

    payloads = []

    # Build reverse dependency map to calculate dependent_services
    # dependencies map: name -> list of dependencies
    dep_map = {}
    for svc in services_list:
        name = str(svc.get("name") or "").strip().lower()
        if not name:
            continue
        deps = svc.get("dependencies")
        if isinstance(deps, list):
            # registry can return strings containing groups like '+TDI' which we can keep as raw dependencies
            dep_map[name] = [str(d).strip().lower() for d in deps if d]

    # Calculate dependent_services (services that depend on THIS service)
    # dependent_map: name -> list of services that depend on it
    dependent_map = {}
    for svc_name, deps in dep_map.items():
        for dep in deps:
            if dep not in dependent_map:
                dependent_map[dep] = []
            dependent_map[dep].append(svc_name)

    for item in services_list:
        name = item.get("name")
        if not name:
            continue

        lower_name = str(name).strip().lower()

        deps = item.get("dependencies")
        if isinstance(deps, list):
            deps = [str(d) for d in deps if d]
        else:
            deps = []

        dependent_svcs = dependent_map.get(lower_name, [])

        payload = ServicePayload(
            name=name,
            display_name=item.get("display_name"),
            description=item.get("description"),
            status=item.get("status"),
            startup_type=item.get("startup_type"),
            service_type=item.get("service_type"),
            binary_path=item.get("binary_path"),
            service_account=item.get("service_account"),
            delayed_auto_start=item.get("delayed_auto_start"),
            process_id=item.get("process_id"),
            dependencies=deps if deps else None,
            dependent_services=dependent_svcs if dependent_svcs else None,
            accept_stop=item.get("accept_stop"),
            accept_pause=item.get("accept_pause"),
            can_shutdown=item.get("can_shutdown"),
            exit_code=item.get("exit_code"),
            service_flags=item.get("service_flags"),
            error_control=item.get("error_control"),
            load_order_group=item.get("load_order_group"),
            tag_id=item.get("tag_id"),
            trigger_start=item.get("trigger_start"),
        )
        payloads.append(payload)

    collected_at = datetime.now(timezone.utc)
    agent_version = agent_settings.agent_version

    request_obj = ServicesInventoryRequest(
        collected_at=collected_at,
        agent_version=agent_version,
        inventory_hash="",
        services=payloads,
    )

    final_hash = compute_inventory_hash(serialize_services(request_obj))
    request_obj.inventory_hash = final_hash

    log.info(
        "Finished windows services collection",
        service_count=len(payloads),
        inventory_hash=final_hash,
    )

    return request_obj
