"""
Agent Pydantic schemas for API data validation and serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AgentCreate(BaseModel):
    """创建新智能体的模式。"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="智能体名称，必填且非空"
    )
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="定义智能体行为的系统提示"
    )
    description: Optional[str] = Field(
        default=None,
        description="可选的智能体描述"
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_whitespace(cls, v: str) -> str:
        """验证名称不能只是空白字符。"""
        if not v.strip():
            raise ValueError("智能体名称不能为空或仅包含空白字符")
        return v.strip()


class AgentUpdate(BaseModel):
    """更新现有智能体的模式。"""

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="智能体名称"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="定义智能体行为的系统提示"
    )
    description: Optional[str] = Field(
        default=None,
        description="可选的智能体描述"
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """如果提供了名称，验证其不能只是空白字符。"""
        if v is not None and not v.strip():
            raise ValueError("智能体名称不能为空或仅包含空白字符")
        return v.strip() if v is not None else None


class AgentResponse(BaseModel):
    """智能体API响应的模式。"""

    id: int
    name: str
    system_prompt: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
