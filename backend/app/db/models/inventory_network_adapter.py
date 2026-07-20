from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint
    from app.db.models.inventory_network_address import InventoryNetworkAddress


class InventoryNetworkAdapter(Base, TimestampMixin):
    """One-to-many: stores physical and virtual network adapters per endpoint."""

    __tablename__ = "inventory_network_adapters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    mac_address: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    is_physical: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_virtual: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    adapter_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
    addresses: Mapped[list["InventoryNetworkAddress"]] = relationship(
        "InventoryNetworkAddress", back_populates="adapter", cascade="all, delete-orphan"
    )
