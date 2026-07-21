"""
Unit tests for the Local Users Inventory Collector.

All Windows API calls (run_powershell) are mocked so these tests run on any OS.
"""

import json
from datetime import datetime, timezone
from unittest.mock import patch

from collectors.local_users import _parse_user, collect_local_users
from models.inventory import LocalUsersInventoryRequest
from utils.serialization import serialize_local_users

# ---------------------------------------------------------------------------
# Shared helper data
# ---------------------------------------------------------------------------

_BASE_USER = {
    "sid": "S-1-5-21-1234567890-1234567890-1234567890-1001",
    "username": "testuser",
    "full_name": "Test User",
    "description": "A regular test account",
    "account_type": "LocalAccount",
    "is_enabled": True,
    "is_locked": False,
    "is_password_required": True,
    "is_password_change_allowed": True,
    "password_expires": True,
    "password_never_expires": False,
    "password_last_set": "2024-06-01T12:00:00+00:00",
    "last_logon": "2024-07-01T08:30:00+00:00",
    "last_logoff": None,
    "account_created": None,
    "account_expires": None,
    "bad_logon_count": 0,
    "home_directory": None,
    "profile_path": None,
    "script_path": None,
    "primary_group": None,
    "local_groups": ["Users"],
    "is_builtin_account": False,
    "is_administrator": False,
    "is_guest": False,
}

_ADMIN_USER = {
    **_BASE_USER,
    "sid": "S-1-5-21-1234567890-1234567890-1234567890-500",  # RID 500
    "username": "Administrator",
    "full_name": None,
    "description": "Built-in administrator account",
    "local_groups": ["Administrators"],
    "is_builtin_account": True,
    "is_administrator": True,
    "is_guest": False,
}

_GUEST_USER = {
    **_BASE_USER,
    "sid": "S-1-5-21-1234567890-1234567890-1234567890-501",  # RID 501
    "username": "Guest",
    "full_name": None,
    "description": "Built-in guest account",
    "is_enabled": False,
    "local_groups": ["Guests"],
    "is_builtin_account": True,
    "is_administrator": False,
    "is_guest": True,
}


# ---------------------------------------------------------------------------
# _parse_user unit tests
# ---------------------------------------------------------------------------


def test_parse_user_basic():
    u = _parse_user(_BASE_USER)
    assert u is not None
    assert u.sid == "S-1-5-21-1234567890-1234567890-1234567890-1001"
    assert u.username == "testuser"
    assert u.full_name == "Test User"
    assert u.is_enabled is True
    assert u.is_locked is False
    assert u.is_administrator is False
    assert u.local_groups == ["Users"]


def test_parse_user_builtin_administrator_rid500():
    """Built-in Admin identified by RID 500 — not by username."""
    u = _parse_user(_ADMIN_USER)
    assert u is not None
    assert u.is_builtin_account is True
    assert u.is_administrator is True
    assert u.is_guest is False


def test_parse_user_builtin_guest_rid501():
    """Built-in Guest identified by RID 501 — not by username."""
    u = _parse_user(_GUEST_USER)
    assert u is not None
    assert u.is_builtin_account is True
    assert u.is_guest is True
    assert u.is_administrator is False


def test_parse_user_renamed_administrator():
    """Renamed administrator account — still identified by RID 500."""
    renamed = {**_ADMIN_USER, "username": "CompanyAdmin"}
    u = _parse_user(renamed)
    assert u is not None
    assert u.username == "CompanyAdmin"
    assert u.is_builtin_account is True
    assert u.is_administrator is True


def test_parse_user_renamed_guest():
    """Renamed guest account — still identified by RID 501."""
    renamed = {**_GUEST_USER, "username": "ReadOnly"}
    u = _parse_user(renamed)
    assert u is not None
    assert u.username == "ReadOnly"
    assert u.is_builtin_account is True
    assert u.is_guest is True


def test_parse_user_disabled_account():
    raw = {**_BASE_USER, "is_enabled": False}
    u = _parse_user(raw)
    assert u is not None
    assert u.is_enabled is False


def test_parse_user_locked_account():
    raw = {**_BASE_USER, "is_locked": True}
    u = _parse_user(raw)
    assert u is not None
    assert u.is_locked is True


def test_parse_user_password_never_expires():
    raw = {**_BASE_USER, "password_never_expires": True, "password_expires": False}
    u = _parse_user(raw)
    assert u is not None
    assert u.password_never_expires is True
    assert u.password_expires is False


