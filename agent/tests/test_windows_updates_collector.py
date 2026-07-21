import json
from unittest.mock import patch

from collectors.windows_updates import collect_windows_updates
from models.inventory import WindowsUpdatesInventoryRequest


def test_collect_windows_updates_empty():
    with patch("collectors.windows_updates.run_powershell", return_value=""):
        req = collect_windows_updates()
        assert isinstance(req, WindowsUpdatesInventoryRequest)
        assert len(req.updates) == 0


def test_collect_windows_updates_parse():
    mock_ps_output = json.dumps(
        {
            "wuapi": [
                {
                    "source": "WUAPI",
                    "hotfix_id": "KB5027303",
                    "title": "2023-06 Cumulative Update for Windows 11",
                    "installation_state": "Installed",
                    "update_id": "11111111-1111-1111-1111-111111111111",
                    "revision_number": 200,
                    "classification": "Security Updates",
                }
            ],
            "wmi": [
                {
                    "source": "WMI",
                    "hotfix_id": "KB5027303",
                    "title": "Update",
                    "installed_by": "SYSTEM",
                    "installed_on": "6/27/2023",
                    "installation_state": "Installed",
                },
                {
                    "source": "WMI",
                    "hotfix_id": "KB5000000",
                    "title": "Update",
                    "installed_by": "SYSTEM",
                    "installed_on": "6/27/2023",
                    "installation_state": "Installed",
                },
            ],
        }
    )

    with patch("collectors.windows_updates.run_powershell", return_value=mock_ps_output):
        req = collect_windows_updates()

        # Deduplicates KB5027303 properly (WMI and WUAPI overlap)
        assert len(req.updates) == 2

        # Ensure WUAPI data overrides WMI for KB5027303
        kb_wu = next(u for u in req.updates if u.hotfix_id == "KB5027303")
        assert kb_wu.title == "2023-06 Cumulative Update for Windows 11"
        assert kb_wu.is_security_update is True
        assert kb_wu.update_id == "11111111-1111-1111-1111-111111111111"

        # Ensure WMI-only is also added
        kb_wmi = next(u for u in req.updates if u.hotfix_id == "KB5000000")
        assert kb_wmi.hotfix_id == "KB5000000"
        assert kb_wmi.installed_by == "SYSTEM"
