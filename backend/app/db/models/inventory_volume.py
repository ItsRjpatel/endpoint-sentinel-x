from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String
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
    label: Mapped[str | None] = mapped_column(String, nullable=True)
    filesystem: Mapped[str | None] = mapped_column(String(50), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    free_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