def test_parse_user_missing_description():
    raw = {**_BASE_USER, "description": None}
    u = _parse_user(raw)
    assert u is not None
    assert u.description is None


def test_parse_user_unicode_username():
    raw = {**_BASE_USER, "username": "Ünïcödé_Üser", "full_name": "Ünïcödé Ñamé"}
    u = _parse_user(raw)
    assert u is not None
    assert u.username == "Ünïcödé_Üser"
    assert u.full_name == "Ünïcödé Ñamé"


def test_parse_user_missing_last_logon():
    raw = {**_BASE_USER, "last_logon": None}
    u = _parse_user(raw)
    assert u is not None
    assert u.last_logon is None


def test_parse_user_sentinel_date_1601():
    """Windows sentinel date 1601-01-01 must be normalised to None."""
    raw = {**_BASE_USER, "last_logon": "1601-01-01T00:00:00+00:00"}
    u = _parse_user(raw)
    assert u is not None
    assert u.last_logon is None


def test_parse_user_sentinel_date_0001():
    """Sentinel date 0001-01-01 must be normalised to None."""
    raw = {**_BASE_USER, "password_last_set": "0001-01-01T00:00:00+00:00"}
    u = _parse_user(raw)
    assert u is not None
    assert u.password_last_set is None


def test_parse_user_valid_date_preserved():
    raw = {**_BASE_USER, "last_logon": "2024-07-01T08:30:00+00:00"}
    u = _parse_user(raw)
    assert u is not None
    assert u.last_logon is not None
    assert u.last_logon.year == 2024


def test_parse_user_empty_groups():
    raw = {**_BASE_USER, "local_groups": []}
    u = _parse_user(raw)
    assert u is not None
    assert u.local_groups == []


def test_parse_user_multiple_groups():
    raw = {**_BASE_USER, "local_groups": ["Users", "Remote Desktop Users", "Backup Operators"]}
    u = _parse_user(raw)
    assert u is not None
    assert len(u.local_groups) == 3
    assert "Remote Desktop Users" in u.local_groups


def test_parse_user_group_from_single_string():
    """When PowerShell returns a single string instead of list, handle it."""
    raw = {**_BASE_USER, "local_groups": "Users"}
    u = _parse_user(raw)
    assert u is not None
    assert "Users" in u.local_groups


def test_parse_user_returns_none_for_missing_sid():
    raw = {**_BASE_USER, "sid": None, "username": "baduser"}
    assert _parse_user(raw) is None


def test_parse_user_returns_none_for_missing_username():
    raw = {**_BASE_USER, "username": ""}
    assert _parse_user(raw) is None


# ---------------------------------------------------------------------------
# collect_local_users integration tests (mocked PowerShell)
# ---------------------------------------------------------------------------


def test_collect_local_users_empty_output():
    with patch("collectors.local_users.run_powershell", return_value=""):
        req = collect_local_users()
    assert isinstance(req, LocalUsersInventoryRequest)
    assert len(req.users) == 0
    assert len(req.inventory_hash) == 64


def test_collect_local_users_single_dict_output():
    """PowerShell may return a single JSON object (not array) if only one user."""
    with patch("collectors.local_users.run_powershell", return_value=json.dumps(_BASE_USER)):
        req = collect_local_users()
    assert len(req.users) == 1
    assert req.users[0].username == "testuser"


def test_collect_local_users_multiple_users():
    ps_out = json.dumps([_ADMIN_USER, _GUEST_USER, _BASE_USER])
    with patch("collectors.local_users.run_powershell", return_value=ps_out):
        req = collect_local_users()
    assert len(req.users) == 3
    sids = [u.sid for u in req.users]
    assert _ADMIN_USER["sid"] in sids
    assert _GUEST_USER["sid"] in sids


def test_collect_local_users_skips_invalid_entries():
    """Entries with no SID or username should be skipped without crashing."""
    bad_entry = {"sid": None, "username": None}
    ps_out = json.dumps([bad_entry, _BASE_USER])
    with patch("collectors.local_users.run_powershell", return_value=ps_out):
        req = collect_local_users()
    assert len(req.users) == 1


def test_collect_local_users_powershell_exception():
    """Collection must not raise even if PowerShell fails."""
    with patch("collectors.local_users.run_powershell", side_effect=RuntimeError("PS failed")):
        req = collect_local_users()
    assert isinstance(req, LocalUsersInventoryRequest)
    assert len(req.users) == 0


