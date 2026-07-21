from unittest.mock import MagicMock, patch

import pytest
from httpx import Response

from api.inventory import submit_network
from config.settings import AgentConfig


@pytest.fixture
def mock_config():
    return AgentConfig(
        api_base_url="http://testserver",
        agent_id="test-agent",
        agent_secret="test-secret",
    )


def test_submit_network_success(mock_config):
    with patch("api.inventory._get_http_client") as mock_client:
        mock_post = MagicMock(return_value=Response(200, json={"status": "accepted"}))
        mock_client.return_value.post = mock_post

        submit_network({"identity": {}, "adapters": []}, config=mock_config)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "http://testserver/api/v1/inventory/network"
        assert kwargs["json"] == {"identity": {}, "adapters": []}


def test_submit_network_unauthorized(mock_config):
    with patch("api.inventory._get_http_client") as mock_client:
        mock_post = MagicMock(return_value=Response(401, json={"detail": "unauthorized"}))
        mock_client.return_value.post = mock_post

        # Should log and return without raising
        submit_network({"identity": {}, "adapters": []}, config=mock_config)
        mock_post.assert_called_once()
