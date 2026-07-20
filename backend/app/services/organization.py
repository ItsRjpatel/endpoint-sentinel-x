from collections.abc import Sequence
from uuid import UUID

from app.repositories.organization import OrganizationRepository
from app.schemas.organization import OrganizationCreate, OrganizationResponse, OrganizationUpdate


class OrganizationService:
    """Service skeleton handling business orchestration for Organization."""

    def __init__(self, repository: OrganizationRepository):
        self.repository = repository

    async def create_organization(self, schema: OrganizationCreate) -> OrganizationResponse:
        """Create a new organization."""
        pass

    async def get_organization(self, org_id: int) -> OrganizationResponse | None:
        """Fetch organization by database ID."""
        pass

    async def get_organization_by_uuid(self, uuid: UUID) -> OrganizationResponse | None:
        """Fetch organization by UUID."""
        pass

    async def update_organization(
        self, org_id: int, schema: OrganizationUpdate
    ) -> OrganizationResponse:
        """Update an existing organization's details."""
        pass

    async def delete_organization(self, org_id: int) -> None:
        """Remove an organization."""
        pass

    async def list_organizations(self) -> Sequence[OrganizationResponse]:
        """Retrieve all organizations."""
        pass
