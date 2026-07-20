import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

import app.db.session as db_session_module
from app.core.config import settings
from app.main import app

# Override engine with NullPool to prevent pooling errors when event loops close
test_engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    future=True,
)
db_session_module.engine = test_engine
db_session_module.AsyncSessionLocal.configure(bind=test_engine)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """Creates a session-wide event loop for running asynchronous tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Specifies anyio backend type."""
    return "asyncio"


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    """Fixture supplying an asynchronous test client for FastAPI routes."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def cleanup_db():
    """Session-scoped fixture to dispose the test engine when all tests complete."""
    yield
    await test_engine.dispose()
