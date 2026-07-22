from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.policy import Policy
    from app.db.models.endpoint import Endpoint
    from app.db.models.user import User

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity

class PolicyAssignment(BaseEntity):
    """Model tracking the assignment of a policy to an endpoint."""

    __tablename__ = "policy_assignments"

    policy_id: Mapped[int] = mapped_column(
        ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assigned_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    policy: Mapped["Policy"] = relationship("Policy", back_populates="assignments")
    endpoint: Mapped["Endpoint"] = relationship("Endpoint")
    assigned_by: Mapped["User"] = relationship("User")
