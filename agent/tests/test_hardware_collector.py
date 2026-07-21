"""
Unit tests for the hardware inventory collector.

All external I/O (psutil, subprocess/PowerShell) is mocked so these tests run
on any platform — no Windows or CIM required.

Test coverage
-------------
* All seven hardware fields are collected and returned in the model.
* Field types are correct (str, int, None as appropriate).
* The collector never raises even when all external calls fail.
* SHA-256 hash is stable for identical payloads.
* SHA-256 hash changes when payload data changes.
* JSON serialization produces JSON-safe primitives matching the expected schema shape.
"""

from unittest.mock import MagicMock, patch

import pytest

from collectors.hardware import collect
from models.inventory import HardwareInventory
from utils.hashing import compute_inventory_hash
from utils.serialization import serialize_hardware

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_psutil_mem():
    """Return a psutil virtual_memory-like object with a known total."""
    mem = MagicMock()
    mem.total = 17_179_869_184  # 16 GiB
    return mem


@pytest.fixture()
def healthy_inventory() -> HardwareInventory:
    """A fully-populated HardwareInventory for hash/serialization tests."""
    return HardwareInventory(
        cpu_model="Intel(R) Core(TM) i7-1185G7 @ 3.00GHz",
        cpu_cores=4,
        cpu_threads=8,
        total_ram_bytes=17_179_869_184,
        system_manufacturer="Dell Inc.",
        system_model="Latitude 7420",
        bios_version="1.23.0",
    )


# ---------------------------------------------------------------------------
# Hardware collection tests
# ---------------------------------------------------------------------------


class TestHardwareCollect:
    """Tests for the top-level collect() function."""

    def test_returns_hardware_inventory_instance(self):
        """collect() must always return a HardwareInventory, never a raw dict."""
        with (
            patch("collectors.hardware.run_powershell", return_value="Intel(R) Core i7"),
            patch("collectors.hardware._psutil") as mock_ps,
        ):
            mock_ps.cpu_count.side_effect = lambda logical=True: 8 if logical else 4
            mock_ps.virtual_memory.return_value = MagicMock(total=8_589_934_592)

            result = collect()

        assert isinstance(result, HardwareInventory)

    def test_all_required_fields_present(self):
        """All seven hardware fields must exist on the returned model."""
        with (
            patch("collectors.hardware.run_powershell", return_value="Test CPU"),
            patch("collectors.hardware._psutil") as mock_ps,
        ):
            mock_ps.cpu_count.side_effect = lambda logical=True: 4 if logical else 2
            mock_ps.virtual_memory.return_value = MagicMock(total=4_294_967_296)

            result = collect()

        assert hasattr(result, "cpu_model")
        assert hasattr(result, "cpu_cores")
        assert hasattr(result, "cpu_threads")
        assert hasattr(result, "total_ram_bytes")
        assert hasattr(result, "system_manufacturer")
        assert hasattr(result, "system_model")
        assert hasattr(result, "bios_version")

    def test_field_types_are_correct(self):
        """Required int fields must be int; string fields must be str or None."""
        with (
            patch("collectors.hardware.run_powershell", return_value="Dell Inc."),
            patch("collectors.hardware._psutil") as mock_ps,
        ):
            mock_ps.cpu_count.side_effect = lambda logical=True: 8 if logical else 4
            mock_ps.virtual_memory.return_value = MagicMock(total=17_179_869_184)

            result = collect()

        assert isinstance(result.cpu_model, str)
        assert isinstance(result.cpu_cores, int)
        assert isinstance(result.cpu_threads, int)
        assert isinstance(result.total_ram_bytes, int)
        # Optional fields are str or None
        assert result.system_manufacturer is None or isinstance(result.system_manufacturer, str)
        assert result.system_model is None or isinstance(result.system_model, str)
        assert result.bios_version is None or isinstance(result.bios_version, str)

    def test_powershell_values_are_populated(self):
        """CIM values returned by run_powershell must appear in the model."""
        expected_cpu = "Intel(R) Core(TM) i7-1185G7 @ 3.00GHz"

        ps_responses = {
            "(Get-CimInstance Win32_Processor).Name": expected_cpu,
            "(Get-CimInstance Win32_ComputerSystem).Manufacturer": "Dell Inc.",
            "(Get-CimInstance Win32_ComputerSystem).Model": "Latitude 7420",
            "(Get-CimInstance Win32_BIOS).SMBIOSBIOSVersion": "1.23.0",
        }

        with (
            patch(
                "collectors.hardware.run_powershell",
                side_effect=lambda cmd, **_: ps_responses.get(cmd),
            ),
            patch("collectors.hardware._psutil") as mock_ps,
        ):
            mock_ps.cpu_count.side_effect = lambda logical=True: 8 if logical else 4
            mock_ps.virtual_memory.return_value = MagicMock(total=17_179_869_184)

            result = collect()

        assert result.cpu_model == expected_cpu
        assert result.system_manufacturer == "Dell Inc."
        assert result.system_model == "Latitude 7420"
        assert result.bios_version == "1.23.0"

    def test_psutil_values_are_populated(self):
        """psutil RAM and core counts must appear in the model."""
        with (
            patch("collectors.hardware.run_powershell", return_value=None),
            patch("collectors.hardware._psutil") as mock_ps,
        ):
            mock_ps.cpu_count.side_effect = lambda logical=True: 16 if logical else 8
            mock_ps.virtual_memory.return_value = MagicMock(total=34_359_738_368)

            result = collect()

        assert result.cpu_cores == 8
        assert result.cpu_threads == 16
        assert result.total_ram_bytes == 34_359_738_368


