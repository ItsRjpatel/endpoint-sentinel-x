import json
from datetime import datetime, timezone

import structlog

from config.settings import agent_settings
from models.inventory import SoftwareInventoryRequest, SoftwarePayload
from utils.powershell import run_powershell

logger = structlog.get_logger(__name__)

SOFTWARE_SCRIPT = """
$ErrorActionPreference = "SilentlyContinue"

$software = @()

# Helpers
function Get-PropertyString($obj, $prop) {
    if ($null -ne $obj.$prop) {
        return [string]$obj.$prop
    }
    return $null
}

function Get-PropertyInt($obj, $prop) {
    if ($null -ne $obj.$prop) {
        $val = $obj.$prop
        if ($val -is [int] -or $val -is [int32] -or $val -is [int64]) {
            return $val
        }
        if ([int32]::TryParse($val, [ref]$null)) {
            return [int32]$val
        }
    }
    return $null
}

# 1. HKLM x64
$hklm64 = Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* `
    -ErrorAction SilentlyContinue | Select-Object *
if ($hklm64) {
    foreach ($item in $hklm64) {
        if ([string]::IsNullOrWhiteSpace($item.DisplayName)) { continue }
        $obj = @{
            name = Get-PropertyString $item "DisplayName"
            version = Get-PropertyString $item "DisplayVersion"
            publisher = Get-PropertyString $item "Publisher"
            install_date = Get-PropertyString $item "InstallDate"
            install_location = Get-PropertyString $item "InstallLocation"
            install_source = Get-PropertyString $item "InstallSource"
            estimated_size_bytes = Get-PropertyInt $item "EstimatedSize"
            uninstall_string = Get-PropertyString $item "UninstallString"
            quiet_uninstall_string = Get-PropertyString $item "QuietUninstallString"
            install_scope = "Machine"
            architecture = "x64"
            product_code = $null
            help_link = Get-PropertyString $item "HelpLink"
            url_info_about = Get-PropertyString $item "URLInfoAbout"
            url_update_info = Get-PropertyString $item "URLUpdateInfo"
            display_icon = Get-PropertyString $item "DisplayIcon"
            language = Get-PropertyString $item "Language"
            release_type = Get-PropertyString $item "ReleaseType"
            parent_application = Get-PropertyString $item "ParentKeyName"
            parent_version = $null
            system_component = if ($item.SystemComponent -eq 1) { $true } else { $false }
            windows_installer = if ($item.WindowsInstaller -eq 1) { $true } else { $false }
            no_remove = if ($item.NoRemove -eq 1) { $true } else { $false }
            no_modify = if ($item.NoModify -eq 1) { $true } else { $false }
            no_repair = if ($item.NoRepair -eq 1) { $true } else { $false }
        }
        if ($item.PSChildName -match "^\\{.*\\}$") {
            $obj.product_code = $item.PSChildName
        }
        if ($obj.estimated_size_bytes -gt 0) {
            $obj.estimated_size_bytes = $obj.estimated_size_bytes * 1024
        }
        $software += $obj
    }
}

# 2. HKLM x86
$path32 = "HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*"
$hklm32 = Get-ItemProperty $path32 -ErrorAction SilentlyContinue | Select-Object *
if ($hklm32) {
    foreach ($item in $hklm32) {
        if ([string]::IsNullOrWhiteSpace($item.DisplayName)) { continue }
        $obj = @{
            name = Get-PropertyString $item "DisplayName"
            version = Get-PropertyString $item "DisplayVersion"
            publisher = Get-PropertyString $item "Publisher"
            install_date = Get-PropertyString $item "InstallDate"
            install_location = Get-PropertyString $item "InstallLocation"
            install_source = Get-PropertyString $item "InstallSource"
            estimated_size_bytes = Get-PropertyInt $item "EstimatedSize"
            uninstall_string = Get-PropertyString $item "UninstallString"
            quiet_uninstall_string = Get-PropertyString $item "QuietUninstallString"
            install_scope = "Machine"
            architecture = "x86"
            product_code = $null
            help_link = Get-PropertyString $item "HelpLink"
            url_info_about = Get-PropertyString $item "URLInfoAbout"
            url_update_info = Get-PropertyString $item "URLUpdateInfo"
            display_icon = Get-PropertyString $item "DisplayIcon"
            language = Get-PropertyString $item "Language"
            release_type = Get-PropertyString $item "ReleaseType"
            parent_application = Get-PropertyString $item "ParentKeyName"
            parent_version = $null
            system_component = if ($item.SystemComponent -eq 1) { $true } else { $false }
            windows_installer = if ($item.WindowsInstaller -eq 1) { $true } else { $false }
            no_remove = if ($item.NoRemove -eq 1) { $true } else { $false }
            no_modify = if ($item.NoModify -eq 1) { $true } else { $false }
            no_repair = if ($item.NoRepair -eq 1) { $true } else { $false }
        }
        if ($item.PSChildName -match "^\\{.*\\}$") {
            $obj.product_code = $item.PSChildName
        }
        if ($obj.estimated_size_bytes -gt 0) {
            $obj.estimated_size_bytes = $obj.estimated_size_bytes * 1024
        }
        $software += $obj
    }
}

# 3. HKU (Users)
$userHives = Get-ChildItem Registry::HKEY_USERS -ErrorAction SilentlyContinue | `
    Where-Object { $_.Name -match "^HKEY_USERS\\\\S-1-5-21-.*$" -and $_.Name -notmatch "_Classes$" }
foreach ($hive in $userHives) {
    $path = "Registry::" + $hive.Name + `
        "\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*"
    $hku = Get-ItemProperty $path -ErrorAction SilentlyContinue | Select-Object *
    if ($hku) {
        foreach ($item in $hku) {
            if ([string]::IsNullOrWhiteSpace($item.DisplayName)) { continue }
            $obj = @{
                name = Get-PropertyString $item "DisplayName"
                version = Get-PropertyString $item "DisplayVersion"
                publisher = Get-PropertyString $item "Publisher"
                install_date = Get-PropertyString $item "InstallDate"
                install_location = Get-PropertyString $item "InstallLocation"
                install_source = Get-PropertyString $item "InstallSource"
                estimated_size_bytes = Get-PropertyInt $item "EstimatedSize"
                uninstall_string = Get-PropertyString $item "UninstallString"
                quiet_uninstall_string = Get-PropertyString $item "QuietUninstallString"
                install_scope = "User"
                architecture = "Unknown"
                product_code = $null
                help_link = Get-PropertyString $item "HelpLink"
                url_info_about = Get-PropertyString $item "URLInfoAbout"
                url_update_info = Get-PropertyString $item "URLUpdateInfo"
                display_icon = Get-PropertyString $item "DisplayIcon"
                language = Get-PropertyString $item "Language"
                release_type = Get-PropertyString $item "ReleaseType"
                parent_application = Get-PropertyString $item "ParentKeyName"
                parent_version = $null
                system_component = if ($item.SystemComponent -eq 1) { $true } else { $false }
                windows_installer = if ($item.WindowsInstaller -eq 1) { $true } else { $false }
                no_remove = if ($item.NoRemove -eq 1) { $true } else { $false }
                no_modify = if ($item.NoModify -eq 1) { $true } else { $false }
                no_repair = if ($item.NoRepair -eq 1) { $true } else { $false }
            }
            if ($item.PSChildName -match "^\\{.*\\}$") {
                $obj.product_code = $item.PSChildName
            }
            if ($obj.estimated_size_bytes -gt 0) {
                $obj.estimated_size_bytes = $obj.estimated_size_bytes * 1024
            }
            $software += $obj
        }
    }
}

# 4. Appx (AppxAllUserStore)
$basePath = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Appx\\AppxAllUserStore"
$appxPath = $basePath + "\\Applications\\*"
$appxItems = Get-ItemProperty $appxPath -ErrorAction SilentlyContinue | Select-Object *
if ($appxItems) {
    foreach ($item in $appxItems) {
        $parts = $item.PSChildName -split "_"
        if ($parts.Length -lt 2) { continue }
        $appName = $parts[0]
        $appVersion = $parts[1]
        $obj = @{
            name = $appName
            version = $appVersion
            publisher = $null
            install_date = $null
            install_location = Get-PropertyString $item "Path"
            install_source = "AppX"
            estimated_size_bytes = $null
            uninstall_string = $null
            quiet_uninstall_string = $null
            install_scope = "Machine"
            architecture = "AppX"
            product_code = $item.PSChildName
            help_link = $null
            url_info_about = $null
            url_update_info = $null
            display_icon = $null
            language = $null
            release_type = "AppX"
            parent_application = $null
            parent_version = $null
            system_component = $false
            windows_installer = $false
            no_remove = $false
            no_modify = $false
            no_repair = $false
        }
        $software += $obj
    }
}

$software | ConvertTo-Json -Depth 10 -Compress
"""


