from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventoryPartition(Base, TimestampMixin):
    """One-to-many: stores partition information per physical disk."""

    __tablename__ = "inventory_partitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    disk_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_disks.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    volume_id: Mapped[int | None] = mapped_column(
        ForeignKey("inventory_volumes.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    partition_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    partition_style: Mapped[str | None] = mapped_column(String(50), nullable=True)
    partition_type: Mapped[str | None] = mapped_column(String, nullable=True)

    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    offset_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    drive_letter: Mapped[str | None] = mapped_column(String(10), nullable=True)

    is_boot: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_hidden: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_read_only: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
    disk = relationship("InventoryDisk")
    volume = relationship("InventoryVolume")
