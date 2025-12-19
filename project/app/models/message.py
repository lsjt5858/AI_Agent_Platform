"""
Message SQLAlchemy model.
Represents a single message in a conversation.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from project.app.database import Base

if TYPE_CHECKING:
    from project.app.models.conversation import Conversation


class Message(Base):
    """
    Message model representing a single message in a conversation.
    
    Attributes:
        id: Primary key, auto-increment
        conversation_id: Foreign key to Conversation
        role: Message role (user/assistant/system)
        content: Message content
        created_at: Creation timestamp
        conversation: Related Conversation
    """
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    # Relationship: Message belongs to Conversation
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role='{self.role}')>"
