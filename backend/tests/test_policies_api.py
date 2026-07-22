from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_active_user
from app.main import app
from app.db.models.user import User


@pytest.mark.anyio
async def test_policies_list_unauthorized(client: AsyncClient) -> None:
    """Verifies that the /policies API requires authentication."""
    response = await client.get("/api/v1/policies")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_policies_list_authorized(client: AsyncClient) -> None:
    """Verifies that the /policies API returns 200 for authenticated users."""
    mock_db = AsyncMock()
    mock_result = AsyncMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    mock_user = User(id=1, organization_id=1, username="testadmin", role="ORGANIZATION_ADMIN", is_active=True)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    response = await client.get("/api/v1/policies")
    assert response.status_code == 200

    app.dependency_overrides.clear()
