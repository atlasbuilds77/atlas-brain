"""
Pytest configuration and fixtures for Kronos tests
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.core.config import settings


# Test database URL - use separate database for tests
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/kronos_test"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

# Create test session factory
TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Override the get_db dependency for testing
    """
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create an event loop for the test session
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    """
    Set up test database before tests and tear down after
    """
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test
    """
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture
def client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """
    Create a test client with overridden dependencies
    """
    # Override the get_db dependency
    app.dependency_overrides[get_db] = lambda: db_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    """
    Get authentication headers for tests
    """
    # Create test user and get token
    # This would be implemented based on your auth system
    return {"Authorization": "Bearer test_token"}


# Test data fixtures
@pytest.fixture
def test_user_data() -> dict:
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": "admin",
    }


@pytest.fixture
def test_lead_data() -> dict:
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "source": "website",
        "status": "new",
        "notes": "Test lead",
    }


@pytest.fixture
def test_client_data() -> dict:
    return {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "+0987654321",
        "client_since": "2024-01-01",
        "status": "active",
    }