"""
Conversation SQLAlchemy model.
Represents a conversation session between user and an Agent.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .agent import Agent
    from .message import Message
    from .token_usage import TokenUsage


class Conversation(Base):
    """
    Conversation model representing a chat session with an Agent.
    
    Attributes:
        id: Primary key, auto-increment
        agent_id: Foreign key to Agent
        title: Optional conversation title
        created_at: Creation timestamp
        updated_at: Last update timestamp
        agent: Related Agent
        messages: Related messages (cascade delete)
    """
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationship: Conversation belongs to Agent
    agent: Mapped["Agent"] = relationship(
        "Agent",
        back_populates="conversations"
    )

    # Relationship: Conversation has many Messages (cascade delete)
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Message.created_at"
    )

    # Relationship: Conversation has many TokenUsage records (cascade delete)
    token_usage: Mapped[List["TokenUsage"]] = relationship(
        "TokenUsage",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, agent_id={self.agent_id})>"
