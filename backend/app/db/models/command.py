import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Command(Base):
    """
    Tracks the lifecycle of an orchestrated remote command.
    """
    __tablename__ = "commands"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    endpoint_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    command_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    command_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # JSON dictionary of arguments provided to the agent
    parameters: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    status: Mapped[str] = mapped_column(String, nullable=False, index=True, default="PENDING")
    
    # Timestamps tracking the command lifecycle
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    queued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Execution metrics and results
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    execution_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)  # in milliseconds
    
    result_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    endpoint: Mapped["Endpoint"] = relationship("Endpoint", back_populates="commands")
