from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventoryWindowsUpdate(Base, TimestampMixin):
    """One-to-many: stores installed Windows Updates per endpoint."""

    __tablename__ = "inventory_windows_updates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    hotfix_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    classification: Mapped[str | None] = mapped_column(String, nullable=True)
    installed_by: Mapped[str | None] = mapped_column(String, nullable=True)
    installed_on: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    installation_state: Mapped[str | None] = mapped_column(String, nullable=True)
    support_url: Mapped[str | None] = mapped_column(String, nullable=True)
    update_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    revision_number: Mapped[int | None] = mapped_column(nullable=True)
    deployment_source: Mapped[str | None] = mapped_column(String, nullable=True)
    package_identity: Mapped[str | None] = mapped_column(String, nullable=True)

    is_security_update: Mapped[bool] = mapped_column(Boolean, default=False)
    is_critical_update: Mapped[bool] = mapped_column(Boolean, default=False)
    is_cumulative_update: Mapped[bool] = mapped_column(Boolean, default=False)
    is_driver_update: Mapped[bool] = mapped_column(Boolean, default=False)
    is_feature_update: Mapped[bool] = mapped_column(Boolean, default=False)
    is_preview_update: Mapped[bool] = mapped_column(Boolean, default=False)
    is_servicing_stack_update: Mapped[bool] = mapped_column(Boolean, default=False)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
