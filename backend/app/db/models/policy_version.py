from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.policy import Policy

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity

class PolicyVersion(BaseEntity):
    """Model tracking the versions and history of a policy."""

    __tablename__ = "policy_versions"

    policy_id: Mapped[int] = mapped_column(
        ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    configuration: Mapped[dict] = mapped_column(JSON, nullable=False)
    change_summary: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    policy: Mapped["Policy"] = relationship("Policy", back_populates="versions")
