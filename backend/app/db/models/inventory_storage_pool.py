from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventoryStoragePool(Base, TimestampMixin):
    """One-to-many: stores storage pool information per endpoint."""

    __tablename__ = "inventory_storage_pools"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    pool_name: Mapped[str] = mapped_column(String, nullable=False)
    health_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    operational_status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    total_capacity: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    free_capacity: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
