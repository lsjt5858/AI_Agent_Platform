"""
Conversation Router - API endpoints for Conversation management.

Implements RESTful endpoints for Conversation CRUD operations.
Requirements: 2.1, 2.4, 2.5, 5.1
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from project.app.database import get_db
from project.app.schemas.conversation import (
    ConversationCreate,
    ConversationDetail,
    ConversationResponse,
)
from project.app.schemas.response import APIResponse
from project.app.services.conversation import (
    AgentNotFoundError,
    ConversationNotFoundError,
    ConversationService,
    get_conversation_service,
)

router = APIRouter(tags=["conversations"])


async def get_service(session: AsyncSession = Depends(get_db)) -> ConversationService:
    """Dependency to get ConversationService instance."""
    return get_conversation_service(session)


@router.post(
    "/agents/{agent_id}/conversations",
    response_model=APIResponse[ConversationDetail],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Conversation",
    description="Create a new conversation for a specific Agent. Requirements: 2.1"
)
async def create_conversation(
    agent_id: int,
    data: ConversationCreate = None,
    service: ConversationService = Depends(get_service)
) -> APIResponse[ConversationDetail]:
    """
    Create a new Conversation for an Agent.
    
    - **agent_id**: ID of the Agent this conversation belongs to
    - **title**: Optional conversation title
    
    Requirements: 2.1
    """
    try:
        conversation = await service.create_conversation(agent_id, data)
        return APIResponse.ok(ConversationDetail.model_validate(conversation))
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


@router.get(
    "/agents/{agent_id}/conversations",
    response_model=APIResponse[List[ConversationResponse]],
    summary="Get Conversations for Agent",
    description="Retrieve all conversations for a specific Agent. Requirements: 2.4"
)
async def get_conversations(
    agent_id: int,
    service: ConversationService = Depends(get_service)
) -> APIResponse[List[ConversationResponse]]:
    """
    Get all Conversations for an Agent.
    
    Returns a list of conversations with summary information including message counts.
    
    Requirements: 2.4
    """
    try:
        conversations = await service.get_conversations(agent_id)
        return APIResponse.ok(conversations)
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


@router.get(
    "/conversations/{conversation_id}",
    response_model=APIResponse[ConversationDetail],
    summary="Get Conversation by ID",
    description="Retrieve a specific Conversation by its ID. Requirements: 2.4"
)
async def get_conversation(
    conversation_id: int,
    service: ConversationService = Depends(get_service)
) -> APIResponse[ConversationDetail]:
    """
    Get Conversation by ID.
    
    Returns the conversation details.
    
    Requirements: 2.4
    """
    try:
        conversation = await service.get_conversation(conversation_id)
        return APIResponse.ok(ConversationDetail.model_validate(conversation))
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Conversation with id {conversation_id} not found"
                }
            }
        )


@router.delete(
    "/conversations/{conversation_id}",
    response_model=APIResponse[dict],
    summary="Delete Conversation",
    description="Delete a Conversation and all its messages. Requirements: 2.5"
)
async def delete_conversation(
    conversation_id: int,
    service: ConversationService = Depends(get_service)
) -> APIResponse[dict]:
    """
    Delete a Conversation.
    
    Removes the Conversation and all its messages from the system.
    
    Requirements: 2.5
    """
    try:
        await service.delete_conversation(conversation_id)
        return APIResponse.ok({"deleted": True, "conversation_id": conversation_id})
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Conversation with id {conversation_id} not found"
                }
            }
        )
