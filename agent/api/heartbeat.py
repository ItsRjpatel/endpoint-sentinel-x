import httpx
import structlog
from config.settings import agent_settings

logger = structlog.get_logger(__name__)

def submit_heartbeat(status: str, cpu: float, ram: float, disk: float, net_in: int, net_out: int) -> None:
    """Submit a REST heartbeat to update performance metrics and lifecycle state."""
    headers = {
        "X-Agent-ID": str(agent_settings.agent_id),
        "X-Agent-Secret": agent_settings.agent_secret,
        "Content-Type": "application/json",
    }
    payload = {
        "status": status,
        "cpu_pct": cpu,
        "ram_pct": ram,
        "disk_pct": disk,
        "network_in": net_in,
        "network_out": net_out,
    }
    
    url = f"{agent_settings.api_base_url.rstrip('/')}/api/v1/agent/heartbeat"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            logger.debug("Heartbeat submitted successfully")
    except Exception as e:
        logger.warning("Failed to submit heartbeat", error=str(e))
