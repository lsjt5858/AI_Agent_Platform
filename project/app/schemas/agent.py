"""
Agent Pydantic schemas for API data validation and serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AgentCreate(BaseModel):
    """Schema for creating a new Agent."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Agent name, required and non-empty"
    )
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt defining agent behavior"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional agent description"
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_whitespace(cls, v: str) -> str:
        """Validate that name is not just whitespace."""
        if not v.strip():
            raise ValueError("Agent name cannot be empty or whitespace only")
        return v.strip()


class AgentUpdate(BaseModel):
    """Schema for updating an existing Agent."""
    
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Agent name"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="System prompt defining agent behavior"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional agent description"
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Validate that name is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError("Agent name cannot be empty or whitespace only")
        return v.strip() if v is not None else None


class AgentResponse(BaseModel):
    """Schema for Agent API response."""
    
    id: int
    name: str
    system_prompt: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
