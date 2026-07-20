from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventoryHardware(Base, TimestampMixin):
    """One-to-one inventory table storing CPU, RAM, BIOS and system board details."""

    __tablename__ = "inventory_hardware"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    cpu_model: Mapped[str] = mapped_column(String, nullable=False)
    cpu_cores: Mapped[int] = mapped_column(Integer, nullable=False)
    cpu_threads: Mapped[int] = mapped_column(Integer, nullable=False)
    total_ram_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    system_manufacturer: Mapped[str | None] = mapped_column(String, nullable=True)
    system_model: Mapped[str | None] = mapped_column(String, nullable=True)
    bios_version: Mapped[str | None] = mapped_column(String, nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
