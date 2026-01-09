"""
AIResponse model

Represents an AI provider's response to a prompt with citations.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from core.database import Base


class ProviderType(str, enum.Enum):
    """AI provider types"""
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    PERPLEXITY = "perplexity"
    GOOGLE_AI = "google_ai"
    HUGGINGFACE = "huggingface"


class CitationCoverage(str, enum.Enum):
    """Citation coverage level"""
    NONE = "none"  # No citations provided
    PARTIAL = "partial"  # Some citations provided
    COMPLETE = "complete"  # Comprehensive citations


class ResponseStatus(str, enum.Enum):
    """Response query status"""
    PENDING = "pending"  # Not yet queried
    IN_PROGRESS = "in_progress"  # Currently querying
    SUCCESS = "success"  # Successfully retrieved
    FAILED = "failed"  # Query failed
    TIMEOUT = "timeout"  # Query timed out


class AIResponse(Base):
    """
    AI provider response entity

    Stores the response from a single AI provider for a specific prompt.
    Includes the answer text, model metadata, and citation coverage level.
    """
    __tablename__ = "ai_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    prompt_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prompts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    provider = Column(
        SQLEnum(ProviderType, name="provider_type"),
        nullable=False,
        index=True
    )
    model_name = Column(String(100), nullable=False)  # e.g., "gpt-4", "claude-3-sonnet"

    # Response content (JSON for flexibility with provider-specific formats)
    answer_text = Column(JSON, nullable=False)  # Normalized answer structure

    # Provider-specific metadata
    response_metadata = Column(JSON, default=dict)  # capability_flags, failure_reason, etc.

    # Citation metrics
    citation_coverage = Column(
        SQLEnum(CitationCoverage, name="citation_coverage"),
        default=CitationCoverage.NONE,
        nullable=False
    )

    # Status tracking
    status = Column(
        SQLEnum(ResponseStatus, name="response_status"),
        default=ResponseStatus.PENDING,
        nullable=False,
        index=True
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)  # When query completed/failed

    # Relationships
    citations = relationship(
        "Citation",
        back_populates="ai_response",
        cascade="all, delete-orphan"
    )
    prompt = relationship("Prompt", back_populates="ai_responses")

    def __repr__(self) -> str:
        return f"<AIResponse(id={self.id}, provider={self.provider}, status={self.status})>"
