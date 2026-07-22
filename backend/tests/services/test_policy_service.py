import pytest
from unittest.mock import AsyncMock, patch

from app.services.policy import PolicyService
from app.schemas.policy import PolicyCreate
from app.db.models.policy import Policy

@pytest.mark.anyio
async def test_create_policy_service() -> None:
    mock_db = AsyncMock()
    service = PolicyService(mock_db)
    
    mock_policy = Policy(id=1, organization_id=1, name="Test Policy")
    
    with patch("app.repositories.policy.PolicyRepository.create", new_callable=AsyncMock) as mock_create:
        with patch("app.repositories.policy.PolicyRepository.create_version", new_callable=AsyncMock) as mock_create_version:
            with patch("app.repositories.policy.PolicyRepository.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
                mock_create.return_value = mock_policy
                mock_get_by_id.return_value = mock_policy
                
                policy_in = PolicyCreate(
                    name="Test Policy",
                    category="security",
                    configuration={"require_bitlocker": True}
                )
                
                result = await service.create_policy(organization_id=1, user_id=1, policy_in=policy_in)
                
                assert result.id == 1
                assert result.name == "Test Policy"
                mock_create.assert_called_once()
                mock_create_version.assert_called_once()
