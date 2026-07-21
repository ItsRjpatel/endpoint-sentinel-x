from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventoryDisk(Base, TimestampMixin):
    """One-to-many: stores physical disk information per endpoint."""

    __tablename__ = "inventory_disks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    device_name: Mapped[str | None] = mapped_column(String, nullable=True)
    friendly_name: Mapped[str | None] = mapped_column(String, nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String, nullable=True)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String, nullable=True)
    firmware_version: Mapped[str | None] = mapped_column(String, nullable=True)
    interface_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bus_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    media_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    health_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    operational_status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    logical_sector_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    physical_sector_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rotation_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_removable: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_boot_disk: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_system_disk: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    unique_id: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    partition_style: Mapped[str | None] = mapped_column(String(50), nullable=True)

    is_offline: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_read_only: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    can_pool: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
