from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.organization import Organization


class OrganizationRepository:
    """Repository handling CRUD operations for Organization entity."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, org_id: int) -> Organization | None:
        """Fetch organization by database ID."""
        return await self.db.get(Organization, org_id)

    async def get_by_uuid(self, uuid: UUID) -> Organization | None:
        """Fetch organization by UUID."""
        stmt = select(Organization).where(Organization.uuid == uuid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Organization | None:
        """Fetch organization by URL slug."""
        stmt = select(Organization).where(Organization.slug == slug)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> Sequence[Organization]:
        """List all organizations in database."""
        stmt = select(Organization)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, organization: Organization) -> Organization:
        """Persist a new organization."""
        self.db.add(organization)
        await self.db.flush()
        return organization

    async def update(self, organization: Organization) -> Organization:
        """Persist updates to an organization."""
        self.db.add(organization)
        await self.db.flush()
        return organization

    async def delete(self, organization: Organization) -> None:
        """Remove an organization."""
        await self.db.delete(organization)
        await self.db.flush()
