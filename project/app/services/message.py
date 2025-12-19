"""
Message Service - Business logic layer for Message operations.
Integrates LLM service and handles message context building.

Requirements: 2.2, 2.3, 2.6, 3.1
"""

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.message import Message
from ..repositories.agent import AgentRepository
from ..repositories.conversation import ConversationRepository
from ..repositories.message import MessageRepository
from .llm import LLMService, get_llm_service


class ConversationNotFoundError(Exception):
    """Exception raised when a Conversation is not found."""
    
    def __init__(self, conversation_id: int):
        self.conversation_id = conversation_id
        super().__init__(f"Conversation with id {conversation_id} not found")


class MessageService:
    """
    Service layer for Message business logic.
    
    Integrates LLM service for AI responses and manages message context.
    Requirements: 2.2, 2.3, 2.6, 3.1
    """

    def __init__(
        self, 
        session: AsyncSession,
        llm_service: LLMService | None = None
    ):
        """
        Initialize MessageService with database session and LLM service.
        
        Args:
            session: AsyncSession for database operations
            llm_service: Optional LLMService instance (defaults to singleton)
        """
        self.message_repository = MessageRepository(session)
        self.conversation_repository = ConversationRepository(session)
        self.agent_repository = AgentRepository(session)
        self.llm_service = llm_service or get_llm_service()
        self.session = session

    def _build_message_context(self, messages: List[Message]) -> List[dict]:
        """
        Build message context for LLM from conversation history.
        
        Converts Message objects to dict format expected by LLM service.
        
        Args:
            messages: List of Message objects in chronological order
            
        Returns:
            List of message dicts with 'role' and 'content' keys
            
        Requirements: 2.6, 3.1
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    async def send_message(
        self, 
        conversation_id: int, 
        content: str
    ) -> tuple[Message, Message]:
        """
        Send a user message and get AI response.
        
        Flow:
        1. Verify conversation exists
        2. Save user message
        3. Build context from conversation history
        4. Call LLM with context and system prompt
        5. Save and return AI response
        
        Args:
            conversation_id: Conversation primary key
            content: User message content
            
        Returns:
            Tuple of (user_message, assistant_message)
            
        Raises:
            ConversationNotFoundError: If conversation not found
            
        Requirements: 2.2, 2.6, 3.1
        """
        # Verify conversation exists and get agent info
        conversation = await self.conversation_repository.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)
        
        # Get agent for system prompt
        agent = await self.agent_repository.get_by_id(conversation.agent_id)
        system_prompt = agent.system_prompt if agent else "You are a helpful assistant."
        
        # Save user message
        user_message = await self.message_repository.create(
            conversation_id=conversation_id,
            role="user",
            content=content
        )
        
        # Get conversation history for context (Requirements: 2.6, 3.1)
        messages = await self.message_repository.get_by_conversation(conversation_id)
        message_context = self._build_message_context(messages)
        
        # Call LLM service
        ai_response = await self.llm_service.chat(
            messages=message_context,
            system_prompt=system_prompt
        )
        
        # Save assistant message
        assistant_message = await self.message_repository.create(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response
        )
        
        await self.session.commit()
        
        return user_message, assistant_message

    async def get_messages(self, conversation_id: int) -> List[Message]:
        """
        Get all messages for a conversation in chronological order.
        
        Args:
            conversation_id: Conversation primary key
            
        Returns:
            List of Message instances ordered by created_at ascending
            
        Raises:
            ConversationNotFoundError: If conversation not found
            
        Requirements: 2.3
        """
        # Verify conversation exists
        conversation = await self.conversation_repository.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)
        
        return await self.message_repository.get_by_conversation(conversation_id)


def get_message_service(
    session: AsyncSession,
    llm_service: LLMService | None = None
) -> MessageService:
    """
    Factory function to create MessageService instance.
    
    Args:
        session: AsyncSession for database operations
        llm_service: Optional LLMService instance
        
    Returns:
        MessageService instance
    """
    return MessageService(session, llm_service)
