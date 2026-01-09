"""
Citation model

Represents a citation/source from an AI response.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from core.database import Base


class SourceType(str, enum.Enum):
    """Citation source type"""
    WEB = "web"  # Web page
    ACADEMIC = "academic"  # Academic paper
    NEWS = "news"  # News article
    DOCUMENTATION = "documentation"  # Technical documentation
    OTHER = "other"  # Other source type


class ValidityStatus(str, enum.Enum):
    """Citation validity status"""
    VALID = "valid"  # URL is accessible
    BROKEN = "broken"  # URL returns 404 or other error
    UNKNOWN = "unknown"  # Not yet validated


class Citation(Base):
    """
    Citation/source entity

    Represents a single citation provided by an AI provider.
    Tracks URL, title, snippet, and validity status.
    """
    __tablename__ = "citations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    ai_response_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_responses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Citation details
    url = Column(Text, nullable=False)  # Full URL
    title = Column(String(500), nullable=True)  # Page/document title
    snippet = Column(Text, nullable=True)  # Relevant excerpt

    # Classification
    source_type = Column(
        SQLEnum(SourceType, name="source_type"),
        default=SourceType.WEB,
        nullable=False
    )

    # Validation
    validity_status = Column(
        SQLEnum(ValidityStatus, name="validity_status"),
        default=ValidityStatus.UNKNOWN,
        nullable=False
    )

    # Position in response (0-indexed)
    position = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ai_response = relationship("AIResponse", back_populates="citations")

    def __repr__(self) -> str:
        return f"<Citation(id={self.id}, url={self.url[:50]}, position={self.position})>"
