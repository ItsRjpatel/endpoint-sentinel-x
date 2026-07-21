"""
Windows Local Users Inventory Collector
========================================

Collects all local user account metadata on a Windows endpoint using a two-pass
strategy:

1. **Primary pass** — ``Get-LocalUser`` (available on Windows 10 1607+ / Server 2016+)
   or ``Get-CimInstance Win32_UserAccount -Filter "LocalAccount=True"`` as fallback.
   Retrieves core account attributes: SID, name, status, dates, description, etc.

2. **Supplemental pass** — ADSI (``[ADSI]"WinNT://."`` provider) to enumerate group
   membership per user in a single batch.  Groups are resolved from the
   ``Administrators``, ``Users``, and every other local group on the machine.

Built-in account detection
--------------------------
Administrator and Guest are identified exclusively by their RID (last component of
the SID), not by username.  This correctly handles renamed built-in accounts:

  - RID 500 → is_builtin_account=True, is_guest=False
  - RID 501 → is_builtin_account=True, is_guest=True

Administrator flag
------------------
``is_administrator`` is derived from membership in the local ``Administrators``
group — never from the username or RID alone.

Security
--------
No password hashes, NTLM hashes, cached credentials, LSA secrets, or SAM data
are ever collected.  Metadata only.
"""

import json
from datetime import UTC, datetime

import structlog

from config.settings import agent_settings
from models.inventory import LocalUserPayload, LocalUsersInventoryRequest
from utils.hashing import compute_inventory_hash
from utils.powershell import run_powershell
from utils.serialization import serialize_local_users

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# PowerShell collection script
# ---------------------------------------------------------------------------
# The script runs a two-pass collection:
#   Pass 1 – Get-LocalUser (fallback to Win32_UserAccount via CIM).
#   Pass 2 – ADSI group enumeration; builds a map of SID → [group names].
# Output is a single JSON array.

