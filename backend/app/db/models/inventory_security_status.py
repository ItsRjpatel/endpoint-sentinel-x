from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.endpoint import Endpoint


class InventorySecurityStatus(Base, TimestampMixin):
    """One-to-one inventory table storing host security control states."""

    __tablename__ = "inventory_security_status"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    # Defender
    defender_installed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    defender_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    defender_rtp: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    defender_sig_version: Mapped[str | None] = mapped_column(String, nullable=True)
    defender_engine_version: Mapped[str | None] = mapped_column(String, nullable=True)
    defender_last_sig_update: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    defender_last_quick_scan: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    defender_last_full_scan: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    defender_av_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    defender_antispyware_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    defender_nis_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    defender_ioav_protection: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    defender_behavior_monitoring: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    defender_tamper_protection: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    defender_exploit_protection: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    defender_controlled_folder_access: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    defender_boot_protection: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # TPM
    tpm_present: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tpm_ready: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tpm_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tpm_activated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tpm_manufacturer: Mapped[str | None] = mapped_column(String, nullable=True)
    tpm_manufacturer_version: Mapped[str | None] = mapped_column(String, nullable=True)
    tpm_specification_version: Mapped[str | None] = mapped_column(String, nullable=True)
    tpm_managed_auth_level: Mapped[str | None] = mapped_column(String, nullable=True)

    # Secure Boot
    secure_boot_supported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    secure_boot_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # UAC
    uac_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    uac_consent_prompt_behavior: Mapped[str | None] = mapped_column(String, nullable=True)

    # Security Center
    security_center_status: Mapped[str | None] = mapped_column(String, nullable=True)
    security_center_registered_av: Mapped[str | None] = mapped_column(String, nullable=True)
    security_center_registered_fw: Mapped[str | None] = mapped_column(String, nullable=True)
    security_center_registered_antispyware: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    security_center_product_state: Mapped[int | None] = mapped_column(nullable=True)

    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
