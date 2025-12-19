"""
Unit tests for repository layer.
Tests basic CRUD operations for Agent, Conversation, and Message repositories.
"""

import pytest
import pytest_asyncio

from project.app.models.agent import Agent
from project.app.models.conversation import Conversation
from project.app.models.message import Message
from project.app.repositories.agent import AgentRepository
from project.app.repositories.conversation import ConversationRepository
from project.app.repositories.message import MessageRepository
from project.app.schemas.agent import AgentCreate, AgentUpdate
from project.app.schemas.conversation import ConversationCreate


class TestAgentRepository:
    """Tests for AgentRepository CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_agent(self, test_session):
        """Test creating an agent."""
        repo = AgentRepository(test_session)
        data = AgentCreate(name="Test Agent", system_prompt="You are a test assistant.")
        
        agent = await repo.create(data)
        await test_session.commit()
        
        assert agent.id is not None
        assert agent.name == "Test Agent"
        assert agent.system_prompt == "You are a test assistant."

    @pytest.mark.asyncio
    async def test_get_agent_by_id(self, test_session):
        """Test retrieving an agent by ID."""
        repo = AgentRepository(test_session)
        data = AgentCreate(name="Retrieve Test", system_prompt="Test prompt")
        
        created = await repo.create(data)
        await test_session.commit()
        
        retrieved = await repo.get_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Retrieve Test"

    @pytest.mark.asyncio
    async def test_get_all_agents(self, test_session):
        """Test retrieving all agents."""
        repo = AgentRepository(test_session)
        
        await repo.create(AgentCreate(name="Agent 1"))
        await repo.create(AgentCreate(name="Agent 2"))
        await test_session.commit()
        
        agents = await repo.get_all()
        
        assert len(agents) >= 2

    @pytest.mark.asyncio
    async def test_update_agent(self, test_session):
        """Test updating an agent."""
        repo = AgentRepository(test_session)
        data = AgentCreate(name="Original Name")
        
        agent = await repo.create(data)
        await test_session.commit()
        
        updated = await repo.update(agent.id, AgentUpdate(name="Updated Name"))
        await test_session.commit()
        
        assert updated is not None
        assert updated.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete_agent(self, test_session):
        """Test deleting an agent."""
        repo = AgentRepository(test_session)
        data = AgentCreate(name="To Delete")
        
        agent = await repo.create(data)
        await test_session.commit()
        
        result = await repo.delete(agent.id)
        await test_session.commit()
        
        assert result is True
        assert await repo.get_by_id(agent.id) is None


class TestConversationRepository:
    """Tests for ConversationRepository CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_conversation(self, test_session):
        """Test creating a conversation."""
        agent_repo = AgentRepository(test_session)
        conv_repo = ConversationRepository(test_session)
        
        agent = await agent_repo.create(AgentCreate(name="Conv Test Agent"))
        await test_session.commit()
        
        conv = await conv_repo.create(agent.id, ConversationCreate(title="Test Conv"))
        await test_session.commit()
        
        assert conv.id is not None
        assert conv.agent_id == agent.id
        assert conv.title == "Test Conv"

    @pytest.mark.asyncio
    async def test_get_conversations_by_agent(self, test_session):
        """Test retrieving conversations by agent."""
        agent_repo = AgentRepository(test_session)
        conv_repo = ConversationRepository(test_session)
        
        agent = await agent_repo.create(AgentCreate(name="Multi Conv Agent"))
        await test_session.commit()
        
        await conv_repo.create(agent.id, ConversationCreate(title="Conv 1"))
        await conv_repo.create(agent.id, ConversationCreate(title="Conv 2"))
        await test_session.commit()
        
        convs = await conv_repo.get_by_agent(agent.id)
        
        assert len(convs) >= 2

    @pytest.mark.asyncio
    async def test_delete_conversation(self, test_session):
        """Test deleting a conversation."""
        agent_repo = AgentRepository(test_session)
        conv_repo = ConversationRepository(test_session)
        
        agent = await agent_repo.create(AgentCreate(name="Delete Conv Agent"))
        await test_session.commit()
        
        conv = await conv_repo.create(agent.id)
        await test_session.commit()
        
        result = await conv_repo.delete(conv.id)
        await test_session.commit()
        
        assert result is True
        assert await conv_repo.get_by_id(conv.id) is None


class TestMessageRepository:
    """Tests for MessageRepository CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_message(self, test_session):
        """Test creating a message."""
        agent_repo = AgentRepository(test_session)
        conv_repo = ConversationRepository(test_session)
        msg_repo = MessageRepository(test_session)
        
        agent = await agent_repo.create(AgentCreate(name="Msg Test Agent"))
        await test_session.commit()
        
        conv = await conv_repo.create(agent.id)
        await test_session.commit()
        
        msg = await msg_repo.create(conv.id, "user", "Hello!")
        await test_session.commit()
        
        assert msg.id is not None
        assert msg.conversation_id == conv.id
        assert msg.role == "user"
        assert msg.content == "Hello!"

    @pytest.mark.asyncio
    async def test_get_messages_by_conversation(self, test_session):
        """Test retrieving messages by conversation in chronological order."""
        agent_repo = AgentRepository(test_session)
        conv_repo = ConversationRepository(test_session)
        msg_repo = MessageRepository(test_session)
        
        agent = await agent_repo.create(AgentCreate(name="Multi Msg Agent"))
        await test_session.commit()
        
        conv = await conv_repo.create(agent.id)
        await test_session.commit()
        
        await msg_repo.create(conv.id, "user", "First message")
        await msg_repo.create(conv.id, "assistant", "Second message")
        await msg_repo.create(conv.id, "user", "Third message")
        await test_session.commit()
        
        messages = await msg_repo.get_by_conversation(conv.id)
        
        assert len(messages) == 3
        # Verify chronological order
        assert messages[0].content == "First message"
        assert messages[1].content == "Second message"
        assert messages[2].content == "Third message"
