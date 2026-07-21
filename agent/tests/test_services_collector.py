import json
from unittest.mock import patch

from collectors.services import collect_services
from models.inventory import ServicesInventoryRequest


def test_collect_services_empty():
    with patch("collectors.services.run_powershell", return_value=""):
        req = collect_services()
        assert isinstance(req, ServicesInventoryRequest)
        assert len(req.services) == 0


def test_collect_services_parse_and_serialize():
    mock_ps_output = json.dumps(
        [
            {
                "name": "Wuauserv",
                "display_name": "Windows Update 🚀",
                "description": None,  # Testing missing description
                "status": "Running",
                "startup_type": "Auto",
                "service_type": "Share Process",
                "binary_path": "C:\\Windows\\system32\\svchost.exe -k netsvcs -p",
                "service_account": "LocalSystem",
                "delayed_auto_start": True,
                "process_id": 1024,
                "dependencies": ["RpcSs", "rpcss"],  # Testing duplicate/ordering
                "dependent_services": [],
                "accept_stop": True,
                "accept_pause": False,
                "exit_code": 0,
                "error_control": "Normal",
                "tag_id": 0,
                "trigger_start": True,
            },
            {
                "name": "RpcSs",
                "display_name": "Remote Procedure Call (RPC)",
                "description": "RPC Service",
                "status": "Stopped",
                "startup_type": "Manual",
                "service_type": "Own Process",
                "binary_path": "C:\\Windows\\system32\\svchost.exe -k rpcss",
                "service_account": "NetworkService",
                "delayed_auto_start": False,
                "process_id": None,  # Testing missing PID
                "dependencies": [],  # Testing empty dependencies
                "dependent_services": [],
                "accept_stop": False,
                "accept_pause": False,
                "exit_code": 1077,
                "error_control": "Ignore",
                "tag_id": 0,
                "trigger_start": False,
            },
        ]
    )

    with patch("collectors.services.run_powershell", return_value=mock_ps_output):
        req = collect_services()

        assert len(req.services) == 2

        # Check Wuauserv
        wuauserv = next(s for s in req.services if s.name == "Wuauserv")
        assert wuauserv.display_name == "Windows Update 🚀"  # Unicode preserved
        assert wuauserv.description is None
        assert wuauserv.process_id == 1024

        # Check RpcSs
        rpcss = next(s for s in req.services if s.name == "RpcSs")
        assert rpcss.process_id is None
        assert rpcss.dependencies is None  # Should be converted to None if empty

        # Check calculated dependent services!
        assert wuauserv.dependent_services is None
        assert "wuauserv" in rpcss.dependent_services

        # Ensure hash is generated
        assert req.inventory_hash
        assert len(req.inventory_hash) == 64
