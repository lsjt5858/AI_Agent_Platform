"""
Agent Repository - Data Access Layer for Agent operations.
Implements CRUD operations for Agent model.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.agent import Agent
from ..schemas.agent import AgentCreate, AgentUpdate


class AgentRepository:
    """
    Repository for Agent database operations.
    
    Provides async CRUD methods for Agent model.
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def create(self, data: AgentCreate) -> Agent:
        """
        Create a new Agent.
        
        Args:
            data: AgentCreate schema with agent details
            
        Returns:
            Created Agent instance
            
        Requirements: 1.1
        """
        agent = Agent(
            name=data.name,
            system_prompt=data.system_prompt,
            description=data.description
        )
        self.session.add(agent)
        await self.session.flush()
        await self.session.refresh(agent)
        return agent

    async def get_all(self) -> List[Agent]:
        """
        Get all Agents.
        
        Returns:
            List of all Agent instances
            
        Requirements: 1.2
        """
        result = await self.session.execute(
            select(Agent).order_by(Agent.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, agent_id: int) -> Optional[Agent]:
        """
        Get Agent by ID.
        
        Args:
            agent_id: Agent primary key
            
        Returns:
            Agent instance if found, None otherwise
            
        Requirements: 1.3
        """
        result = await self.session.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        return result.scalar_one_or_none()

    async def update(self, agent_id: int, data: AgentUpdate) -> Optional[Agent]:
        """
        Update an existing Agent.
        
        Args:
            agent_id: Agent primary key
            data: AgentUpdate schema with fields to update
            
        Returns:
            Updated Agent instance if found, None otherwise
            
        Requirements: 1.4
        """
        agent = await self.get_by_id(agent_id)
        if agent is None:
            return None

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(agent, field, value)

        await self.session.flush()
        await self.session.refresh(agent)
        return agent

    async def delete(self, agent_id: int) -> bool:
        """
        Delete an Agent and all associated conversations (cascade).
        
        Args:
            agent_id: Agent primary key
            
        Returns:
            True if deleted, False if not found
            
        Requirements: 1.5
        """
        agent = await self.get_by_id(agent_id)
        if agent is None:
            return False

        await self.session.delete(agent)
        await self.session.flush()
        return True
