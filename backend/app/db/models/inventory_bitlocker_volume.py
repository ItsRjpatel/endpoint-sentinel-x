from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventoryBitlockerVolume(Base, TimestampMixin):
    """One-to-many inventory table storing BitLocker volumes per endpoint."""

    __tablename__ = "inventory_bitlocker_volumes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    drive_letter: Mapped[str] = mapped_column(String, nullable=False)
    volume_type: Mapped[str | None] = mapped_column(String, nullable=True)
    protection_status: Mapped[str | None] = mapped_column(String, nullable=True)
    encryption_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    encryption_method: Mapped[str | None] = mapped_column(String, nullable=True)
    lock_status: Mapped[str | None] = mapped_column(String, nullable=True)
    auto_unlock: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    key_protector_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
