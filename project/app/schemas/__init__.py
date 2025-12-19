"""
Pydantic Schemas Package.

Exports all schemas for API data validation and serialization.
"""

from .agent import AgentCreate, AgentResponse, AgentUpdate
from .conversation import (
    ConversationCreate,
    ConversationDetail,
    ConversationResponse,
)
from .message import MessageCreate, MessageResponse
from .response import APIResponse, ErrorDetail

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
