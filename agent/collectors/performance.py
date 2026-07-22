"""
Gathers real-time performance metrics (CPU, RAM, Disk, Network) using psutil.
"""
import psutil
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)

class PerformanceMetrics(BaseModel):
    cpu_usage_percent: float = Field(..., description="Overall CPU usage percentage")
    memory_usage_percent: float = Field(..., description="Overall Memory usage percentage")
    disk_usage_percent: float = Field(..., description="System Drive usage percentage")
    network_in_bytes: int = Field(..., description="Total bytes received")
    network_out_bytes: int = Field(..., description="Total bytes sent")

def collect() -> PerformanceMetrics:
    """Collects system performance metrics."""
    try:
        cpu = psutil.cpu_percent(interval=1.0)
    except Exception as e:
        logger.warning("Failed to collect CPU usage", error=str(e))
        cpu = 0.0

    try:
        mem = psutil.virtual_memory().percent
    except Exception as e:
        logger.warning("Failed to collect Memory usage", error=str(e))
        mem = 0.0

    try:
        disk = psutil.disk_usage('C:\\').percent
    except Exception as e:
        logger.warning("Failed to collect Disk usage", error=str(e))
        disk = 0.0

    try:
        net = psutil.net_io_counters()
        net_in = net.bytes_recv
        net_out = net.bytes_sent
    except Exception as e:
        logger.warning("Failed to collect Network IO", error=str(e))
        net_in = 0
        net_out = 0

    return PerformanceMetrics(
        cpu_usage_percent=cpu,
        memory_usage_percent=mem,
        disk_usage_percent=disk,
        network_in_bytes=net_in,
        network_out_bytes=net_out
    )
