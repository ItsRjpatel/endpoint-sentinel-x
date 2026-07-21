import json
from unittest.mock import patch

import pytest

from collectors.software import collect_software


@pytest.fixture
def mock_powershell():
    with patch("collectors.software.run_powershell") as mock_ps:
        yield mock_ps


def test_collect_software_empty(mock_powershell):
    mock_powershell.return_value = ""
    req = collect_software()
    assert req.software == []


def test_collect_software_valid(mock_powershell):
    mock_powershell.return_value = json.dumps(
        [
            {
                "name": "Google Chrome",
                "version": "120.0",
                "publisher": "Google LLC",
                "install_date": "2024-01-15",
                "install_scope": "Machine",
                "architecture": "x64",
            },
            {
                "name": "Visual Studio Code",
                "version": "1.85.0",
                "publisher": "Microsoft Corporation",
                "install_date": None,
                "install_scope": "User",
                "architecture": "x64",
            },
        ]
    )
    req = collect_software()
    assert len(req.software) == 2
    names = {s.name for s in req.software}
    assert "Google Chrome" in names
    assert "Visual Studio Code" in names


def test_collect_software_deduplication(mock_powershell):
    # Two entries for same product code should be deduped
    mock_powershell.return_value = json.dumps(
        [
            {
                "name": "App1",
                "version": "1.0",
                "publisher": "Pub",
                "product_code": "{ABCD}",
                "install_scope": "Machine",
                "architecture": "x64",
            },
            {
                "name": "App1-duplicate",
                "version": "1.0",
                "publisher": "Pub",
                "product_code": "{ABCD}",
                "install_scope": "User",
                "architecture": "x86",
            },
        ]
    )
    req = collect_software()
    assert len(req.software) == 1
    assert req.software[0].name == "App1"
