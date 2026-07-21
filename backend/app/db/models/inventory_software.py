from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventorySoftware(Base, TimestampMixin):
    """One-to-many: stores installed application inventory per endpoint."""

    __tablename__ = "inventory_software"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    version: Mapped[str | None] = mapped_column(String, nullable=True)
    publisher: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    install_date: Mapped[str | None] = mapped_column(String, nullable=True)
    install_location: Mapped[str | None] = mapped_column(String, nullable=True)
    install_source: Mapped[str | None] = mapped_column(String, nullable=True)
    estimated_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    uninstall_string: Mapped[str | None] = mapped_column(String, nullable=True)
    quiet_uninstall_string: Mapped[str | None] = mapped_column(String, nullable=True)
    install_scope: Mapped[str | None] = mapped_column(String, nullable=True)
    architecture: Mapped[str | None] = mapped_column(String, nullable=True)
    product_code: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    help_link: Mapped[str | None] = mapped_column(String, nullable=True)
    url_info_about: Mapped[str | None] = mapped_column(String, nullable=True)
    url_update_info: Mapped[str | None] = mapped_column(String, nullable=True)
    display_icon: Mapped[str | None] = mapped_column(String, nullable=True)
    language: Mapped[str | None] = mapped_column(String, nullable=True)
    release_type: Mapped[str | None] = mapped_column(String, nullable=True)
    parent_application: Mapped[str | None] = mapped_column(String, nullable=True)
    parent_version: Mapped[str | None] = mapped_column(String, nullable=True)
    system_component: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    windows_installer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    no_remove: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    no_modify: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    no_repair: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    classification: Mapped[str | None] = mapped_column(String, nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
