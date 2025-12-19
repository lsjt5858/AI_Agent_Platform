"""
Message Router - API endpoints for Message operations.

Implements RESTful endpoints for sending messages and retrieving history.
Requirements: 2.2, 2.3, 5.1
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.message import MessageCreate, MessageResponse
from ..schemas.response import APIResponse
from ..services.message import (
    ConversationNotFoundError,
    MessageService,
    get_message_service,
)

router = APIRouter(tags=["messages"])


async def get_service(session: AsyncSession = Depends(get_db)) -> MessageService:
    """Dependency to get MessageService instance."""
    return get_message_service(session)


class SendMessageResponse:
    """Response model for send message endpoint."""
    user_message: MessageResponse
    assistant_message: MessageResponse


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Send a message",
    description="Send a user message and receive AI response. Requirements: 2.2"
)
async def send_message(
    conversation_id: int,
    data: MessageCreate,
    service: MessageService = Depends(get_service)
) -> APIResponse[dict]:
    """
    Send a message in a conversation.
    
    Sends the user message to the LLM with conversation context and returns
    both the user message and the AI response.
    
    - **conversation_id**: ID of the conversation
    - **content**: Message content (required, non-empty)
    
    Requirements: 2.2
    """
    try:
        user_message, assistant_message = await service.send_message(
            conversation_id=conversation_id,
            content=data.content
        )
        return APIResponse.ok({
            "user_message": MessageResponse.model_validate(user_message).model_dump(),
            "assistant_message": MessageResponse.model_validate(assistant_message).model_dump()
        })
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


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=APIResponse[List[MessageResponse]],
    summary="Get message history",
    description="Retrieve all messages in a conversation in chronological order. Requirements: 2.3"
)
async def get_messages(
    conversation_id: int,
    service: MessageService = Depends(get_service)
) -> APIResponse[List[MessageResponse]]:
    """
    Get all messages for a conversation.
    
    Returns messages in chronological order (ascending by created_at).
    
    Requirements: 2.3
    """
    try:
        messages = await service.get_messages(conversation_id)
        return APIResponse.ok([MessageResponse.model_validate(m) for m in messages])
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
