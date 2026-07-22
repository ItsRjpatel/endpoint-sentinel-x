from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.organization import Organization
    from app.db.models.policy_version import PolicyVersion
    from app.db.models.policy_assignment import PolicyAssignment
    from app.db.models.user import User

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity

class Policy(BaseEntity):
    """Model defining an enterprise security or operational policy."""

    __tablename__ = "policies"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship("User")
    versions: Mapped[list["PolicyVersion"]] = relationship(
        "PolicyVersion", back_populates="policy", cascade="all, delete-orphan"
    )
    assignments: Mapped[list["PolicyAssignment"]] = relationship(
        "PolicyAssignment", back_populates="policy", cascade="all, delete-orphan"
    )
