"""
Prompt model

Represents a query prompt used in an analysis.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from core.database import Base


class Prompt(Base):
    """
    Query prompt entity

    Represents a prompt that will be sent to AI providers for analysis.
    Can be either AI-suggested or user-added custom prompts.

    Constraints:
    - Maximum 7 prompts per analysis (enforced in service layer)
    - Unique prompt text within an analysis (enforced in service layer)
    """
    __tablename__ = "prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    analysis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    text = Column(Text, nullable=False)
    is_suggested = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="prompts")
    ai_responses = relationship(
        "AIResponse",
        back_populates="prompt",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        suggested_flag = "AI" if self.is_suggested else "Custom"
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"<Prompt(id={self.id}, type={suggested_flag}, text='{preview}')>"
