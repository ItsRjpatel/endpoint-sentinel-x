import json
from datetime import datetime, timezone

import structlog

from config.settings import agent_settings
from models.inventory import WindowsUpdatePayload, WindowsUpdatesInventoryRequest
from utils.hashing import compute_inventory_hash
from utils.powershell import run_powershell
from utils.serialization import serialize_windows_updates

logger = structlog.get_logger(__name__)

WINDOWS_UPDATES_SCRIPT = """
$ErrorActionPreference = "SilentlyContinue"

# 1. Primary Source: Windows Update COM Object
$wuItems = @()
try {
    $Session = New-Object -ComObject "Microsoft.Update.Session" -ErrorAction Stop
    $Searcher = $Session.CreateUpdateSearcher()
    $historyCount = $Searcher.GetTotalHistoryCount()
    if ($historyCount -gt 0) {
        $History = $Searcher.QueryHistory(0, $historyCount)
        foreach ($h in $History) {
            # Operation 1 = Installation
            $state = "Unknown"
            if ($h.ResultCode -eq 2) { $state = "Installed" }
            elseif ($h.ResultCode -eq 3) { $state = "Failed" }
            elseif ($h.ResultCode -eq 4) { $state = "Aborted" }

            $cat = if ($h.Categories) { ($h.Categories | ForEach-Object { $_.Name }) -join ", " } else { $null }  # noqa: E501

            $wuItems += @{
                source = "WUAPI"
                title = $h.Title
                description = $h.Description
                update_id = $h.UpdateIdentity.UpdateID
                revision_number = $h.UpdateIdentity.RevisionNumber
                installed_on = if ($h.Date) { $h.Date.ToString("o") } else { $null }
                installation_state = $state
                support_url = $h.SupportUrl
                # WUAPI returns categories as a collection
                classification = $cat
            }
        }
    }
} catch {
    # Ignore COM errors
}

# 2. Secondary Source: Win32_QuickFixEngineering
$wmiItems = @()
$qfe = Get-WmiObject -Class Win32_QuickFixEngineering -ErrorAction SilentlyContinue
if ($qfe) {
    foreach ($item in $qfe) {
        $wmiItems += @{
            source = "WMI"
            hotfix_id = $item.HotFixID
            title = $item.Description
            installed_by = $item.InstalledBy
            installed_on = $item.InstalledOn
            installation_state = "Installed"
        }
    }
}

$result = @{
    wuapi = $wuItems
    wmi = $wmiItems
}
$result | ConvertTo-Json -Depth 5 -Compress
"""


def _extract_kb(title: str, hotfix_id: str) -> str:
    if hotfix_id and hotfix_id.upper().startswith("KB"):
        return hotfix_id.upper()
    import re

    if title:
        match = re.search(r"(KB\d+)", title, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return ""


def collect_windows_updates() -> WindowsUpdatesInventoryRequest:
    """Collects installed Windows Updates from the endpoint."""
    logger.info("Starting windows updates collection")
    output = run_powershell(WINDOWS_UPDATES_SCRIPT)

    if not output.strip():
        return WindowsUpdatesInventoryRequest(
            collected_at=datetime.now(timezone.utc),
            agent_version=agent_settings.agent_version,
            inventory_hash="empty",
            updates=[],
        )

    try:
        raw_data = json.loads(output)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse windows updates JSON: {e}")
        raw_data = {"wuapi": [], "wmi": []}

    wuapi = raw_data.get("wuapi", []) or []
    wmi = raw_data.get("wmi", []) or []

    if isinstance(wuapi, dict):
        wuapi = [wuapi]
    if isinstance(wmi, dict):
        wmi = [wmi]

    # Deduplication map
    dedup = {}

    def _add_item(item, source="WUAPI"):
        uid = str(item.get("update_id") or "").strip().lower()
        rev = str(item.get("revision_number") or "").strip().lower()
        title = str(item.get("title") or "").strip()
        desc = str(item.get("description") or "").strip()
        installed_on = item.get("installed_on")
        parsed_date = None
        if installed_on:
            if isinstance(installed_on, dict):
                installed_on = installed_on.get("value", "")
            installed_on = str(installed_on).strip()
            
            if installed_on and not installed_on.startswith("/Date("):
                try:
                    if "T" in installed_on:
                        parsed_date = installed_on
                    else:
                        dt = datetime.strptime(installed_on.split(" ")[0], "%m/%d/%Y")
                        parsed_date = dt.isoformat()
                except Exception:
                    parsed_date = None
                    
        installed_on = parsed_date

        hotfix_id = str(item.get("hotfix_id") or "").strip().upper()
        extracted_kb = _extract_kb(title, hotfix_id)
        if extracted_kb:
            hotfix_id = extracted_kb

        pkg = str(item.get("package_identity") or "").strip().lower()

        # Keys in precedence: Update GUID+Revision, Package Identity, KB+Revision, KB+Title
        keys = []
        if uid:
            keys.append(f"uid|{uid}|{rev}")
        if pkg:
            keys.append(f"pkg|{pkg}")
        if hotfix_id:
            keys.append(f"kb_only|{hotfix_id}")
            keys.append(f"kb|{hotfix_id}|{rev}")
            keys.append(f"kb_title|{hotfix_id}|{title.lower()}")

        # If we have no keys, just use title to avoid dropping it
        if not keys and title:
            keys.append(f"title|{title.lower()}")

        # Check if already processed
        for k in keys:
            if k in dedup:
                return  # Already exists with higher precedence (WUAPI is parsed first)

        classification = str(item.get("classification") or "")

        is_security = "security" in classification.lower() or "security" in title.lower()
        is_critical = "critical" in classification.lower() or "critical" in title.lower()
        is_cumulative = "cumulative" in classification.lower() or "cumulative" in title.lower()
        is_driver = "driver" in classification.lower() or "driver" in title.lower()
        is_feature = "feature" in classification.lower() or "feature" in title.lower()
        is_preview = "preview" in classification.lower() or "preview" in title.lower()
        is_ssu = "servicing stack" in classification.lower() or "servicing stack" in title.lower()

        payload = WindowsUpdatePayload(
            hotfix_id=hotfix_id or None,
            title=title or None,
            description=desc or None,
            classification=classification or None,
            installed_by=item.get("installed_by"),
            installed_on=installed_on if installed_on else None,
            installation_state=item.get("installation_state"),
            support_url=item.get("support_url"),
            update_id=item.get("update_id"),
            revision_number=item.get("revision_number"),
            deployment_source=item.get("deployment_source"),
            package_identity=item.get("package_identity"),
            is_security_update=is_security,
            is_critical_update=is_critical,
            is_cumulative_update=is_cumulative,
            is_driver_update=is_driver,
            is_feature_update=is_feature,
            is_preview_update=is_preview,
            is_servicing_stack_update=is_ssu,
        )

        for k in keys:
            dedup[k] = payload

    # Process WUAPI first (higher fidelity)
    for item in wuapi:
        _add_item(item, source="WUAPI")

    # Process WMI as fallback
    for item in wmi:
        _add_item(item, source="WMI")

    # Unique payloads
    unique_payloads = list({id(p): p for p in dedup.values()}.values())

    collected_at = datetime.now(timezone.utc)
    agent_version = agent_settings.agent_version

    request_obj = WindowsUpdatesInventoryRequest(
        collected_at=collected_at,
        agent_version=agent_version,
        inventory_hash="",
        updates=unique_payloads,
    )

    final_hash = compute_inventory_hash(serialize_windows_updates(request_obj))
    request_obj.inventory_hash = final_hash
    return request_obj
