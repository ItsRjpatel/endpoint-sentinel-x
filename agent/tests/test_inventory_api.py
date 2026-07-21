"""
Unit tests for the hardware inventory API client.

All HTTP traffic is mocked via ``httpx`` transport overrides — no real network
connection is made.

Test coverage
-------------
* 200 accepted response is handled and logged correctly.
* 200 skipped response (duplicate hash) is detected by status field.
* 401 Unauthorized terminates without retry.
* 403 Forbidden terminates without retry.
* 409 Conflict terminates without retry.
* 413 Payload Too Large terminates without retry.
* Connection error triggers retry (up to 3 attempts).
* Timeout triggers retry (up to 3 attempts).
* Unexpected exceptions are caught; function always returns normally.
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from api.inventory import _MAX_RETRIES, submit_hardware
from config.settings import AgentConfig

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(**overrides) -> AgentConfig:
    """Build a minimal AgentConfig with test-safe values."""
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
    """Create an httpx.Response with a JSON body."""
    import json as _json

    content = _json.dumps(json_body or {}).encode()
    return httpx.Response(
        status_code=status_code,
        content=content,
        headers={"Content-Type": "application/json"},
        request=httpx.Request("POST", "http://testserver/api/v1/inventory/hardware"),
    )


_SAMPLE_BODY: dict = {
    "collected_at": "2026-07-21T00:00:00+00:00",
    "agent_version": "0.1.0",
    "inventory_hash": "a" * 64,
    "hardware": {
        "cpu_model": "Intel Core i7",
        "cpu_cores": 4,
        "cpu_threads": 8,
        "total_ram_bytes": 17_179_869_184,
        "system_manufacturer": "Dell Inc.",
        "system_model": "Latitude 7420",
        "bios_version": "1.23.0",
    },
}


# ---------------------------------------------------------------------------
# Successful upload tests
# ---------------------------------------------------------------------------


class TestSubmitHardwareSuccess:
    """Tests for HTTP 200 responses (accepted and skipped)."""

    def test_accepted_response_does_not_raise(self):
        """A 200 accepted response must complete without raising."""
        cfg = _make_config()
        response = _make_response(200, {"status": "accepted", "category": "hardware"})

        with patch("api.inventory._get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.post.return_value = response
            mock_get_client.return_value = mock_client

            # Must not raise
            submit_hardware(body=_SAMPLE_BODY, config=cfg)

        mock_client.post.assert_called_once()

    def test_skipped_response_does_not_raise(self):
        """A 200 skipped response (duplicate hash) must complete without raising."""
        cfg = _make_config()
        response = _make_response(200, {"status": "skipped", "category": "hardware"})

        with patch("api.inventory._get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.post.return_value = response
            mock_get_client.return_value = mock_client

            submit_hardware(body=_SAMPLE_BODY, config=cfg)

        mock_client.post.assert_called_once()

    def test_correct_url_is_called(self):
        """The client must POST to /api/v1/inventory/hardware."""
        cfg = _make_config(api_base_url="http://sentinel-backend")
        response = _make_response(200, {"status": "accepted", "category": "hardware"})

        with patch("api.inventory._get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.post.return_value = response
            mock_get_client.return_value = mock_client

            submit_hardware(body=_SAMPLE_BODY, config=cfg)

        called_url = mock_client.post.call_args[0][0]
        assert called_url == "http://sentinel-backend/api/v1/inventory/hardware"

    def test_auth_headers_are_sent(self):
        """X-Agent-ID and X-Agent-Secret headers must be present in the request."""
        cfg = _make_config(
            agent_id="test-agent-uuid",
            agent_secret="super_secret",
        )
        response = _make_response(200, {"status": "accepted", "category": "hardware"})

        with patch("api.inventory._get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.post.return_value = response
            mock_get_client.return_value = mock_client

            submit_hardware(body=_SAMPLE_BODY, config=cfg)

        headers = mock_client.post.call_args.kwargs["headers"]
        assert headers["X-Agent-ID"] == "test-agent-uuid"
        assert headers["X-Agent-Secret"] == "super_secret"


# ---------------------------------------------------------------------------
# Non-retryable error tests
# ---------------------------------------------------------------------------


class TestSubmitHardwareTerminalErrors:
    """Tests for HTTP error responses that must NOT trigger a retry."""

    @pytest.mark.parametrize("status_code", [401, 403, 409, 413])
    def test_terminal_status_does_not_retry(self, status_code: int):
        """HTTP {401, 403, 409, 413} must result in exactly ONE attempt."""
        cfg = _make_config()
        response = _make_response(status_code)

        with patch("api.inventory._get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.post.return_value = response
            mock_get_client.return_value = mock_client

            submit_hardware(body=_SAMPLE_BODY, config=cfg)

        # Exactly one HTTP call — no retry
        assert mock_client.post.call_count == 1

    @pytest.mark.parametrize("status_code", [401, 403, 409, 413])
    def test_terminal_status_does_not_raise(self, status_code: int):
        """Terminal HTTP errors must not propagate as exceptions."""
        cfg = _make_config()
        response = _make_response(status_code)

        with patch("api.inventory._get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.post.return_value = response
            mock_get_client.return_value = mock_client

            # Must not raise
            submit_hardware(body=_SAMPLE_BODY, config=cfg)

    def test_unauthorized_401_no_retry(self):
        """401 specifically must not retry (credential errors are non-transient)."""
        cfg = _make_config()

        with patch("api.inventory._get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.post.return_value = _make_response(401)
            mock_get_client.return_value = mock_client

            submit_hardware(body=_SAMPLE_BODY, config=cfg)

        assert mock_client.post.call_count == 1

    def test_conflict_409_no_retry(self):
        """409 Conflict (stale snapshot) must not retry."""
        cfg = _make_config()

        with patch("api.inventory._get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.post.return_value = _make_response(409)
            mock_get_client.return_value = mock_client

            submit_hardware(body=_SAMPLE_BODY, config=cfg)

        assert mock_client.post.call_count == 1


# ---------------------------------------------------------------------------
# Network failure and retry tests
# ---------------------------------------------------------------------------


class TestSubmitHardwareRetry:
    """Tests for retryable failure conditions (connection errors, timeouts)."""

    def test_connect_error_retries_up_to_max(self):
        """ConnectError must be retried up to _MAX_RETRIES times then stop."""
        cfg = _make_config()

        with (
            patch("api.inventory._get_http_client") as mock_get_client,
            patch("api.inventory.time.sleep"),  # suppress actual sleeping
        ):
            mock_client = MagicMock()
            mock_client.post.side_effect = httpx.ConnectError("Connection refused")
            mock_get_client.return_value = mock_client

            submit_hardware(body=_SAMPLE_BODY, config=cfg)

        assert mock_client.post.call_count == _MAX_RETRIES

    def test_timeout_retries_up_to_max(self):
        """ReadTimeout must be retried up to _MAX_RETRIES times then stop."""
        cfg = _make_config()

        with (
            patch("api.inventory._get_http_client") as mock_get_client,
            patch("api.inventory.time.sleep"),
        ):
            mock_client = MagicMock()
            mock_client.post.side_effect = httpx.ReadTimeout("timed out")
            mock_get_client.return_value = mock_client

            submit_hardware(body=_SAMPLE_BODY, config=cfg)

        assert mock_client.post.call_count == _MAX_RETRIES

    def test_connect_error_does_not_raise(self):
        """ConnectError exhausting all retries must not propagate to the caller."""
        cfg = _make_config()

        with (
            patch("api.inventory._get_http_client") as mock_get_client,
            patch("api.inventory.time.sleep"),
        ):
            mock_client = MagicMock()
            mock_client.post.side_effect = httpx.ConnectError("host unreachable")
            mock_get_client.return_value = mock_client

            # Must not raise
            submit_hardware(body=_SAMPLE_BODY, config=cfg)

    def test_timeout_does_not_raise(self):
        """Timeout exhausting all retries must not propagate to the caller."""
        cfg = _make_config()

        with (
            patch("api.inventory._get_http_client") as mock_get_client,
            patch("api.inventory.time.sleep"),
        ):
            mock_client = MagicMock()
            mock_client.post.side_effect = httpx.ConnectTimeout("connect timeout")
            mock_get_client.return_value = mock_client

            # Must not raise
            submit_hardware(body=_SAMPLE_BODY, config=cfg)

    def test_succeeds_on_retry_after_transient_error(self):
        """If connection fails then succeeds, the result is treated as success."""
        cfg = _make_config()
        success_response = _make_response(200, {"status": "accepted", "category": "hardware"})

        with (
            patch("api.inventory._get_http_client") as mock_get_client,
            patch("api.inventory.time.sleep"),
        ):
            mock_client = MagicMock()
            mock_client.post.side_effect = [
                httpx.ConnectError("first attempt fails"),
                success_response,
            ]
            mock_get_client.return_value = mock_client

            submit_hardware(body=_SAMPLE_BODY, config=cfg)

        assert mock_client.post.call_count == 2

    def test_backoff_sleep_is_called_between_retries(self):
        """time.sleep must be called with the correct backoff values on retry."""
        cfg = _make_config()

        with (
            patch("api.inventory._get_http_client") as mock_get_client,
            patch("api.inventory.time.sleep") as mock_sleep,
        ):
            mock_client = MagicMock()
            mock_client.post.side_effect = httpx.ConnectError("down")
            mock_get_client.return_value = mock_client

            submit_hardware(body=_SAMPLE_BODY, config=cfg)

        # Should have slept twice (before attempt 2 and attempt 3)
        assert mock_sleep.call_count == 2
        sleep_values = [c.args[0] for c in mock_sleep.call_args_list]
        assert sleep_values == [1.0, 2.0]


# ---------------------------------------------------------------------------
# Unexpected exception tests
# ---------------------------------------------------------------------------


class TestSubmitHardwareUnexpectedErrors:
    """Any unexpected exception must be swallowed — function always returns."""

    def test_unexpected_exception_does_not_raise(self):
        """A completely unexpected exception inside the HTTP call must be caught."""
        cfg = _make_config()

        with patch("api.inventory._get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.post.side_effect = RuntimeError("completely unexpected")
            mock_get_client.return_value = mock_client

            # Must not raise
            submit_hardware(body=_SAMPLE_BODY, config=cfg)

    def test_json_decode_error_on_200_does_not_raise(self):
        """If the 200 response body is not valid JSON, function must still return."""
        cfg = _make_config()
        # Craft a response with non-JSON content
        bad_response = httpx.Response(
            status_code=200,
            content=b"not json at all",
            request=httpx.Request("POST", "http://testserver/api/v1/inventory/hardware"),
        )

        with patch("api.inventory._get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.post.return_value = bad_response
            mock_get_client.return_value = mock_client

            # Must not raise
            submit_hardware(body=_SAMPLE_BODY, config=cfg)
