import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.db.models.organization import Organization
from app.db.models.user import User
from app.db.session import AsyncSessionLocal
from app.dependencies.auth import get_current_active_user, require_org_admin, require_super_admin
from app.dependencies.database import get_db
from app.main import app
from app.models.role import UserRole
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository


@pytest.fixture
async def db_session() -> AsyncSession:
    """Fixture providing a transactional session that rolls back after each test."""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(autouse=True)
async def override_db(db_session: AsyncSession):
    """Automatically overrides get_db dependency to use the transactional test session."""
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Creates a test organization and user in the database."""
    org_repo = OrganizationRepository(db_session)
    org = await org_repo.create(
        Organization(
            name="Auth Test Org",
            slug="auth-test-org",
            description="Testing auth constraints",
        )
    )

    user_repo = UserRepository(db_session)
    user = await user_repo.create(
        User(
            organization_id=org.id,
            first_name="Auth",
            last_name="User",
            email="authuser@example.com",
            username="authuser",
            password_hash=get_password_hash("authpassword123"),
            role=UserRole.SECURITY_ANALYST,
            is_active=True,
        )
    )
    return user


@pytest.mark.anyio
async def test_login_success(client: AsyncClient, test_user: User) -> None:
    """Tests successful authentication and token receipt."""
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "authuser", "password": "authpassword123"},
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert "refresh_token" in json_data
    assert json_data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_failure_credentials(client: AsyncClient, test_user: User) -> None:
    """Tests authentication failure with wrong password."""
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "authuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.anyio
async def test_login_failure_disabled_user(
    client: AsyncClient, test_user: User, db_session: AsyncSession
) -> None:
    """Tests authentication failure for disabled user."""
    test_user.is_active = False
    db_session.add(test_user)
    await db_session.flush()

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "authuser", "password": "authpassword123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User is disabled"


@pytest.mark.anyio
async def test_logout_success(client: AsyncClient, test_user: User) -> None:
    """Tests user logout endpoint."""
    access_token = create_access_token(str(test_user.uuid))
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "Logged out successfully"


@pytest.mark.anyio
async def test_refresh_token_success(client: AsyncClient, test_user: User) -> None:
    """Tests token refresh lifecycle."""
    refresh_token = create_refresh_token(str(test_user.uuid))
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert "refresh_token" in json_data


@pytest.mark.anyio
async def test_refresh_token_failure_invalid(client: AsyncClient) -> None:
    """Tests refresh endpoint with malformed/invalid refresh token."""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.refresh.token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


@pytest.mark.anyio
async def test_me_profile_success(client: AsyncClient, test_user: User) -> None:
    """Tests profile details endpoint (/me) with valid token."""
    access_token = create_access_token(str(test_user.uuid))
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["email"] == "authuser@example.com"
    assert json_data["username"] == "authuser"


@pytest.mark.anyio
async def test_me_profile_unauthorized(client: AsyncClient) -> None:
    """Tests profile endpoint without credentials."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_rbac_dependencies(test_user: User) -> None:
    """Tests the RBAC dependencies directly in isolation."""
    # Active User Check
    test_user.is_active = True
    active_user = await get_current_active_user(test_user)
    assert active_user == test_user

    test_user.is_active = False
    with pytest.raises(HTTPException) as exc:
        await get_current_active_user(test_user)
    assert exc.value.status_code == 400

    # Reset active status for role checks
    test_user.is_active = True

    # require_super_admin
    test_user.role = UserRole.SUPER_ADMIN
    res = await require_super_admin(test_user)
    assert res == test_user

    test_user.role = UserRole.SECURITY_ANALYST
    with pytest.raises(HTTPException) as exc:
        await require_super_admin(test_user)
    assert exc.value.status_code == 403

    # require_org_admin
    test_user.role = UserRole.ORGANIZATION_ADMIN
    res = await require_org_admin(test_user)
    assert res == test_user

    test_user.role = UserRole.READ_ONLY
    with pytest.raises(HTTPException) as exc:
        await require_org_admin(test_user)
    assert exc.value.status_code == 403
