from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity

if TYPE_CHECKING:
    from app.db.models.organization import Organization


class Endpoint(BaseEntity):
    """Model tracking enrolled endpoint agents, hardware details, and statuses."""

    __tablename__ = "endpoints"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    hostname: Mapped[str] = mapped_column(String, nullable=False)
    os_platform: Mapped[str] = mapped_column(String, nullable=False)
    os_version: Mapped[str] = mapped_column(String, nullable=False)
    hardware_uuid: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    ip_address: Mapped[str] = mapped_column(String, nullable=False)
    agent_id: Mapped[UUID] = mapped_column(Uuid, unique=True, index=True, nullable=False)
    agent_secret_hash: Mapped[str] = mapped_column(String, nullable=False)
    lifecycle_state: Mapped[str] = mapped_column(String(50), default="REGISTERED", nullable=False)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Network Identity
    fqdn: Mapped[str | None] = mapped_column(String, nullable=True)
    domain_workgroup: Mapped[str | None] = mapped_column(String, nullable=True)
    primary_dns_suffix: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
