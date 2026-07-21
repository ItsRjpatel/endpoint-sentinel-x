from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.inventory_network_adapter import InventoryNetworkAdapter


class InventoryNetworkVpn(Base):
    """Stores VPN specific details for a virtual adapter."""

    __tablename__ = "inventory_network_vpn"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    adapter_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_network_adapters.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    connection_status: Mapped[str | None] = mapped_column(String, nullable=True)
    tunnel_type: Mapped[str | None] = mapped_column(String, nullable=True)

    adapter: Mapped["InventoryNetworkAdapter"] = relationship(
        "InventoryNetworkAdapter", back_populates="vpn"
    )
