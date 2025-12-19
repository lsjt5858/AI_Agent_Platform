"""
Conversation Pydantic schemas for API data validation and serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    """创建新对话的模式。"""

    title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="可选的对话标题"
    )


class ConversationResponse(BaseModel):
    """对话API响应的模式。"""

    id: int
    agent_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = Field(
        default=0,
        description="对话中的消息数量"
    )

    model_config = {"from_attributes": True}


class ConversationDetail(BaseModel):
    """包含消息的详细对话响应模式。"""

    id: int
    agent_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
