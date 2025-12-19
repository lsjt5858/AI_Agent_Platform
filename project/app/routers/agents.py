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

router = APIRouter(prefix="/agents", tags=["智能体管理"])


async def get_service(session: AsyncSession = Depends(get_db)) -> AgentService:
    """获取 AgentService 实例的依赖注入。"""
    return get_agent_service(session)


@router.post(
    "",
    response_model=APIResponse[AgentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建新的智能体",
    description="创建新的 AI 智能体，包含名称和系统提示。需求：1.1"
)
async def create_agent(
    data: AgentCreate,
    service: AgentService = Depends(get_service)
) -> APIResponse[AgentResponse]:
    """
    创建新的智能体。

    - **name**: 智能体名称（必填，非空）
    - **system_prompt**: 定义智能体行为的系统提示
    - **description**: 可选的智能体描述

    需求：1.1
    """
    agent = await service.create_agent(data)
    return APIResponse.ok(AgentResponse.model_validate(agent))


@router.get(
    "",
    response_model=APIResponse[List[AgentResponse]],
    summary="获取所有智能体",
    description="获取所有智能体的列表。需求：1.2"
)
async def get_agents(
    service: AgentService = Depends(get_service)
) -> APIResponse[List[AgentResponse]]:
    """
    获取所有智能体。

    返回包含所有智能体基本信息的列表。

    需求：1.2
    """
    agents = await service.get_agents()
    return APIResponse.ok([AgentResponse.model_validate(a) for a in agents])


@router.get(
    "/{agent_id}",
    response_model=APIResponse[AgentResponse],
    summary="根据ID获取智能体",
    description="根据ID获取特定的智能体。需求：1.3"
)
async def get_agent(
    agent_id: int,
    service: AgentService = Depends(get_service)
) -> APIResponse[AgentResponse]:
    """
    根据ID获取智能体。

    返回包含配置信息的完整智能体详情。

    需求：1.3
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
    summary="更新智能体",
    description="更新现有智能体的配置。需求：1.4"
)
async def update_agent(
    agent_id: int,
    data: AgentUpdate,
    service: AgentService = Depends(get_service)
) -> APIResponse[AgentResponse]:
    """
    更新现有智能体。

    - **name**: 新的智能体名称（可选）
    - **system_prompt**: 新的系统提示（可选）
    - **description**: 新的描述（可选）

    需求：1.4
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
    summary="删除智能体",
    description="删除智能体及其所有相关对话。需求：1.5"
)
async def delete_agent(
    agent_id: int,
    service: AgentService = Depends(get_service)
) -> APIResponse[dict]:
    """
    删除智能体。

    从系统中移除智能体及其所有相关对话。

    需求：1.5
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
