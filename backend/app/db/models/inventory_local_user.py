from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventoryLocalUser(Base, TimestampMixin):
    """One-to-many: stores local user account inventory per endpoint."""

    __tablename__ = "inventory_local_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"), index=True, nullable=False
    )

    sid: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    account_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    is_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_locked: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_password_required: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_password_change_allowed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    password_expires: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    password_never_expires: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    password_last_set: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_logon: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_logoff: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    account_created: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    account_expires: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    bad_logon_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    home_directory: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    profile_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    script_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    primary_group: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Store group memberships as a JSONB array
    local_groups: Mapped[list[str]] = mapped_column(JSONB, default=list, server_default="[]")

    is_builtin_account: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_administrator: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_guest: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
