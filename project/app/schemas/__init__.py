"""
Pydantic Schemas Package.

Exports all schemas for API data validation and serialization.
"""

from project.app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from project.app.schemas.conversation import (
    ConversationCreate,
    ConversationDetail,
    ConversationResponse,
)
from project.app.schemas.message import MessageCreate, MessageResponse
from project.app.schemas.response import APIResponse, ErrorDetail

__all__ = [
    # Agent schemas
    "AgentCreate",
    "AgentUpdate",
    "AgentResponse",
    # Conversation schemas
    "ConversationCreate",
    "ConversationResponse",
    "ConversationDetail",
    # Message schemas
    "MessageCreate",
    "MessageResponse",
    # Response schemas
    "APIResponse",
    "ErrorDetail",
]
