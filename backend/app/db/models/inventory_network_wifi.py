from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.inventory_network_adapter import InventoryNetworkAdapter


class InventoryNetworkWifi(Base):
    """Stores Wi-Fi specific details for a wireless adapter."""

    __tablename__ = "inventory_network_wifi"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    adapter_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_network_adapters.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    ssid: Mapped[str | None] = mapped_column(String, nullable=True)
    bssid: Mapped[str | None] = mapped_column(String, nullable=True)
    signal_strength: Mapped[int | None] = mapped_column(Integer, nullable=True)
    auth_type: Mapped[str | None] = mapped_column(String, nullable=True)
    radio_type: Mapped[str | None] = mapped_column(String, nullable=True)
    channel: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frequency_mhz: Mapped[int | None] = mapped_column(Integer, nullable=True)

    adapter: Mapped["InventoryNetworkAdapter"] = relationship(
        "InventoryNetworkAdapter", back_populates="wifi"
    )