_PS_SCRIPT = r"""
$ErrorActionPreference = 'SilentlyContinue'

# ---------------------------------------------------------------------------
# Helper: convert a FileTime / DateTime to ISO-8601 or $null
# ---------------------------------------------------------------------------
function ConvertTo-IsoOrNull {
    param($val)
    if ($null -eq $val) { return $null }
    try {
        $dt = [datetime]$val
        if ($dt.Year -le 1 -or $dt.Year -eq 1601) { return $null }
        return $dt.ToUniversalTime().ToString('o')
    } catch { return $null }
}

# ---------------------------------------------------------------------------
# Pass 2 – ADSI: build SID → groups map for every local group
# ---------------------------------------------------------------------------
$groupMap = @{}  # SID (string) -> [group names]

try {
    $computer = [ADSI]"WinNT://$($env:COMPUTERNAME),computer"
    $localGroups = @($computer.Children | Where-Object { $_.SchemaClassName -eq 'group' })

    foreach ($grp in $localGroups) {
        $grpName = $grp.Name.Value
        try {
            $members = @($grp.Invoke("Members"))
            foreach ($m in $members) {
                try {
                    $memberPath = $m.GetType().InvokeMember("ADsPath", "GetProperty", $null, $m, $null)
                    # Only include local machine members (not domain)
                    if ($memberPath -notlike "WinNT://$($env:COMPUTERNAME)/*") { continue }
                    $memberObj = [ADSI]$memberPath
                    if ($memberObj.SchemaClassName -ne 'User') { continue }
                    # Resolve SID
                    $sidBytes = $memberObj.objectSid.Value
                    if ($null -eq $sidBytes) { continue }
                    $sid = (New-Object System.Security.Principal.SecurityIdentifier($sidBytes, 0)).Value
                    if (-not $groupMap.ContainsKey($sid)) { $groupMap[$sid] = [System.Collections.Generic.List[string]]::new() }
                    $groupMap[$sid].Add($grpName)
                } catch { continue }
            }
        } catch { continue }
    }
} catch { <# ADSI not available; groups will be empty #> }

# ---------------------------------------------------------------------------
# Pass 1 – Get-LocalUser (preferred) or Win32_UserAccount (fallback)
# ---------------------------------------------------------------------------
$users = $null
$useLocalUser = $false

try {
    $users = @(Get-LocalUser -ErrorAction Stop)
    $useLocalUser = $true
} catch {
    $users = @(Get-CimInstance -ClassName Win32_UserAccount -Filter "LocalAccount=True" -ErrorAction SilentlyContinue)
}

$results = [System.Collections.Generic.List[object]]::new()

foreach ($u in $users) {
    try {
        # ---- SID ----
        if ($useLocalUser) {
            $sidStr = $u.SID.Value
        } else {
            $sidStr = $u.SID
        }
        if ([string]::IsNullOrEmpty($sidStr)) { continue }

        # ---- RID for built-in detection ----
        $ridParts = $sidStr -split '-'
        $rid = [int]$ridParts[-1]
        $isBuiltin = ($rid -eq 500 -or $rid -eq 501)
        $isGuest   = ($rid -eq 501)

        # ---- Groups from ADSI map ----
        $groups = @()
        if ($groupMap.ContainsKey($sidStr)) {
            $groups = @($groupMap[$sidStr])
        }
        $isAdmin = ($groups -contains 'Administrators')

        # ---- Attributes differ between Get-LocalUser and Win32_UserAccount ----
        if ($useLocalUser) {
            $enabled            = [bool]$u.Enabled
            $locked             = [bool]$u.UserMayNotChangePassword -eq $false -and $false  # LockedOut via Get-LocalUser
            try { $locked = [bool]$u.LockedOut } catch { $locked = $null }
            $pwdRequired        = -not [bool]$u.PasswordNotRequired
            $pwdChangeAllowed   = -not [bool]$u.UserMayNotChangePassword
            $pwdNeverExpires    = [bool]$u.PasswordNeverExpires
            $pwdExpires         = -not $pwdNeverExpires
            $pwdLastSet         = ConvertTo-IsoOrNull $u.PasswordLastSet
            $lastLogon          = ConvertTo-IsoOrNull $u.LastLogon
            $accountExpires     = ConvertTo-IsoOrNull $u.AccountExpires
            $accountCreated     = $null   # Not exposed by Get-LocalUser
            $lastLogoff         = $null
            $badLogon           = $null
            $homeDir            = $null
            $profilePath        = $null
            $scriptPath         = $null
            $primaryGroup       = $null
            $fullName           = if ($u.FullName) { $u.FullName } else { $null }
            $description        = if ($u.Description) { $u.Description } else { $null }
            $accountType        = "LocalAccount"
        } else {
            # Win32_UserAccount
            $enabled            = -not [bool]$u.Disabled
            $locked             = [bool]$u.Lockout
            $pwdRequired        = [bool]$u.PasswordRequired
            $pwdChangeAllowed   = [bool]$u.PasswordChangeable
            $pwdNeverExpires    = [bool]$u.PasswordExpires -eq $false
            $pwdExpires         = [bool]$u.PasswordExpires
            $pwdLastSet         = $null
            $lastLogon          = $null
            $accountExpires     = $null
            $accountCreated     = $null
            $lastLogoff         = $null
            $badLogon           = $null
            $homeDir            = $null
            $profilePath        = $null
            $scriptPath         = $null
            $primaryGroup       = $null
            $fullName           = if ($u.FullName) { $u.FullName } else { $null }
            $description        = if ($u.Description) { $u.Description } else { $null }
            $accountType        = $u.AccountType
        }

        $results.Add([PSCustomObject]@{
            sid                     = $sidStr
            username                = $u.Name
            full_name               = $fullName
            description             = $description
            account_type            = $accountType
            is_enabled              = $enabled
            is_locked               = $locked
            is_password_required    = $pwdRequired
            is_password_change_allowed = $pwdChangeAllowed
            password_expires        = $pwdExpires
            password_never_expires  = $pwdNeverExpires
            password_last_set       = $pwdLastSet
            last_logon              = $lastLogon
            last_logoff             = $lastLogoff
            account_created         = $accountCreated
            account_expires         = $accountExpires
            bad_logon_count         = $badLogon
            home_directory          = $homeDir
            profile_path            = $profilePath
            script_path             = $scriptPath
            primary_group           = $primaryGroup
            local_groups            = $groups
            is_builtin_account      = $isBuiltin
            is_administrator        = $isAdmin
            is_guest                = $isGuest
        })
    } catch { continue }
}

$results | ConvertTo-Json -Depth 5 -Compress
"""


