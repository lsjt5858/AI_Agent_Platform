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
from ..schemas.token_usage import TokenUsageResponse, ConversationTokenUsage
from ..services.message import (
    ConversationNotFoundError,
    MessageService,
    get_message_service,
)

router = APIRouter(tags=["消息管理"])


async def get_service(session: AsyncSession = Depends(get_db)) -> MessageService:
    """获取 MessageService 实例的依赖注入。"""
    return get_message_service(session)


class SendMessageResponse:
    """发送消息端点的响应模型。"""
    user_message: MessageResponse
    assistant_message: MessageResponse


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="发送消息",
    description="发送用户消息并接收AI响应。需求：2.2"
)
async def send_message(
    conversation_id: int,
    data: MessageCreate,
    service: MessageService = Depends(get_service)
) -> APIResponse[dict]:
    """
    在对话中发送消息。

    将用户消息连同对话上下文一起发送给LLM，并返回用户消息和AI响应。

    - **conversation_id**: 对话ID
    - **content**: 消息内容（必填，非空）

    需求：2.2
    """
    try:
        user_message, assistant_message = await service.send_message(
            conversation_id=conversation_id,
            content=data.content
        )
        # 获取最新的token使用记录
        token_records = await service.token_usage_repository.get_by_conversation(conversation_id)
        latest_token_usage = None
        if token_records:
            latest_token_usage = TokenUsageResponse.model_validate(token_records[-1])

        return APIResponse.ok({
            "user_message": MessageResponse.model_validate(user_message).model_dump(),
            "assistant_message": MessageResponse.model_validate(assistant_message).model_dump(),
            "token_usage": latest_token_usage.model_dump() if latest_token_usage else None
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
    summary="获取消息历史",
    description="按时间顺序获取对话中的所有消息。需求：2.3"
)
async def get_messages(
    conversation_id: int,
    service: MessageService = Depends(get_service)
) -> APIResponse[List[MessageResponse]]:
    """
    获取对话的所有消息。

    按时间顺序返回消息（按创建时间升序排列）。

    需求：2.3
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


@router.get(
    "/conversations/{conversation_id}/token-usage",
    response_model=APIResponse[ConversationTokenUsage],
    summary="获取对话的Token使用统计",
    description="获取特定对话的Token使用详细统计。"
)
async def get_conversation_token_usage(
    conversation_id: int,
    service: MessageService = Depends(get_service)
) -> APIResponse[ConversationTokenUsage]:
    """
    获取对话的Token使用统计。

    返回对话的总Token使用量、消息数量和详细的Token使用记录。

    Args:
        conversation_id: 对话ID

    Returns:
        对话的Token使用统计信息
    """
    try:
        # 验证对话存在
        conversation = await service.conversation_repository.get_by_id(conversation_id)
        if conversation is None:
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

        # 获取Token使用记录
        token_records = await service.token_usage_repository.get_by_conversation(conversation_id)
        total_tokens = await service.token_usage_repository.get_total_tokens_by_conversation(conversation_id)

        # 获取消息数量
        messages = await service.message_repository.get_by_conversation(conversation_id)
        message_count = len(messages)

        token_usage_response = ConversationTokenUsage(
            conversation_id=conversation_id,
            title=conversation.title,
            total_tokens=total_tokens,
            message_count=message_count,
            token_usage_records=[
                TokenUsageResponse.model_validate(record)
                for record in token_records
            ]
        )

        return APIResponse.ok(token_usage_response)

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
