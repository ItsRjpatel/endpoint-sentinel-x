"""
Agent runtime configuration.

Reads credentials and endpoint settings from environment variables or an
optional .env.agent file in the working directory.  Every inventory module
and API client imports the singleton `agent_settings` exported at the bottom
of this file.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentConfig(BaseSettings):
    """Validated settings for the Endpoint Sentinel X Windows Agent."""

    model_config = SettingsConfigDict(
        env_file=".env.agent",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Credentials (written to disk by the registration flow) ──────────────
    agent_id: str = Field(
        "",
        description="UUID of the registered agent endpoint (X-Agent-ID header).",
    )
    agent_secret: str = Field(
        "",
        description="Raw agent secret key issued at registration (X-Agent-Secret header).",
    )

    # ── Backend API ──────────────────────────────────────────────────────────
    api_base_url: str = Field(
        "http://localhost:8000",
        description="Base URL of the Endpoint Sentinel X backend API.",
    )

    # ── Agent identity ───────────────────────────────────────────────────────
    agent_version: str = Field(
        "0.1.0",
        description="Semver string of this agent build, included in every inventory upload.",
    )

    # ── HTTP behaviour ───────────────────────────────────────────────────────
    inventory_timeout_seconds: int = Field(
        30,
        ge=5,
        le=300,
        description="Seconds before an inventory HTTP request is abandoned.",
    )


# Module-level singleton — imported by all other agent modules.
agent_settings = AgentConfig()
