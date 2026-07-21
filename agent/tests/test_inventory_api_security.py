"""
Unit tests for the Security inventory API client.
"""

from unittest.mock import MagicMock, patch

import httpx

from api.inventory import submit_security
from config.settings import AgentConfig


def _make_config(**overrides) -> AgentConfig:
    defaults = {
        "agent_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "agent_secret": "test_secret_value",
        "api_base_url": "http://testserver",
        "agent_version": "0.1.0",
        "inventory_timeout_seconds": 5,
    }
    defaults.update(overrides)
    return AgentConfig(**defaults)


def _make_response(status_code: int, json_body: dict | None = None) -> httpx.Response:
    import json as _json

    content = _json.dumps(json_body or {}).encode()
    return httpx.Response(
        status_code=status_code,
        content=content,
        headers={"Content-Type": "application/json"},
        request=httpx.Request("POST", "http://testserver/api/v1/inventory/security"),
    )


_SAMPLE_BODY: dict = {
    "collected_at": "2026-07-21T00:00:00+00:00",
    "agent_version": "0.1.0",
    "inventory_hash": "c" * 64,
    "security": {
        "defender": None,
        "tpm": None,
        "secure_boot": None,
        "uac": None,
        "security_center": None,
        "bitlocker_volumes": [],
        "firewall_profiles": [],
    },
}


class TestSubmitSecuritySuccess:
    """Tests for HTTP 200 responses (accepted and skipped)."""

    def test_accepted_response_does_not_raise(self):
        cfg = _make_config()
        response = _make_response(200, {"status": "accepted", "category": "security"})

        with patch("api.inventory._get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.post.return_value = response
            mock_get_client.return_value = mock_client

            submit_security(body=_SAMPLE_BODY, config=cfg)

        mock_client.post.assert_called_once()

    def test_correct_url_is_called(self):
        cfg = _make_config(api_base_url="http://sentinel-backend")
        response = _make_response(200, {"status": "accepted", "category": "security"})

        with patch("api.inventory._get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.post.return_value = response
            mock_get_client.return_value = mock_client

            submit_security(body=_SAMPLE_BODY, config=cfg)

        called_url = mock_client.post.call_args[0][0]
        assert called_url == "http://sentinel-backend/api/v1/inventory/security"

    def test_auth_headers_are_sent(self):
        cfg = _make_config(
            agent_id="test-agent-uuid",
            agent_secret="super_secret",
        )
        response = _make_response(200, {"status": "accepted", "category": "security"})

        with patch("api.inventory._get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.post.return_value = response
            mock_get_client.return_value = mock_client

            submit_security(body=_SAMPLE_BODY, config=cfg)

        headers = mock_client.post.call_args.kwargs["headers"]
        assert headers["X-Agent-ID"] == "test-agent-uuid"
        assert headers["X-Agent-Secret"] == "super_secret"

    def test_unauthorized_401_no_retry(self):
        cfg = _make_config()

        with patch("api.inventory._get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.post.return_value = _make_response(401)
            mock_get_client.return_value = mock_client

            submit_security(body=_SAMPLE_BODY, config=cfg)

        assert mock_client.post.call_count == 1
