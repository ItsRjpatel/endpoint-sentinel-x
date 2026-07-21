import json
import re
from datetime import datetime, timezone
from typing import Any

import structlog

from models.inventory import (
    BitLockerVolumeInventory,
    DefenderInventory,
    FirewallProfileInventory,
    SecureBootInventory,
    SecurityCenterInventory,
    SecurityInventory,
    TPMInventory,
    UACInventory,
)
from utils.powershell import run_powershell

logger = structlog.get_logger(__name__)


def _is_admin() -> bool:
    """Check if the current process has Administrator privileges."""
    script = (
        "$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent());"  # noqa: E501
        "$currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)"
    )
    result = run_powershell(script)
    return bool(result and "True" in result)


def _parse_ps_date(date_str: Any) -> datetime | None:
    if not date_str:
        return None

    if isinstance(date_str, str):
        # Handle PowerShell JSON dates like "\/Date(1721532000000)\/"
        match = re.search(r"\\/Date\((\d+)\)\\/", date_str)
        if match:
            timestamp = int(match.group(1)) / 1000.0
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)

        # Or standard ISO strings if PowerShell 7 outputs them
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            pass
    return None


def _get_defender() -> DefenderInventory | None:
    try:
        script = (
            "Get-MpComputerStatus -ErrorAction SilentlyContinue | "
            "Select-Object AMServiceEnabled, AntivirusEnabled, RealTimeProtectionEnabled, "
            "AMProductVersion, AMEngineVersion, AntivirusSignatureLastUpdated, "
            "QuickScanEndTime, FullScanEndTime, AntispywareEnabled, NISEnabled, "
            "IoavProtectionEnabled, BehaviorMonitorEnabled, IsTamperProtected | "
            "ConvertTo-Json -Compress"
        )
        result = run_powershell(script)
        if not result:
            return DefenderInventory(installed=False)

        data = json.loads(result)
        if not data:
            return DefenderInventory(installed=False)

        return DefenderInventory(
            installed=True,
            enabled=bool(data.get("AMServiceEnabled")),
            real_time_protection=bool(data.get("RealTimeProtectionEnabled")),
            antivirus_signature_version=data.get("AMProductVersion"),
            engine_version=data.get("AMEngineVersion"),
            last_signature_update=_parse_ps_date(data.get("AntivirusSignatureLastUpdated")),
            last_quick_scan=_parse_ps_date(data.get("QuickScanEndTime")),
            last_full_scan=_parse_ps_date(data.get("FullScanEndTime")),
            antivirus_enabled=bool(data.get("AntivirusEnabled")),
            antispyware_enabled=bool(data.get("AntispywareEnabled")),
            nis_enabled=bool(data.get("NISEnabled")),
            ioav_protection=bool(data.get("IoavProtectionEnabled")),
            behavior_monitoring=bool(data.get("BehaviorMonitorEnabled")),
            tamper_protection=bool(data.get("IsTamperProtected")),
        )
    except Exception:
        logger.warning("Failed to collect Defender inventory", exc_info=True)
        return None


def _get_tpm(is_admin: bool) -> TPMInventory | None:
    if not is_admin:
        return None
    try:
        script = (
            "Get-Tpm -ErrorAction SilentlyContinue | "
            "Select-Object TpmPresent, TpmReady, TpmEnabled, TpmActivated, "
            "ManufacturerId, ManufacturerVersion, SpecVersion, ManagedAuthLevel | "
            "ConvertTo-Json -Compress"
        )
        result = run_powershell(script)
        if not result:
            return None

        data = json.loads(result)
        return TPMInventory(
            present=bool(data.get("TpmPresent")),
            ready=bool(data.get("TpmReady")),
            enabled=bool(data.get("TpmEnabled")),
            activated=bool(data.get("TpmActivated")),
            manufacturer=str(data.get("ManufacturerId")) if data.get("ManufacturerId") else None,
            manufacturer_version=str(data.get("ManufacturerVersion"))
            if data.get("ManufacturerVersion")
            else None,
            specification_version=str(data.get("SpecVersion")) if data.get("SpecVersion") else None,
            managed_authentication_level=str(data.get("ManagedAuthLevel"))
            if data.get("ManagedAuthLevel") is not None
            else None,
        )
    except Exception:
        logger.warning("Failed to collect TPM inventory", exc_info=True)
        return None


def _get_secure_boot(is_admin: bool) -> SecureBootInventory | None:
    if not is_admin:
        return None
    try:
        # Confirm-SecureBootUEFI throws an error if not supported, or returns True/False
        script = (
            "try { $val = Confirm-SecureBootUEFI -ErrorAction Stop; "
            'Write-Output "{\\`"supported\\`": true, \\`"enabled\\`": '
            "$(if($val){'true'}else{'false'})}\" } "
            'catch { Write-Output "{\\`"supported\\`": false, \\`"enabled\\`": false}" }'
        )
        result = run_powershell(script)
        if not result:
            return None
        data = json.loads(result)
        return SecureBootInventory(
            supported=bool(data.get("supported")),
            enabled=bool(data.get("enabled")),
        )
    except Exception:
        logger.warning("Failed to collect Secure Boot inventory", exc_info=True)
        return None


def _get_uac() -> UACInventory | None:
    try:
        script = (
            "$path = 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System';"
            "@{ enabled = [bool](Get-ItemPropertyValue -Path $path -Name EnableLUA "
            "-ErrorAction SilentlyContinue);"
            "consent = (Get-ItemPropertyValue -Path $path -Name ConsentPromptBehaviorAdmin "
            "-ErrorAction SilentlyContinue) } | "
            "ConvertTo-Json -Compress"
        )
        result = run_powershell(script)
        if not result:
            return None
        data = json.loads(result)
        consent = data.get("consent")
        return UACInventory(
            enabled=bool(data.get("enabled")),
            consent_prompt_behavior=str(consent) if consent is not None else None,
        )
    except Exception:
        logger.warning("Failed to collect UAC inventory", exc_info=True)
        return None


