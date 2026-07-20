from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.dependencies.database import get_db
from app.main import app


@pytest.mark.anyio
async def test_health_check_endpoint(client: AsyncClient) -> None:
    """Verifies that the /health API returns a 200 status code and matches the schema."""
    # Mock the database session to avoid requiring a running DB during unit tests
    mock_db = AsyncMock()
    mock_db.execute.return_value = None

    # Inject mock session dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    response = await client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data
    assert data["services"]["database"] == "healthy"
    assert data["services"]["redis"] == "configured"

    # Reset overrides after test
    app.dependency_overrides.clear()
