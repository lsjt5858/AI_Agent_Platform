"""
Message Repository - Data Access Layer for Message operations.
Implements CRUD operations for Message model.
"""

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from project.app.models.message import Message


class MessageRepository:
    """
    Repository for Message database operations.
    
    Provides async CRUD methods for Message model.
    Requirements: 2.2, 2.3
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def create(self, conversation_id: int, role: str, content: str) -> Message:
        """
        Create a new Message in a Conversation.
        
        Args:
            conversation_id: ID of the Conversation this message belongs to
            role: Message role (user/assistant/system)
            content: Message content
            
        Returns:
            Created Message instance
            
        Requirements: 2.2
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def get_by_conversation(self, conversation_id: int) -> List[Message]:
        """
        Get all Messages for a specific Conversation in chronological order.
        
        Args:
            conversation_id: Conversation primary key
            
        Returns:
            List of Message instances ordered by created_at ascending
            
        Requirements: 2.3
        """
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())
