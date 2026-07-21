from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventoryFirewallProfile(Base, TimestampMixin):
    """One-to-many inventory table storing Windows Firewall profiles per endpoint."""

    __tablename__ = "inventory_firewall_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    profile_name: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_inbound_policy: Mapped[str | None] = mapped_column(String, nullable=True)
    default_outbound_policy: Mapped[str | None] = mapped_column(String, nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
