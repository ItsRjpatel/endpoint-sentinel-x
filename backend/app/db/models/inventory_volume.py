from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventoryVolume(Base, TimestampMixin):
    """One-to-many: stores filesystem volume information per endpoint."""

    __tablename__ = "inventory_volumes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    drive_letter: Mapped[str | None] = mapped_column(String(10), nullable=True)
    volume_name: Mapped[str | None] = mapped_column(String, nullable=True)
    file_system: Mapped[str | None] = mapped_column(String(50), nullable=True)
    file_system_label: Mapped[str | None] = mapped_column(String, nullable=True)
    file_system_version: Mapped[str | None] = mapped_column(String, nullable=True)
    allocation_unit_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    total_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    free_space: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    used_space: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    percentage_used: Mapped[float | None] = mapped_column(Float, nullable=True)
    percentage_free: Mapped[float | None] = mapped_column(Float, nullable=True)

    health_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    compression_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    deduplication_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    shadow_copies_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
