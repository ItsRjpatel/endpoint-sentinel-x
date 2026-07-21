import pytest
from agent.commands.service import RestartServiceCommand, StopServiceCommand

@pytest.mark.asyncio
async def test_service_name_validation():
    """Ensure regex blocks malicious input."""
    
    # Valid input
    cmd = RestartServiceCommand({"id": "1", "parameters": {"service_name": "Spooler"}})
    assert cmd._validate_service_name("Spooler") == "Spooler"

    # Malicious inputs
    invalid_inputs = [
        "Spooler; rm -rf /",
        "Spooler | iex",
        '"Spooler" -Force',
        "Spooler && echo 'hacked'",
    ]
    
    for bad_input in invalid_inputs:
        with pytest.raises(ValueError, match="Invalid 'service_name'. Contains forbidden characters."):
            cmd._validate_service_name(bad_input)
