"""Recommendation model for actionable suggestions"""
import enum
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Enum, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class ConfidenceLevel(enum.Enum):
    """Confidence levels for recommendations"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ImpactLevel(enum.Enum):
    """Expected impact levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Recommendation(Base):
    """
    Represents an actionable recommendation derived from insights.

    Recommendations provide concrete suggestions for improving
    brand visibility and competitive positioning.
    """
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    analysis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Recommendation content
    text = Column(Text, nullable=False)  # The recommendation itself
    rationale = Column(Text, nullable=False)  # Why this recommendation is made

    # Impact assessment
    expected_impact = Column(Enum(ImpactLevel), nullable=False, default=ImpactLevel.MEDIUM)
    confidence_level = Column(Enum(ConfidenceLevel), nullable=False, default=ConfidenceLevel.MEDIUM)

    # Evidence linking - JSON array of references to insights, AI responses, and citations
    # Format: [{"insight_id": "uuid", "response_id": "uuid", "citation_ids": ["uuid", ...]}]
    evidence_references = Column(JSON, nullable=False, default=list)

    # Priority for ordering (1 = highest priority)
    priority = Column(Integer, nullable=False, default=5)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation priority={self.priority} for analysis {self.analysis_id}>"

    def to_dict(self):
        """Convert recommendation to dictionary"""
        return {
            "id": str(self.id),
            "analysis_id": str(self.analysis_id),
            "text": self.text,
            "rationale": self.rationale,
            "expected_impact": self.expected_impact.value,
            "confidence_level": self.confidence_level.value,
            "evidence_references": self.evidence_references,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
