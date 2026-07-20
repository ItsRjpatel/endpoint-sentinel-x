from collections.abc import Sequence
from uuid import UUID

from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate


class UserService:
    """Service skeleton handling business orchestration for User."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, schema: UserCreate) -> UserResponse:
        """Create a new user."""
        pass

    async def get_user(self, user_id: int) -> UserResponse | None:
        """Fetch user by database ID."""
        pass

    async def get_user_by_uuid(self, uuid: UUID) -> UserResponse | None:
        """Fetch user by UUID."""
        pass

    async def update_user(self, user_id: int, schema: UserUpdate) -> UserResponse:
        """Update an existing user's details."""
        pass

    async def delete_user(self, user_id: int) -> None:
        """Remove a user."""
        pass

    async def list_organization_users(self, org_id: int) -> Sequence[UserResponse]:
        """List all users belonging to an organization."""
        pass
