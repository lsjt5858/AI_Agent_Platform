"""
Token Usage SQLAlchemy model.
Tracks token consumption for LLM API calls.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .conversation import Conversation


class TokenUsage(Base):
    """
    TokenUsage model tracking token consumption for API calls.

    Attributes:
        id: Primary key, auto-increment
        conversation_id: Foreign key to Conversation
        model: Model name used for the request
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        total_tokens: Total number of tokens used
        created_at: Timestamp of the API call
        conversation: Related Conversation
    """
    __tablename__ = "token_usage"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )
    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    prompt_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    completion_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    total_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    # Relationship: TokenUsage belongs to Conversation
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="token_usage"
    )

    def __repr__(self) -> str:
        return f"<TokenUsage(id={self.id}, total_tokens={self.total_tokens})>"