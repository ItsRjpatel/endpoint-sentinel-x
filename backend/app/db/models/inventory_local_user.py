from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventoryLocalUser(Base, TimestampMixin):
    """One-to-many: stores local user account inventory per endpoint."""

    __tablename__ = "inventory_local_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(String, index=True, nullable=False)
    is_active: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    privilege: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
