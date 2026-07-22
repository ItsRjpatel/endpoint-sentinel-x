from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.policy import Policy
from app.db.models.policy_assignment import PolicyAssignment
from app.db.models.policy_version import PolicyVersion


class PolicyRepository:
    """Repository for managing Policy entities in the database."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, policy: Policy) -> Policy:
        self.db.add(policy)
        await self.db.flush()
        return policy

    async def update(self, policy: Policy) -> Policy:
        await self.db.flush()
        return policy

    async def delete(self, policy_id: int) -> None:
        stmt = delete(Policy).where(Policy.id == policy_id)
        await self.db.execute(stmt)
        await self.db.flush()

    async def get_by_id(self, policy_id: int) -> Policy | None:
        stmt = (
            select(Policy)
            .options(selectinload(Policy.versions), selectinload(Policy.assignments))
            .where(Policy.id == policy_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_organization(self, organization_id: int) -> Sequence[Policy]:
        stmt = select(Policy).where(Policy.organization_id == organization_id).order_by(Policy.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_version(self, policy_version: PolicyVersion) -> PolicyVersion:
        self.db.add(policy_version)
        await self.db.flush()
        return policy_version

    async def assign_endpoint(self, assignment: PolicyAssignment) -> PolicyAssignment:
        self.db.add(assignment)
        await self.db.flush()
        return assignment

    async def remove_assignment(self, policy_id: int, endpoint_id: int) -> bool:
        stmt = delete(PolicyAssignment).where(
            PolicyAssignment.policy_id == policy_id,
            PolicyAssignment.endpoint_id == endpoint_id,
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount > 0

    async def get_assignment(self, policy_id: int, endpoint_id: int) -> PolicyAssignment | None:
        stmt = select(PolicyAssignment).where(
            PolicyAssignment.policy_id == policy_id,
            PolicyAssignment.endpoint_id == endpoint_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
