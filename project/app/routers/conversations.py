"""
Conversation Router - API endpoints for Conversation management.

Implements RESTful endpoints for Conversation CRUD operations.
Requirements: 2.1, 2.4, 2.5, 5.1
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.conversation import (
    ConversationCreate,
    ConversationDetail,
    ConversationResponse,
)
from ..schemas.response import APIResponse
from ..services.conversation import (
    AgentNotFoundError,
    ConversationNotFoundError,
    ConversationService,
    get_conversation_service,
)

router = APIRouter(tags=["对话管理"])


async def get_service(session: AsyncSession = Depends(get_db)) -> ConversationService:
    """获取 ConversationService 实例的依赖注入。"""
    return get_conversation_service(session)


@router.post(
    "/agents/{agent_id}/conversations",
    response_model=APIResponse[ConversationDetail],
    status_code=status.HTTP_201_CREATED,
    summary="创建新对话",
    description="为特定智能体创建新对话。需求：2.1"
)
async def create_conversation(
    agent_id: int,
    data: ConversationCreate = None,
    service: ConversationService = Depends(get_service)
) -> APIResponse[ConversationDetail]:
    """
    为智能体创建新对话。

    - **agent_id**: 此对话所属智能体的ID
    - **title**: 可选的对话标题

    需求：2.1
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
    summary="获取智能体的对话列表",
    description="获取特定智能体的所有对话。需求：2.4"
)
async def get_conversations(
    agent_id: int,
    service: ConversationService = Depends(get_service)
) -> APIResponse[List[ConversationResponse]]:
    """
    获取智能体的所有对话。

    返回包含消息数量等摘要信息的对话列表。

    需求：2.4
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
    summary="根据ID获取对话",
    description="根据ID获取特定对话。需求：2.4"
)
async def get_conversation(
    conversation_id: int,
    service: ConversationService = Depends(get_service)
) -> APIResponse[ConversationDetail]:
    """
    根据ID获取对话。

    返回对话详情。

    需求：2.4
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
    summary="删除对话",
    description="删除对话及其所有消息。需求：2.5"
)
async def delete_conversation(
    conversation_id: int,
    service: ConversationService = Depends(get_service)
) -> APIResponse[dict]:
    """
    删除对话。

    从系统中移除对话及其所有消息。

    需求：2.5
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
