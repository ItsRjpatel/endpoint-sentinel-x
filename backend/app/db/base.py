from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.0 models in Endpoint Sentinel X."""

    pass


class TimestampMixin:
    """Mixin to add audit timestamp fields to models."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


import uuid as uuid_pkg  # noqa: E402
from uuid import UUID  # noqa: E402


class BaseEntity(Base, TimestampMixin):
    """Base entity with integer primary key, UUID, and timestamps."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(
        default=uuid_pkg.uuid4,
        unique=True,
        nullable=False,
    )


# End of base entity definition
