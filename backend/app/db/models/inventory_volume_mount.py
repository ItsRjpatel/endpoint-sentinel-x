from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventoryVolumeMount(Base, TimestampMixin):
    """One-to-many: stores mount points per volume."""

    __tablename__ = "inventory_volume_mounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    volume_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_volumes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    mount_path: Mapped[str] = mapped_column(String, nullable=False)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
    volume = relationship("InventoryVolume")
