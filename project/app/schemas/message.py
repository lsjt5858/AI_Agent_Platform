"""
Message Pydantic schemas for API data validation and serialization.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class MessageCreate(BaseModel):
    """Schema for creating a new Message (user input)."""
    
    content: str = Field(
        ...,
        min_length=1,
        description="Message content, required and non-empty"
    )

    @field_validator("content")
    @classmethod
    def content_must_not_be_whitespace(cls, v: str) -> str:
        """Validate that content is not just whitespace."""
        if not v.strip():
            raise ValueError("Message content cannot be empty or whitespace only")
        return v


class MessageResponse(BaseModel):
    """Schema for Message API response."""
    
    id: int
    conversation_id: int
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
