"""
Agent SQLAlchemy model.
Represents an AI Agent with role configuration.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from project.app.database import Base

if TYPE_CHECKING:
    from project.app.models.conversation import Conversation


class Agent(Base):
    """
    Agent model representing an AI assistant with specific role settings.
    
    Attributes:
        id: Primary key, auto-increment
        name: Agent name, required
        system_prompt: System prompt defining agent behavior
        description: Optional description
        created_at: Creation timestamp
        updated_at: Last update timestamp
        conversations: Related conversations (cascade delete)
    """
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    system_prompt: Mapped[str] = mapped_column(
        Text, 
        nullable=False, 
        default="You are a helpful assistant."
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    # Relationship: Agent has many Conversations (cascade delete)
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation",
        back_populates="agent",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name='{self.name}')>"
