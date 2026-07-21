from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class InventoryDiskSmart(Base, TimestampMixin):
    """Stores SMART data for a disk (1:1 with InventoryDisk)."""

    __tablename__ = "inventory_disk_smart"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    disk_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_disks.id", ondelete="CASCADE"),
        index=True,
        unique=True,
        nullable=False,
    )

    predict_failure: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    temperature: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wear_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remaining_life: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reallocated_sector_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    disk = relationship("InventoryDisk")
