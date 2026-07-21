from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventoryOS(Base, TimestampMixin):
    """One-to-one inventory table storing operating system details."""

    __tablename__ = "inventory_os"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    edition: Mapped[str | None] = mapped_column(String, nullable=True)
    version: Mapped[str] = mapped_column(String, nullable=False)
    build_number: Mapped[str | None] = mapped_column(String, nullable=True)
    display_version: Mapped[str | None] = mapped_column(String, nullable=True)
    architecture: Mapped[str] = mapped_column(String, nullable=False)
    install_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_boot_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    system_uptime_seconds: Mapped[int | None] = mapped_column(nullable=True)
    computer_name: Mapped[str | None] = mapped_column(String, nullable=True)
    domain: Mapped[str | None] = mapped_column(String, nullable=True)
    registered_owner: Mapped[str | None] = mapped_column(String, nullable=True)
    time_zone: Mapped[str | None] = mapped_column(String, nullable=True)
    system_locale: Mapped[str | None] = mapped_column(String, nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
