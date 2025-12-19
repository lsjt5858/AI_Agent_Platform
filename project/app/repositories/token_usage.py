"""
Token Usage Repository module.
Handles database operations for TokenUsage entities.
"""

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models.token_usage import TokenUsage


class TokenUsageRepository:
    """
    Repository for TokenUsage database operations.

    Provides CRUD operations and aggregation queries for token usage tracking.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize TokenUsageRepository with database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def create(
        self,
        conversation_id: int,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int
    ) -> TokenUsage:
        """
        Create a new TokenUsage record.

        Args:
            conversation_id: ID of the conversation
            model: Model name used
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            total_tokens: Total number of tokens

        Returns:
            Created TokenUsage instance
        """
        token_usage = TokenUsage(
            conversation_id=conversation_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens
        )

        self.session.add(token_usage)
        return token_usage

    async def get_by_conversation(self, conversation_id: int) -> List[TokenUsage]:
        """
        Get all token usage records for a conversation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            List of TokenUsage instances ordered by created_at
        """
        stmt = select(TokenUsage).where(
            TokenUsage.conversation_id == conversation_id
        ).order_by(TokenUsage.created_at)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_total_tokens_by_conversation(self, conversation_id: int) -> int:
        """
        Get total tokens used for a conversation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            Total number of tokens used
        """
        stmt = select(func.sum(TokenUsage.total_tokens)).where(
            TokenUsage.conversation_id == conversation_id
        )

        result = await self.session.execute(stmt)
        total = result.scalar() or 0
        return total

    async def get_total_tokens_by_agent(self, agent_id: int) -> int:
        """
        Get total tokens used for all conversations of an agent.

        Args:
            agent_id: ID of the agent

        Returns:
            Total number of tokens used across all conversations
        """
        from ..models.conversation import Conversation

        stmt = select(func.sum(TokenUsage.total_tokens)).join(
            Conversation, TokenUsage.conversation_id == Conversation.id
        ).where(Conversation.agent_id == agent_id)

        result = await self.session.execute(stmt)
        total = result.scalar() or 0
        return total