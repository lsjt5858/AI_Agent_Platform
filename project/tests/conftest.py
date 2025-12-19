"""
Pytest configuration and fixtures for testing.
Provides test database, async session, and HTTP client fixtures.

Requirements: 4.3, 4.5
- Configures test database (in-memory SQLite)
- Configures async test client
- Handles database transaction rollback for test isolation
"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from project.app.database import Base, get_db
from project.app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_engine():
    """
    Create a test database engine using in-memory SQLite.
    
    Creates all tables at the start and disposes the engine after tests.
    Each test gets a fresh database state.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.
    
    Provides an isolated session for each test with automatic rollback
    to ensure test isolation.
    """
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def test_session_maker(test_engine):
    """
    Create a test session maker for dependency injection.
    
    Returns a session factory that can be used to override
    the get_db dependency in FastAPI.
    """
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@pytest_asyncio.fixture
async def client(test_engine, test_session_maker) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP test client with database dependency override.
    
    This fixture:
    - Overrides the get_db dependency to use the test database
    - Provides an AsyncClient for making HTTP requests to the API
    - Ensures proper cleanup after tests
    """
    
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        """Override database dependency for testing."""
        async with test_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create async client with ASGI transport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def db_with_agent(test_session):
    """
    Fixture that provides a test session with a pre-created agent.
    
    Useful for tests that need an existing agent to work with.
    Returns tuple of (session, agent).
    """
    from project.app.models.agent import Agent
    
    agent = Agent(
        name="Test Agent",
        system_prompt="You are a helpful test assistant.",
        description="A test agent for testing purposes"
    )
    test_session.add(agent)
    await test_session.commit()
    await test_session.refresh(agent)
    
    yield test_session, agent


@pytest_asyncio.fixture
async def db_with_conversation(db_with_agent):
    """
    Fixture that provides a test session with a pre-created conversation.
    
    Useful for tests that need an existing conversation to work with.
    Returns tuple of (session, agent, conversation).
    """
    from project.app.models.conversation import Conversation
    
    session, agent = db_with_agent
    
    conversation = Conversation(
        agent_id=agent.id,
        title="Test Conversation"
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    
    yield session, agent, conversation


@pytest_asyncio.fixture
async def db_with_messages(db_with_conversation):
    """
    Fixture that provides a test session with pre-created messages.
    
    Useful for tests that need existing messages to work with.
    Returns tuple of (session, agent, conversation, messages).
    """
    from project.app.models.message import Message
    
    session, agent, conversation = db_with_conversation
    
    messages = []
    for i, (role, content) in enumerate([
        ("user", "Hello, how are you?"),
        ("assistant", "I'm doing well, thank you! How can I help you today?"),
        ("user", "Can you help me with Python?"),
    ]):
        msg = Message(
            conversation_id=conversation.id,
            role=role,
            content=content
        )
        session.add(msg)
        messages.append(msg)
    
    await session.commit()
    for msg in messages:
        await session.refresh(msg)
    
    yield session, agent, conversation, messages
