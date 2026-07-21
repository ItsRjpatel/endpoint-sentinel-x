"""
Inventory API client for Endpoint Sentinel X.

Provides a module-level shared ``httpx.Client`` and the ``submit_hardware``
function that posts a hardware inventory payload to the backend.

Authentication
--------------
Every request carries ``X-Agent-ID`` and ``X-Agent-Secret`` headers, matching
the backend ``get_current_agent`` dependency.  Credentials are read from the
``AgentConfig`` singleton — never hard-coded or duplicated here.

HTTP Client
-----------
A single :class:`httpx.Client` is created at module import time and reused
for every inventory request.  This avoids the overhead of opening a new TCP
connection on each upload.

Retry Policy
------------
Connection errors and timeouts are retried up to 3 times with exponential
backoff (1 s → 2 s → 4 s).  HTTP error responses (401, 403, 409, 413) are
**not** retried — they indicate a logical rejection that a retry cannot fix.
"""

import time

import httpx
import structlog

from config.settings import AgentConfig, agent_settings

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Shared HTTP client
# ---------------------------------------------------------------------------

_http_client: httpx.Client | None = None


def _get_http_client(config: AgentConfig) -> httpx.Client:
    """
    Return (or lazily create) the shared :class:`httpx.Client`.

    The client is configured with the agent's ``inventory_timeout_seconds``
    as both connect and read timeout.
    """
    global _http_client  # noqa: PLW0603
    if _http_client is None or _http_client.is_closed:
        timeout = httpx.Timeout(float(config.inventory_timeout_seconds))
        _http_client = httpx.Client(timeout=timeout)
    return _http_client


# ---------------------------------------------------------------------------
# Retry constants
# ---------------------------------------------------------------------------

_MAX_RETRIES: int = 3
_BACKOFF_SECONDS: tuple[float, ...] = (1.0, 2.0, 4.0)

# HTTP status codes that must NOT be retried.
_NO_RETRY_STATUSES: frozenset[int] = frozenset({401, 403, 409, 413})


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def submit_hardware(body: dict, config: AgentConfig | None = None) -> None:
    """
    Upload a hardware inventory payload to ``POST /api/v1/inventory/hardware``.

    Parameters
    ----------
    body:
        Fully-formed request body as a plain dictionary.  Must conform to the
        ``HardwareInventoryRequest`` schema expected by the backend.
    config:
        Agent configuration instance.  Defaults to the module-level
        ``agent_settings`` singleton when ``None``.

    Behaviour
    ---------
    * **200 accepted** — logs success and returns.
    * **200 skipped** — inventory hash matched a previous upload; logs skip and returns.
    * **401 Unauthorized** — logs error; does not retry.
    * **403 Forbidden** — agent decommissioned; logs error; does not retry.
    * **409 Conflict** — stale snapshot; logs warning; does not retry.
    * **413 Payload Too Large** — logs error; does not retry.
    * **Other 4xx/5xx** — logs error; does not retry.
    * **Connection / timeout errors** — retried up to 3 times with exponential backoff.
    * Any unhandled exception is caught; the function always returns normally.

    Secrets
    -------
    Credential values are never logged.
    """
    cfg = config or agent_settings
    client = _get_http_client(cfg)

    url = f"{cfg.api_base_url.rstrip('/')}/api/v1/inventory/hardware"
    headers = {
        "X-Agent-ID": cfg.agent_id,
        "X-Agent-Secret": cfg.agent_secret,
        "Content-Type": "application/json",
    }

    log = logger.bind(url=url, agent_id=cfg.agent_id, category="hardware")
    log.info("Hardware inventory upload started")

    attempt = 0
    while attempt <= _MAX_RETRIES - 1:
        try:
            response = client.post(url, json=body, headers=headers)
        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
            attempt += 1
            if attempt >= _MAX_RETRIES:
                log.error(
                    "Hardware inventory upload failed after all retries",
                    error=str(exc),
                    attempts=attempt,
                )
                return
            backoff = _BACKOFF_SECONDS[attempt - 1]
            log.warning(
                "Network error during hardware inventory upload — retrying",
                error=str(exc),
                attempt=attempt,
                backoff_seconds=backoff,
            )
            time.sleep(backoff)
            continue
        except httpx.TimeoutException as exc:
            attempt += 1
            if attempt >= _MAX_RETRIES:
                log.error(
                    "Hardware inventory upload timed out after all retries",
                    error=str(exc),
                    attempts=attempt,
                )
                return
            backoff = _BACKOFF_SECONDS[attempt - 1]
            log.warning(
                "Timeout during hardware inventory upload — retrying",
                error=str(exc),
                attempt=attempt,
                backoff_seconds=backoff,
            )
            time.sleep(backoff)
            continue
        except Exception as exc:  # noqa: BLE001
            log.error("Unexpected error during hardware inventory upload", error=str(exc))
            return

        # ── Response handling ────────────────────────────────────────────────
        status_code = response.status_code
        log = log.bind(http_status=status_code)

        if status_code == 200:
            try:
                data = response.json()
            except Exception:  # noqa: BLE001
                data = {}

            upload_status = data.get("status", "unknown")

            if upload_status == "skipped":
                log.info("Hardware inventory upload skipped (hash unchanged)", status=upload_status)
            else:
                log.info("Hardware inventory upload completed successfully", status=upload_status)
            return

        if status_code in _NO_RETRY_STATUSES:
            _log_terminal_error(log, status_code, response)
            return

        # Unexpected status — log and bail without retry.
        log.error(
            "Hardware inventory upload failed with unexpected HTTP status",
            http_status=status_code,
        )
        return

    # Exhausted retries (should be unreachable; loop returns internally).
    log.error("Hardware inventory upload exhausted all retry attempts")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _log_terminal_error(
    log: structlog.BoundLogger, status_code: int, response: httpx.Response
) -> None:
    """Log a descriptive message for non-retryable HTTP error responses."""
    messages: dict[int, str] = {
        401: "Hardware inventory upload rejected: agent unauthorized (401)",
        403: "Hardware inventory upload rejected: agent forbidden/decommissioned (403)",
        409: "Hardware inventory upload conflict: stale snapshot rejected by server (409)",
        413: "Hardware inventory upload rejected: payload too large (413)",
    }
    msg = messages.get(status_code, f"Hardware inventory upload failed (HTTP {status_code})")
    log.error(msg, http_status=status_code)
