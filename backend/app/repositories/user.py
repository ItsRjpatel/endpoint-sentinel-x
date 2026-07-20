from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UserRepository:
    """Repository handling CRUD operations for User entity."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        """Fetch user by database ID."""
        return await self.db.get(User, user_id)

    async def get_by_uuid(self, uuid: UUID) -> User | None:
        """Fetch user by UUID."""
        stmt = select(User).where(User.uuid == uuid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Fetch user by email address."""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Fetch user by username."""
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_organization(self, org_id: int) -> Sequence[User]:
        """List all users belonging to a specific organization."""
        stmt = select(User).where(User.organization_id == org_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, user: User) -> User:
        """Persist a new user."""
        self.db.add(user)
        await self.db.flush()
        return user

    async def update(self, user: User) -> User:
        """Persist updates to a user."""
        self.db.add(user)
        await self.db.flush()
        return user

    async def delete(self, user: User) -> None:
        """Remove a user."""
        await self.db.delete(user)
        await self.db.flush()
