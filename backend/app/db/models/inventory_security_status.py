from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventorySecurityStatus(Base, TimestampMixin):
    """One-to-one inventory table storing host security control states."""

    __tablename__ = "inventory_security_status"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    antivirus_name: Mapped[str | None] = mapped_column(String, nullable=True)
    antivirus_status: Mapped[str | None] = mapped_column(String, nullable=True)
    firewall_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    bitlocker_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    secure_boot_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