def _get_security_center() -> SecurityCenterInventory | None:
    try:
        # Requires WMI root\SecurityCenter2. This works without admin in many cases.
        script = (
            "$av = Get-CimInstance -Namespace root\\SecurityCenter2 -ClassName AntiVirusProduct "
            "-ErrorAction SilentlyContinue | Select -ExpandProperty displayName -First 1;"
            "$fw = Get-CimInstance -Namespace root\\SecurityCenter2 -ClassName FirewallProduct "
            "-ErrorAction SilentlyContinue | Select -ExpandProperty displayName -First 1;"
            "$as = Get-CimInstance -Namespace root\\SecurityCenter2 -ClassName AntiSpywareProduct "
            "-ErrorAction SilentlyContinue | Select -ExpandProperty displayName -First 1;"
            "$ps = Get-CimInstance -Namespace root\\SecurityCenter2 -ClassName AntiVirusProduct "
            "-ErrorAction SilentlyContinue | Select -ExpandProperty productState -First 1;"
            "@{ av = $av; fw = $fw; as = $as; ps = $ps } | ConvertTo-Json -Compress"
        )
        result = run_powershell(script)
        if not result:
            return None
        data = json.loads(result)
        return SecurityCenterInventory(
            status="Active" if data.get("av") or data.get("fw") else "Unknown",
            registered_antivirus=data.get("av"),
            registered_firewall=data.get("fw"),
            registered_antispyware=data.get("as"),
            product_state=int(data["ps"]) if data.get("ps") is not None else None,
        )
    except Exception:
        logger.warning("Failed to collect Security Center inventory", exc_info=True)
        return None


def _get_bitlocker_volumes(is_admin: bool) -> list[BitLockerVolumeInventory]:
    if not is_admin:
        return []
    try:
        script = (
            "Get-BitLockerVolume -ErrorAction SilentlyContinue | "
            "Select-Object MountPoint, VolumeType, ProtectionStatus, EncryptionPercentage, "
            "EncryptionMethod, LockStatus, AutoUnlockEnabled, "
            "@{Name='KeyProtectorCount';Expression={$_.KeyProtector.Count}} | "
            "ConvertTo-Json -AsArray -Compress"
        )
        result = run_powershell(script)
        if not result:
            return []
        data = json.loads(result)
        volumes = []
        for vol in data:
            # Enums are returned as integers in PowerShell 5.1 ConvertTo-Json by default,
            # or strings depending on exact formatting. We cast to string for safety.
            volumes.append(
                BitLockerVolumeInventory(
                    drive_letter=str(vol.get("MountPoint", "Unknown")),
                    volume_type=str(vol.get("VolumeType"))
                    if vol.get("VolumeType") is not None
                    else None,
                    protection_status=str(vol.get("ProtectionStatus"))
                    if vol.get("ProtectionStatus") is not None
                    else None,
                    encryption_percentage=float(vol["EncryptionPercentage"])
                    if vol.get("EncryptionPercentage") is not None
                    else None,
                    encryption_method=str(vol.get("EncryptionMethod"))
                    if vol.get("EncryptionMethod") is not None
                    else None,
                    lock_status=str(vol.get("LockStatus"))
                    if vol.get("LockStatus") is not None
                    else None,
                    auto_unlock=bool(vol.get("AutoUnlockEnabled")),
                    key_protector_count=int(vol["KeyProtectorCount"])
                    if vol.get("KeyProtectorCount") is not None
                    else None,
                )
            )
        return volumes
    except Exception:
        logger.warning("Failed to collect BitLocker inventory", exc_info=True)
        return []


def _get_firewall_profiles() -> list[FirewallProfileInventory]:
    try:
        script = (
            "Get-NetFirewallProfile -ErrorAction SilentlyContinue | "
            "Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction | "
            "ConvertTo-Json -AsArray -Compress"
        )
        result = run_powershell(script)
        if not result:
            return []
        data = json.loads(result)
        profiles = []
        for prof in data:
            profiles.append(
                FirewallProfileInventory(
                    profile_name=str(prof.get("Name", "Unknown")),
                    enabled=prof.get("Enabled")
                    in (True, 1, "True", "true"),  # PowerShell enum casts
                    default_inbound_policy=str(prof.get("DefaultInboundAction"))
                    if prof.get("DefaultInboundAction") is not None
                    else None,
                    default_outbound_policy=str(prof.get("DefaultOutboundAction"))
                    if prof.get("DefaultOutboundAction") is not None
                    else None,
                )
            )
        return profiles
    except Exception:
        logger.warning("Failed to collect Firewall inventory", exc_info=True)
        return []


def collect() -> SecurityInventory:
    """Collect security inventory from the Windows endpoint."""
    logger.info("Starting security inventory collection")

    is_admin = _is_admin()
    if not is_admin:
        logger.warning(
            "Agent does not have Administrator privileges. Some security features (BitLocker, "
            "TPM, Secure Boot) will return safe defaults or None."
        )

    defender = _get_defender()
    tpm = _get_tpm(is_admin)
    secure_boot = _get_secure_boot(is_admin)
    uac = _get_uac()
    security_center = _get_security_center()
    bitlocker_volumes = _get_bitlocker_volumes(is_admin)
    firewall_profiles = _get_firewall_profiles()

    return SecurityInventory(
        defender=defender,
        tpm=tpm,
        secure_boot=secure_boot,
        uac=uac,
        security_center=security_center,
        bitlocker_volumes=bitlocker_volumes,
        firewall_profiles=firewall_profiles,
    )
