"""
Token Usage Pydantic schemas for API data validation and serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TokenUsageResponse(BaseModel):
    """Token使用统计响应的模式。"""

    id: int
    conversation_id: int
    model: str
    prompt_tokens: int = Field(description="提示词的token数量")
    completion_tokens: int = Field(description="回复内容的token数量")
    total_tokens: int = Field(description="总token数量")
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenUsageSummary(BaseModel):
    """Token使用摘要的模式。"""

    total_tokens: int = Field(description="总token使用量")
    total_requests: int = Field(description="总请求次数")
    average_tokens_per_request: float = Field(description="平均每次请求的token数")
    model_usage: dict[str, int] = Field(description="按模型分组的token使用量")


class ConversationTokenUsage(BaseModel):
    """对话Token使用的详细信息。"""

    conversation_id: int
    title: Optional[str]
    total_tokens: int = Field(description="该对话的总token使用量")
    message_count: int = Field(description="消息数量")
    token_usage_records: list[TokenUsageResponse] = Field(description="Token使用记录列表")