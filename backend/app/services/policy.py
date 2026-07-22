import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.policy import Policy
from app.db.models.policy_assignment import PolicyAssignment
from app.db.models.policy_version import PolicyVersion
from app.repositories.policy import PolicyRepository
from app.schemas.policy import PolicyCreate, PolicyUpdate

logger = structlog.get_logger()


class PolicyService:
    """Service layer for Enterprise Policy Engine."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PolicyRepository(db)

    async def create_policy(self, organization_id: int, user_id: int, policy_in: PolicyCreate) -> Policy:
        """Create a new policy and its initial version."""
        policy = Policy(
            organization_id=organization_id,
            name=policy_in.name,
            description=policy_in.description,
            category=policy_in.category,
            enabled=policy_in.enabled,
            priority=policy_in.priority,
            current_version=1,
            created_by_id=user_id,
        )
        created_policy = await self.repo.create(policy)

        # Create initial version
        version = PolicyVersion(
            policy_id=created_policy.id,
            version=1,
            configuration=policy_in.configuration,
            change_summary="Initial policy creation"
        )
        await self.repo.create_version(version)

        logger.info(
            "Policy created",
            policy_id=created_policy.id,
            organization_id=organization_id,
            user_id=user_id
        )

        # Refetch to get relationships loaded if necessary, or just return
        return await self.repo.get_by_id(created_policy.id)

    async def update_policy(self, policy_id: int, policy_in: PolicyUpdate) -> Policy | None:
        """Update an existing policy. If configuration is provided, create a new version."""
        policy = await self.repo.get_by_id(policy_id)
        if not policy:
            return None

        has_changes = False

        if policy_in.name is not None and policy_in.name != policy.name:
            policy.name = policy_in.name
            has_changes = True
        if policy_in.description is not None and policy_in.description != policy.description:
            policy.description = policy_in.description
            has_changes = True
        if policy_in.category is not None and policy_in.category != policy.category:
            policy.category = policy_in.category
            has_changes = True
        if policy_in.enabled is not None and policy_in.enabled != policy.enabled:
            policy.enabled = policy_in.enabled
            has_changes = True
        if policy_in.priority is not None and policy_in.priority != policy.priority:
            policy.priority = policy_in.priority
            has_changes = True

        if policy_in.configuration is not None:
            # Check if configuration actually changed compared to current version?
            # For simplicity, if provided, we bump version.
            policy.current_version += 1
            has_changes = True
            
            version = PolicyVersion(
                policy_id=policy.id,
                version=policy.current_version,
                configuration=policy_in.configuration,
                change_summary=policy_in.change_summary or "Policy updated"
            )
            await self.repo.create_version(version)

        if has_changes:
            policy = await self.repo.update(policy)
            logger.info("Policy updated", policy_id=policy.id, current_version=policy.current_version)

        return await self.repo.get_by_id(policy.id)

    async def delete_policy(self, policy_id: int) -> bool:
        """Delete a policy."""
        policy = await self.repo.get_by_id(policy_id)
        if not policy:
            return False

        await self.repo.delete(policy_id)
        logger.info("Policy deleted", policy_id=policy_id)
        return True

    async def get_policy(self, policy_id: int) -> Policy | None:
        """Get a single policy by ID."""
        return await self.repo.get_by_id(policy_id)

    async def list_policies(self, organization_id: int) -> list[Policy]:
        """List all policies for an organization."""
        policies = await self.repo.list_by_organization(organization_id)
        return list(policies)

    async def assign_endpoint(self, policy_id: int, endpoint_id: int, user_id: int) -> PolicyAssignment | None:
        """Assign a policy to an endpoint."""
        policy = await self.repo.get_by_id(policy_id)
        if not policy:
            return None

        # Check if already assigned
        existing = await self.repo.get_assignment(policy_id, endpoint_id)
        if existing:
            return existing

        assignment = PolicyAssignment(
            policy_id=policy_id,
            endpoint_id=endpoint_id,
            assigned_by_id=user_id
        )
        created = await self.repo.assign_endpoint(assignment)
        logger.info("Policy assigned", policy_id=policy_id, endpoint_id=endpoint_id, user_id=user_id)
        return created

    async def unassign_endpoint(self, policy_id: int, endpoint_id: int) -> bool:
        """Remove a policy assignment from an endpoint."""
        removed = await self.repo.remove_assignment(policy_id, endpoint_id)
        if removed:
            logger.info("Policy unassigned", policy_id=policy_id, endpoint_id=endpoint_id)
        return removed
