"""
Conversation Pydantic schemas for API data validation and serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    """Schema for creating a new Conversation."""
    
    title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional conversation title"
    )


class ConversationResponse(BaseModel):
    """Schema for Conversation API response."""
    
    id: int
    agent_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = Field(
        default=0,
        description="Number of messages in the conversation"
    )

    model_config = {"from_attributes": True}


class ConversationDetail(BaseModel):
    """Schema for detailed Conversation response with messages."""
    
    id: int
    agent_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