class TestHardwareCollectResiliency:
    """The collector must never raise, even under total failure conditions."""

    def test_never_raises_when_powershell_fails(self):
        """A crash in run_powershell must not propagate to the caller."""
        with (
            patch(
                "collectors.hardware.run_powershell",
                side_effect=RuntimeError("PowerShell exploded"),
            ),
            patch("collectors.hardware._psutil") as mock_ps,
        ):
            mock_ps.cpu_count.return_value = 4
            mock_ps.virtual_memory.return_value = MagicMock(total=8_589_934_592)

            result = collect()  # must not raise

        assert isinstance(result, HardwareInventory)

    def test_never_raises_when_psutil_fails(self):
        """A crash in psutil must not propagate to the caller."""
        with (
            patch("collectors.hardware.run_powershell", return_value="Test CPU"),
            patch("collectors.hardware._psutil") as mock_ps,
        ):
            mock_ps.cpu_count.side_effect = RuntimeError("psutil broken")
            mock_ps.virtual_memory.side_effect = RuntimeError("psutil broken")

            result = collect()  # must not raise

        assert isinstance(result, HardwareInventory)

    def test_never_raises_when_all_sources_fail(self):
        """The collector must return a HardwareInventory even with zero data."""
        with (
            patch(
                "collectors.hardware.run_powershell",
                side_effect=Exception("total failure"),
            ),
            patch("collectors.hardware._psutil") as mock_ps,
        ):
            mock_ps.cpu_count.side_effect = Exception("total failure")
            mock_ps.virtual_memory.side_effect = Exception("total failure")

            result = collect()  # must not raise

        assert isinstance(result, HardwareInventory)
        # Safe defaults
        assert result.cpu_model == "Unknown"
        assert result.cpu_cores == 0
        assert result.cpu_threads == 0
        assert result.total_ram_bytes == 0

    def test_partial_collection_succeeds(self):
        """When only some sources succeed the available data is captured."""
        with (
            patch("collectors.hardware.run_powershell", return_value=None),
            patch("collectors.hardware._psutil") as mock_ps,
        ):
            mock_ps.cpu_count.side_effect = lambda logical=True: 4 if logical else 2
            mock_ps.virtual_memory.return_value = MagicMock(total=8_589_934_592)

            result = collect()

        # psutil data present; CIM data absent (None)
        assert result.cpu_cores == 2
        assert result.cpu_threads == 4
        assert result.total_ram_bytes == 8_589_934_592
        assert result.system_manufacturer is None
        assert result.system_model is None
        assert result.bios_version is None


# ---------------------------------------------------------------------------
# Hash stability tests
# ---------------------------------------------------------------------------


