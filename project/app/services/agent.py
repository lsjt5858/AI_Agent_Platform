"""
Agent Service - Business logic layer for Agent operations.
Encapsulates repository calls and adds business validation.

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from project.app.models.agent import Agent
from project.app.repositories.agent import AgentRepository
from project.app.schemas.agent import AgentCreate, AgentUpdate


class AgentNotFoundError(Exception):
    """Exception raised when an Agent is not found."""
    
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        super().__init__(f"Agent with id {agent_id} not found")


class AgentService:
    """
    Service layer for Agent business logic.
    
    Encapsulates AgentRepository calls and provides business validation.
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize AgentService with database session.
        
        Args:
            session: AsyncSession for database operations
        """
        self.repository = AgentRepository(session)
        self.session = session

    async def create_agent(self, data: AgentCreate) -> Agent:
        """
        Create a new Agent.
        
        Args:
            data: AgentCreate schema with agent details
            
        Returns:
            Created Agent instance
            
        Requirements: 1.1
        """
        agent = await self.repository.create(data)
        await self.session.commit()
        return agent

    async def get_agents(self) -> List[Agent]:
        """
        Get all Agents.
        
        Returns:
            List of all Agent instances
            
        Requirements: 1.2
        """
        return await self.repository.get_all()

    async def get_agent(self, agent_id: int) -> Agent:
        """
        Get Agent by ID.
        
        Args:
            agent_id: Agent primary key
            
        Returns:
            Agent instance
            
        Raises:
            AgentNotFoundError: If agent not found
            
        Requirements: 1.3
        """
        agent = await self.repository.get_by_id(agent_id)
        if agent is None:
            raise AgentNotFoundError(agent_id)
        return agent

    async def update_agent(self, agent_id: int, data: AgentUpdate) -> Agent:
        """
        Update an existing Agent.
        
        Args:
            agent_id: Agent primary key
            data: AgentUpdate schema with fields to update
            
        Returns:
            Updated Agent instance
            
        Raises:
            AgentNotFoundError: If agent not found
            
        Requirements: 1.4
        """
        agent = await self.repository.update(agent_id, data)
        if agent is None:
            raise AgentNotFoundError(agent_id)
        await self.session.commit()
        return agent

    async def delete_agent(self, agent_id: int) -> bool:
        """
        Delete an Agent and all associated conversations (cascade).
        
        Args:
            agent_id: Agent primary key
            
        Returns:
            True if deleted
            
        Raises:
            AgentNotFoundError: If agent not found
            
        Requirements: 1.5
        """
        deleted = await self.repository.delete(agent_id)
        if not deleted:
            raise AgentNotFoundError(agent_id)
        await self.session.commit()
        return True


def get_agent_service(session: AsyncSession) -> AgentService:
    """
    Factory function to create AgentService instance.
    
    Args:
        session: AsyncSession for database operations
        
    Returns:
        AgentService instance
    """
    return AgentService(session)