def _parse_user(raw: dict) -> LocalUserPayload | None:
    """Parse a single raw PowerShell result dict into a ``LocalUserPayload``."""
    sid = (raw.get("sid") or "").strip()
    username = (raw.get("username") or "").strip()
    if not sid or not username:
        return None

    def _str(key: str) -> str | None:
        v = raw.get(key)
        return str(v).strip() or None if v else None

    def _bool(key: str) -> bool | None:
        v = raw.get(key)
        if v is None:
            return None
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)

    def _int(key: str) -> int | None:
        v = raw.get(key)
        try:
            return int(v) if v is not None else None
        except (ValueError, TypeError):
            return None

    def _dt(key: str) -> datetime | None:
        v = raw.get(key)
        if not v:
            return None
        try:
            dt = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
            # Reject Windows sentinel years
            if dt.year <= 1 or dt.year == 1601:
                return None
            return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
        except (ValueError, AttributeError):
            return None

    def _groups(key: str) -> list[str]:
        v = raw.get(key)
        if not v:
            return []
        if isinstance(v, list):
            return [str(g).strip() for g in v if g]
        return [str(v).strip()] if str(v).strip() else []

    return LocalUserPayload(
        sid=sid,
        username=username,
        full_name=_str("full_name"),
        description=_str("description"),
        account_type=_str("account_type"),
        is_enabled=_bool("is_enabled"),
        is_locked=_bool("is_locked"),
        is_password_required=_bool("is_password_required"),
        is_password_change_allowed=_bool("is_password_change_allowed"),
        password_expires=_bool("password_expires"),
        password_never_expires=_bool("password_never_expires"),
        password_last_set=_dt("password_last_set"),
        last_logon=_dt("last_logon"),
        last_logoff=_dt("last_logoff"),
        account_created=_dt("account_created"),
        account_expires=_dt("account_expires"),
        bad_logon_count=_int("bad_logon_count"),
        home_directory=_str("home_directory"),
        profile_path=_str("profile_path"),
        script_path=_str("script_path"),
        primary_group=_str("primary_group"),
        local_groups=_groups("local_groups"),
        is_builtin_account=_bool("is_builtin_account"),
        is_administrator=_bool("is_administrator"),
        is_guest=_bool("is_guest"),
    )


def collect_local_users() -> LocalUsersInventoryRequest:
    """
    Execute the PowerShell collection script and return a fully-hashed
    ``LocalUsersInventoryRequest`` ready for upload.

    Fault-tolerant: per-user parse failures are skipped; the function always
    returns a valid (possibly empty) request.
    """
    log = logger.bind(component="collector", category="local-users")
    log.info("Local users inventory collection started")

    users: list[LocalUserPayload] = []

    try:
        raw_output = run_powershell(_PS_SCRIPT)

        if raw_output and raw_output.strip():
            data = json.loads(raw_output)
            if isinstance(data, dict):
                data = [data]

            for entry in data:
                try:
                    payload = _parse_user(entry)
                    if payload:
                        users.append(payload)
                except Exception as exc:
                    log.warning(
                        "Skipping user due to parse error",
                        error=str(exc),
                        raw=entry.get("username") or entry.get("sid"),
                    )

        log.info(
            "Local users collection summary",
            total=len(users),
            enabled=sum(1 for u in users if u.is_enabled),
            disabled=sum(1 for u in users if u.is_enabled is False),
            administrators=sum(1 for u in users if u.is_administrator),
            guests=sum(1 for u in users if u.is_guest),
        )

    except Exception as exc:
        log.error("Local users collection failed", error=str(exc))

    cfg = agent_settings
    collected_at = datetime.now(UTC)

    request = LocalUsersInventoryRequest(
        agent_version=cfg.agent_version,
        collected_at=collected_at,
        inventory_hash="",
        users=users,
    )

    serialized = serialize_local_users(request)
    inventory_hash = compute_inventory_hash(serialized)
    request.inventory_hash = inventory_hash

    log.info(
        "Local users inventory serialized",
        user_count=len(users),
        inventory_hash=inventory_hash,
    )

    return request
