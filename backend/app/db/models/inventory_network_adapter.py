from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.db.models.inventory_network_vpn import InventoryNetworkVpn
from app.db.models.inventory_network_wifi import InventoryNetworkWifi

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
    friendly_name: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    interface_type: Mapped[str | None] = mapped_column(String, nullable=True)
    adapter_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String, nullable=True)
    mac_address: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    is_physical: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_virtual: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    admin_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    link_speed_bps: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    mtu: Mapped[int | None] = mapped_column(Integer, nullable=True)
    driver_version: Mapped[str | None] = mapped_column(String, nullable=True)
    driver_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    interface_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    interface_guid: Mapped[str | None] = mapped_column(String, nullable=True)
    dhcp_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    dhcp_server: Mapped[str | None] = mapped_column(String, nullable=True)
    dhcp_lease_obtained: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    dhcp_lease_expires: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    default_gateways: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    dns_servers: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    dns_search_suffixes: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
    addresses: Mapped[list["InventoryNetworkAddress"]] = relationship(
        "InventoryNetworkAddress", back_populates="adapter", cascade="all, delete-orphan"
    )
    wifi: Mapped["InventoryNetworkWifi | None"] = relationship(
        "InventoryNetworkWifi",
        back_populates="adapter",
        cascade="all, delete-orphan",
        uselist=False,
    )
    vpn: Mapped["InventoryNetworkVpn | None"] = relationship(
        "InventoryNetworkVpn", back_populates="adapter", cascade="all, delete-orphan", uselist=False
    )