class TestInventoryHash:
    """SHA-256 hash must be stable and sensitive to payload changes."""

    def test_hash_is_deterministic(self, healthy_inventory: HardwareInventory):
        """The same inventory must produce the same hash on every call."""
        payload = serialize_hardware(healthy_inventory)
        h1 = compute_inventory_hash(payload)
        h2 = compute_inventory_hash(payload)
        assert h1 == h2

    def test_hash_is_64_hex_chars(self, healthy_inventory: HardwareInventory):
        """SHA-256 hex digest must be exactly 64 lowercase hex characters."""
        payload = serialize_hardware(healthy_inventory)
        h = compute_inventory_hash(payload)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_hash_changes_when_cpu_model_changes(self, healthy_inventory: HardwareInventory):
        """A change in any field must produce a different hash."""
        payload_a = serialize_hardware(healthy_inventory)

        modified = healthy_inventory.model_copy(update={"cpu_model": "AMD Ryzen 9 5900X"})
        payload_b = serialize_hardware(modified)

        assert compute_inventory_hash(payload_a) != compute_inventory_hash(payload_b)

    def test_hash_changes_when_ram_changes(self, healthy_inventory: HardwareInventory):
        """RAM change must produce a different hash."""
        payload_a = serialize_hardware(healthy_inventory)

        modified = healthy_inventory.model_copy(update={"total_ram_bytes": 8_589_934_592})
        payload_b = serialize_hardware(modified)

        assert compute_inventory_hash(payload_a) != compute_inventory_hash(payload_b)

    def test_hash_changes_when_optional_field_changes(self, healthy_inventory: HardwareInventory):
        """A change in an optional field (None → value) must change the hash."""
        payload_a = serialize_hardware(healthy_inventory)

        modified = healthy_inventory.model_copy(update={"bios_version": "9.99.0"})
        payload_b = serialize_hardware(modified)

        assert compute_inventory_hash(payload_a) != compute_inventory_hash(payload_b)

    def test_hash_is_independent_of_dict_insertion_order(self):
        """Key ordering must not affect the hash (sort_keys=True)."""
        payload_a = {
            "cpu_model": "Intel i7",
            "cpu_cores": 4,
            "cpu_threads": 8,
            "total_ram_bytes": 8_589_934_592,
            "system_manufacturer": None,
            "system_model": None,
            "bios_version": None,
        }
        payload_b = {
            "total_ram_bytes": 8_589_934_592,
            "bios_version": None,
            "system_model": None,
            "cpu_threads": 8,
            "cpu_model": "Intel i7",
            "system_manufacturer": None,
            "cpu_cores": 4,
        }
        assert compute_inventory_hash(payload_a) == compute_inventory_hash(payload_b)


# ---------------------------------------------------------------------------
# Serialization tests
# ---------------------------------------------------------------------------


class TestHardwareSerialization:
    """serialize_hardware must produce a JSON-safe dict matching the schema."""

    def test_returns_dict(self, healthy_inventory: HardwareInventory):
        """serialize_hardware must return a plain dict."""
        result = serialize_hardware(healthy_inventory)
        assert isinstance(result, dict)

    def test_all_schema_keys_present(self, healthy_inventory: HardwareInventory):
        """All seven backend schema keys must be present in the output."""
        expected_keys = {
            "cpu_model",
            "cpu_cores",
            "cpu_threads",
            "total_ram_bytes",
            "system_manufacturer",
            "system_model",
            "bios_version",
        }
        result = serialize_hardware(healthy_inventory)
        assert expected_keys == set(result.keys())

    def test_values_are_json_primitives(self, healthy_inventory: HardwareInventory):
        """All values must be JSON-serializable primitives (no datetime, UUID, etc.)."""
        import json

        result = serialize_hardware(healthy_inventory)
        # Must not raise
        encoded = json.dumps(result)
        assert isinstance(encoded, str)

    def test_none_fields_serialized_as_null(self):
        """Optional fields with None must appear as None in the dict."""
        inv = HardwareInventory(
            cpu_model="Test CPU",
            cpu_cores=2,
            cpu_threads=4,
            total_ram_bytes=4_294_967_296,
            system_manufacturer=None,
            system_model=None,
            bios_version=None,
        )
        result = serialize_hardware(inv)
        assert result["system_manufacturer"] is None
        assert result["system_model"] is None
        assert result["bios_version"] is None

    def test_values_match_model(self, healthy_inventory: HardwareInventory):
        """Serialized values must exactly match the model fields."""
        result = serialize_hardware(healthy_inventory)
        assert result["cpu_model"] == healthy_inventory.cpu_model
        assert result["cpu_cores"] == healthy_inventory.cpu_cores
        assert result["cpu_threads"] == healthy_inventory.cpu_threads
        assert result["total_ram_bytes"] == healthy_inventory.total_ram_bytes
        assert result["system_manufacturer"] == healthy_inventory.system_manufacturer
        assert result["system_model"] == healthy_inventory.system_model
        assert result["bios_version"] == healthy_inventory.bios_version
