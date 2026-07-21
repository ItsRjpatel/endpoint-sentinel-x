from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventoryVirtualDisk(Base, TimestampMixin):
    """One-to-many: stores virtual disk information per storage pool."""

    __tablename__ = "inventory_virtual_disks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    pool_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_storage_pools.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    virtual_disk_name: Mapped[str] = mapped_column(String, nullable=False)
    resiliency_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    provisioning_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    health_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    operational_status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
    pool = relationship("InventoryStoragePool")
