"""
Agent Router - API endpoints for Agent management.

Implements RESTful endpoints for Agent CRUD operations.
Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 5.1
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from ..schemas.response import APIResponse
from ..services.agent import AgentNotFoundError, AgentService, get_agent_service

router = APIRouter(prefix="/agents", tags=["agents"])


async def get_service(session: AsyncSession = Depends(get_db)) -> AgentService:
    """Dependency to get AgentService instance."""
    return get_agent_service(session)


@router.post(
    "",
    response_model=APIResponse[AgentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Agent",
    description="Create a new AI Agent with name and system prompt. Requirements: 1.1"
)
async def create_agent(
    data: AgentCreate,
    service: AgentService = Depends(get_service)
) -> APIResponse[AgentResponse]:
    """
    Create a new Agent.
    
    - **name**: Agent name (required, non-empty)
    - **system_prompt**: System prompt defining agent behavior
    - **description**: Optional agent description
    
    Requirements: 1.1
    """
    agent = await service.create_agent(data)
    return APIResponse.ok(AgentResponse.model_validate(agent))


@router.get(
    "",
    response_model=APIResponse[List[AgentResponse]],
    summary="Get all Agents",
    description="Retrieve a list of all Agents. Requirements: 1.2"
)
async def get_agents(
    service: AgentService = Depends(get_service)
) -> APIResponse[List[AgentResponse]]:
    """
    Get all Agents.
    
    Returns a list of all Agents with their basic information.
    
    Requirements: 1.2
    """
    agents = await service.get_agents()
    return APIResponse.ok([AgentResponse.model_validate(a) for a in agents])


@router.get(
    "/{agent_id}",
    response_model=APIResponse[AgentResponse],
    summary="Get Agent by ID",
    description="Retrieve a specific Agent by its ID. Requirements: 1.3"
)
async def get_agent(
    agent_id: int,
    service: AgentService = Depends(get_service)
) -> APIResponse[AgentResponse]:
    """
    Get Agent by ID.
    
    Returns the complete Agent details including configuration.
    
    Requirements: 1.3
    """
    try:
        agent = await service.get_agent(agent_id)
        return APIResponse.ok(AgentResponse.model_validate(agent))
    except AgentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Agent with id {agent_id} not found"
                }
            }
        )


@router.put(
    "/{agent_id}",
    response_model=APIResponse[AgentResponse],
    summary="Update Agent",
    description="Update an existing Agent's configuration. Requirements: 1.4"
)
async def update_agent(
    agent_id: int,
    data: AgentUpdate,
    service: AgentService = Depends(get_service)
) -> APIResponse[AgentResponse]:
    """
    Update an existing Agent.
    
    - **name**: New agent name (optional)
    - **system_prompt**: New system prompt (optional)
    - **description**: New description (optional)
    
    Requirements: 1.4
    """
    try:
        agent = await service.update_agent(agent_id, data)
        return APIResponse.ok(AgentResponse.model_validate(agent))
    except AgentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Agent with id {agent_id} not found"
                }
            }
        )


@router.delete(
    "/{agent_id}",
    response_model=APIResponse[dict],
    summary="Delete Agent",
    description="Delete an Agent and all associated conversations. Requirements: 1.5"
)
async def delete_agent(
    agent_id: int,
    service: AgentService = Depends(get_service)
) -> APIResponse[dict]:
    """
    Delete an Agent.
    
    Removes the Agent and all associated conversations from the system.
    
    Requirements: 1.5
    """
    try:
        await service.delete_agent(agent_id)
        return APIResponse.ok({"deleted": True, "agent_id": agent_id})
    except AgentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Agent with id {agent_id} not found"
                }
            }
        )
