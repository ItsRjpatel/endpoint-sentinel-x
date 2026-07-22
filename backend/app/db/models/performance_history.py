from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.models.endpoint import Endpoint

class PerformanceHistory(BaseEntity):
    """Model tracking historical performance metrics for endpoints."""

    __tablename__ = "performance_history"

    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    cpu_usage_percent: Mapped[float] = mapped_column(Float, nullable=False)
    memory_usage_percent: Mapped[float] = mapped_column(Float, nullable=False)
    disk_usage_percent: Mapped[float] = mapped_column(Float, nullable=False)
    network_in_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    network_out_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
