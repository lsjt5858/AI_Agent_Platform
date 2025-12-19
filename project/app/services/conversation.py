"""
Conversation Service - Business logic layer for Conversation operations.
Encapsulates repository calls and adds business validation.

Requirements: 2.1, 2.4, 2.5
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.conversation import Conversation
from ..repositories.agent import AgentRepository
from ..repositories.conversation import ConversationRepository
from ..schemas.conversation import ConversationCreate, ConversationResponse


class ConversationNotFoundError(Exception):
    """Exception raised when a Conversation is not found."""
    
    def __init__(self, conversation_id: int):
        self.conversation_id = conversation_id
        super().__init__(f"Conversation with id {conversation_id} not found")


class AgentNotFoundError(Exception):
    """Exception raised when an Agent is not found."""
    
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        super().__init__(f"Agent with id {agent_id} not found")


class ConversationService:
    """
    Service layer for Conversation business logic.
    
    Encapsulates ConversationRepository calls and provides business validation.
    Requirements: 2.1, 2.4, 2.5
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize ConversationService with database session.
        
        Args:
            session: AsyncSession for database operations
        """
        self.repository = ConversationRepository(session)
        self.agent_repository = AgentRepository(session)
        self.session = session

    async def create_conversation(
        self, 
        agent_id: int, 
        data: Optional[ConversationCreate] = None
    ) -> Conversation:
        """
        Create a new Conversation for an Agent.
        
        Args:
            agent_id: ID of the Agent this conversation belongs to
            data: Optional ConversationCreate schema with title
            
        Returns:
            Created Conversation instance
            
        Raises:
            AgentNotFoundError: If agent not found
            
        Requirements: 2.1
        """
        # Verify agent exists
        agent = await self.agent_repository.get_by_id(agent_id)
        if agent is None:
            raise AgentNotFoundError(agent_id)
        
        conversation = await self.repository.create(agent_id, data)
        await self.session.commit()
        return conversation

    async def get_conversations(self, agent_id: int) -> List[ConversationResponse]:
        """
        Get all Conversations for a specific Agent with message counts.
        
        Args:
            agent_id: Agent primary key
            
        Returns:
            List of ConversationResponse with message counts
            
        Raises:
            AgentNotFoundError: If agent not found
            
        Requirements: 2.4
        """
        # Verify agent exists
        agent = await self.agent_repository.get_by_id(agent_id)
        if agent is None:
            raise AgentNotFoundError(agent_id)
        
        conversations = await self.repository.get_by_agent(agent_id)
        
        # Build response with message counts
        result = []
        for conv in conversations:
            message_count = await self.repository.get_message_count(conv.id)
            result.append(ConversationResponse(
                id=conv.id,
                agent_id=conv.agent_id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=message_count
            ))
        
        return result

    async def get_conversation(self, conversation_id: int) -> Conversation:
        """
        Get Conversation by ID.
        
        Args:
            conversation_id: Conversation primary key
            
        Returns:
            Conversation instance
            
        Raises:
            ConversationNotFoundError: If conversation not found
            
        Requirements: 2.4
        """
        conversation = await self.repository.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)
        return conversation

    async def delete_conversation(self, conversation_id: int) -> bool:
        """
        Delete a Conversation and all associated messages (cascade).
        
        Args:
            conversation_id: Conversation primary key
            
        Returns:
            True if deleted
            
        Raises:
            ConversationNotFoundError: If conversation not found
            
        Requirements: 2.5
        """
        deleted = await self.repository.delete(conversation_id)
        if not deleted:
            raise ConversationNotFoundError(conversation_id)
        await self.session.commit()
        return True


def get_conversation_service(session: AsyncSession) -> ConversationService:
    """
    Factory function to create ConversationService instance.
    
    Args:
        session: AsyncSession for database operations
        
    Returns:
        ConversationService instance
    """
    return ConversationService(session)
