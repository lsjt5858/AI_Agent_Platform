"""
Conversation Repository - Data Access Layer for Conversation operations.
Implements CRUD operations for Conversation model.
"""

from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from project.app.models.conversation import Conversation
from project.app.models.message import Message
from project.app.schemas.conversation import ConversationCreate


class ConversationRepository:
    """
    Repository for Conversation database operations.
    
    Provides async CRUD methods for Conversation model.
    Requirements: 2.1, 2.4, 2.5
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def create(self, agent_id: int, data: Optional[ConversationCreate] = None) -> Conversation:
        """
        Create a new Conversation for an Agent.
        
        Args:
            agent_id: ID of the Agent this conversation belongs to
            data: Optional ConversationCreate schema with title
            
        Returns:
            Created Conversation instance
            
        Requirements: 2.1
        """
        conversation = Conversation(
            agent_id=agent_id,
            title=data.title if data else None
        )
        self.session.add(conversation)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def get_by_agent(self, agent_id: int) -> List[Conversation]:
        """
        Get all Conversations for a specific Agent.
        
        Args:
            agent_id: Agent primary key
            
        Returns:
            List of Conversation instances for the agent
            
        Requirements: 2.4
        """
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.agent_id == agent_id)
            .order_by(Conversation.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """
        Get Conversation by ID.
        
        Args:
            conversation_id: Conversation primary key
            
        Returns:
            Conversation instance if found, None otherwise
            
        Requirements: 2.4
        """
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, conversation_id: int) -> bool:
        """
        Delete a Conversation and all associated messages (cascade).
        
        Args:
            conversation_id: Conversation primary key
            
        Returns:
            True if deleted, False if not found
            
        Requirements: 2.5
        """
        conversation = await self.get_by_id(conversation_id)
        if conversation is None:
            return False

        await self.session.delete(conversation)
        await self.session.flush()
        return True

    async def get_message_count(self, conversation_id: int) -> int:
        """
        Get the number of messages in a conversation.
        
        Args:
            conversation_id: Conversation primary key
            
        Returns:
            Number of messages in the conversation
        """
        result = await self.session.execute(
            select(func.count(Message.id))
            .where(Message.conversation_id == conversation_id)
        )
        return result.scalar() or 0
