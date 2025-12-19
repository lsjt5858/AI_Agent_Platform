"""
Message Pydantic schemas for API data validation and serialization.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class MessageCreate(BaseModel):
    """创建新消息（用户输入）的模式。"""

    content: str = Field(
        ...,
        min_length=1,
        description="消息内容，必填且非空"
    )

    @field_validator("content")
    @classmethod
    def content_must_not_be_whitespace(cls, v: str) -> str:
        """验证内容不能只是空白字符。"""
        if not v.strip():
            raise ValueError("消息内容不能为空或仅包含空白字符")
        return v


class MessageResponse(BaseModel):
    """消息API响应的模式。"""

    id: int
    conversation_id: int
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
