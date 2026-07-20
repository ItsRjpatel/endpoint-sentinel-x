from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.inventory_network_adapter import InventoryNetworkAdapter


class InventoryNetworkAddress(Base):
    """Normalized IP address records for a network adapter (IPv4 and IPv6)."""

    __tablename__ = "inventory_network_addresses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    adapter_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_network_adapters.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    address: Mapped[str] = mapped_column(String, index=True, nullable=False)
    family: Mapped[str] = mapped_column(String(10), nullable=False)  # ipv4 | ipv6
    prefix_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_loopback: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    adapter: Mapped["InventoryNetworkAdapter"] = relationship(
        "InventoryNetworkAdapter", back_populates="addresses"
    )