def collect_software() -> SoftwareInventoryRequest:
    """Collects installed software from the Windows endpoint."""
    logger.info("Starting software collection")
    output = run_powershell(SOFTWARE_SCRIPT)

    if not output.strip():
        logger.warning("Software script returned empty output")
        return SoftwareInventoryRequest(
            collected_at=datetime.now(timezone.utc),
            agent_version=agent_settings.agent_version,
            inventory_hash="empty",
            software=[],
        )

    try:
        raw_list = json.loads(output)
        if isinstance(raw_list, dict):
            raw_list = [raw_list]
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse software JSON: {e}")
        raw_list = []

    # Deduplication
    dedup = {}
    for item in raw_list:
        pub = str(item.get("publisher") or "").strip().lower()
        prod_code = str(item.get("product_code") or "").strip().lower()
        name = str(item.get("name") or "").strip().lower()
        ver = str(item.get("version") or "").strip().lower()
        arch = str(item.get("architecture") or "").strip().lower()
        scope = str(item.get("install_scope") or "").strip().lower()

        if prod_code:
            key = f"{pub}|{prod_code}"
        else:
            key = f"{pub}|{name}|{ver}|{arch}|{scope}"

        if key not in dedup:
            dedup[key] = SoftwarePayload(**item)

    payloads = list(dedup.values())

    collected_at = datetime.now(timezone.utc)
    agent_version = agent_settings.agent_version

    request_obj = SoftwareInventoryRequest(
        collected_at=collected_at,
        agent_version=agent_version,
        inventory_hash="",
        software=payloads,
    )

    from utils.hashing import compute_inventory_hash
    from utils.serialization import serialize_software

    final_hash = compute_inventory_hash(serialize_software(request_obj))
    request_obj.inventory_hash = final_hash
    return request_obj
