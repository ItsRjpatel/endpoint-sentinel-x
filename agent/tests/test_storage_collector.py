import json

from collectors.storage import collect_storage
from models.inventory import StorageInventoryRequest


def test_storage_collector_empty_fallback(monkeypatch):
    """Test that the storage collector returns an empty payload on failure."""

    def mock_run_powershell(script: str) -> str:
        return ""

    monkeypatch.setattr("collectors.storage.run_powershell", mock_run_powershell)

    inventory = collect_storage()
    assert isinstance(inventory, StorageInventoryRequest)
    assert len(inventory.disks) == 0
    assert len(inventory.volumes) == 0
    assert len(inventory.storage_pools) == 0


def test_storage_collector_success(monkeypatch):
    """Test that the storage collector parses valid JSON output."""
    mock_data = {
        "disks": [{"device_name": "PhysicalDrive0", "size_bytes": 500000000000, "partitions": []}],
        "volumes": [],
        "storage_pools": [],
    }

    def mock_run_powershell(script: str) -> str:
        return json.dumps(mock_data)

    monkeypatch.setattr("collectors.storage.run_powershell", mock_run_powershell)

    inventory = collect_storage()
    assert isinstance(inventory, StorageInventoryRequest)
    assert len(inventory.disks) == 1
    assert inventory.disks[0].device_name == "PhysicalDrive0"