def test_collect_local_users_hash_is_64_chars():
    ps_out = json.dumps([_ADMIN_USER, _BASE_USER])
    with patch("collectors.local_users.run_powershell", return_value=ps_out):
        req = collect_local_users()
    assert len(req.inventory_hash) == 64


# ---------------------------------------------------------------------------
# serialize_local_users / hash stability tests
# ---------------------------------------------------------------------------


def _make_request(*raw_users) -> LocalUsersInventoryRequest:
    users = [_parse_user(r) for r in raw_users]
    users = [u for u in users if u is not None]
    return LocalUsersInventoryRequest(
        agent_version="1.0.0",
        collected_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        inventory_hash="placeholder",
        users=users,
    )


def test_serialize_sort_by_sid():
    """Users must be sorted by SID in the hash payload."""
    req = _make_request(_BASE_USER, _ADMIN_USER)  # BASE comes first alphabetically by SID?
    serialized = serialize_local_users(req)
    sids = [u["sid"] for u in serialized["users"]]
    assert sids == sorted(sids)


def test_serialize_groups_sorted_alphabetically():
    raw = {**_BASE_USER, "local_groups": ["Users", "Administrators", "Remote Desktop Users"]}
    req = _make_request(raw)
    serialized = serialize_local_users(req)
    groups = serialized["users"][0]["local_groups"]
    assert groups == sorted(groups)


def test_serialize_strings_lowercased_for_hash():
    """Serialized (hash) values must be lowercase; original payload retains case."""
    req = _make_request({**_BASE_USER, "full_name": "John DOE", "description": "Test ADMIN"})
    serialized = serialize_local_users(req)
    u = serialized["users"][0]
    assert u["full_name"] == "john doe"
    assert u["description"] == "test admin"
    # Original model keeps case
    assert req.users[0].full_name == "John DOE"


def test_serialize_sentinel_dates_become_null():
    """Sentinel dates must appear as None in serialized output."""
    raw = {
        **_BASE_USER,
        "last_logon": "1601-01-01T00:00:00+00:00",
        "password_last_set": "0001-01-01T00:00:00+00:00",
    }
    req = _make_request(raw)
    serialized = serialize_local_users(req)
    u = serialized["users"][0]
    assert u["last_logon"] is None
    assert u["password_last_set"] is None


def test_hash_stability_identical_inputs():
    """Identical payloads must produce identical hashes."""

    ps_out = json.dumps([_ADMIN_USER, _BASE_USER, _GUEST_USER])

    with patch("collectors.local_users.run_powershell", return_value=ps_out):
        req1 = collect_local_users()
    with patch("collectors.local_users.run_powershell", return_value=ps_out):
        req2 = collect_local_users()

    assert req1.inventory_hash == req2.inventory_hash


def test_hash_stability_reordered_users():
    """Hash must be identical regardless of user ordering in PS output."""

    ps_out_a = json.dumps([_BASE_USER, _ADMIN_USER])
    ps_out_b = json.dumps([_ADMIN_USER, _BASE_USER])

    with patch("collectors.local_users.run_powershell", return_value=ps_out_a):
        req_a = collect_local_users()
    with patch("collectors.local_users.run_powershell", return_value=ps_out_b):
        req_b = collect_local_users()

    assert req_a.inventory_hash == req_b.inventory_hash


def test_hash_stability_reordered_groups():
    """Hash must be identical regardless of group ordering in PS output."""
    from utils.hashing import compute_inventory_hash

    user_a = {**_BASE_USER, "local_groups": ["Users", "Remote Desktop Users"]}
    user_b = {**_BASE_USER, "local_groups": ["Remote Desktop Users", "Users"]}

    req_a = _make_request(user_a)
    req_b = _make_request(user_b)

    ser_a = serialize_local_users(req_a)
    ser_b = serialize_local_users(req_b)

    h_a = compute_inventory_hash(ser_a)
    h_b = compute_inventory_hash(ser_b)

    assert h_a == h_b


def test_hash_changes_on_user_change():
    """Different users must produce different hashes."""

    ps_out_a = json.dumps([_BASE_USER])
    ps_out_b = json.dumps([{**_BASE_USER, "is_enabled": False}])

    with patch("collectors.local_users.run_powershell", return_value=ps_out_a):
        req_a = collect_local_users()
    with patch("collectors.local_users.run_powershell", return_value=ps_out_b):
        req_b = collect_local_users()

    assert req_a.inventory_hash != req_b.inventory_hash
