from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventoryService(Base, TimestampMixin):
    """One-to-many: stores system service inventory per endpoint."""

    __tablename__ = "inventory_services"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String, nullable=True)
    startup_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    service_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    binary_path: Mapped[str | None] = mapped_column(String, nullable=True)
    service_account: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delayed_auto_start: Mapped[bool | None] = mapped_column(nullable=True)
    process_id: Mapped[int | None] = mapped_column(nullable=True)
    dependencies: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    dependent_services: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    accept_stop: Mapped[bool | None] = mapped_column(nullable=True)
    accept_pause: Mapped[bool | None] = mapped_column(nullable=True)
    can_shutdown: Mapped[bool | None] = mapped_column(nullable=True)
    exit_code: Mapped[int | None] = mapped_column(nullable=True)
    service_flags: Mapped[int | None] = mapped_column(nullable=True)
    error_control: Mapped[str | None] = mapped_column(String(50), nullable=True)
    load_order_group: Mapped[str | None] = mapped_column(String, nullable=True)
    tag_id: Mapped[int | None] = mapped_column(nullable=True)
    trigger_start: Mapped[bool | None] = mapped_column(nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
