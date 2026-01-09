"""Insight model for competitive analysis insights"""
import enum
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class InsightType(enum.Enum):
    """Types of insights generated"""
    VISIBILITY = "visibility"  # Brand visibility scoring
    SENTIMENT = "sentiment"  # Sentiment analysis
    THEME = "theme"  # Key themes identified
    GAP = "gap"  # Content/coverage gaps
    COMPARISON = "comparison"  # Brand vs competitor comparison
    MENTION = "mention"  # Mention frequency analysis


class ConfidenceLevel(enum.Enum):
    """Confidence levels for insights"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class Insight(Base):
    """
    Represents a generated insight from analysis data.

    Insights are derived from AI responses and provide actionable
    intelligence about brand visibility, sentiment, themes, and gaps.
    """
    __tablename__ = "insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    analysis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Insight type classification
    insight_type = Column(Enum(InsightType), nullable=False)

    # Entity this insight is about (brand or competitor name)
    brand_name = Column(String(255), nullable=False)
    competitor_name = Column(String(255), nullable=True)  # Optional for comparison insights

    # Insight content
    summary = Column(String(500), nullable=False)  # Short summary
    explanation = Column(Text, nullable=False)  # Detailed explanation

    # Evidence linking - JSON array of references to AI responses and citations
    # Format: [{"response_id": "uuid", "citation_ids": ["uuid", ...], "excerpt": "text"}]
    evidence_references = Column(JSON, nullable=False, default=list)

    # Confidence and scoring
    confidence_level = Column(Enum(ConfidenceLevel), nullable=False, default=ConfidenceLevel.MEDIUM)

    # Scores - JSONB for flexible scoring data
    # Format depends on insight_type:
    # - visibility: {"presence": 0.8, "frequency": 0.6, "position": 0.9, "composite": 0.76}
    # - sentiment: {"positive": 0.6, "neutral": 0.3, "negative": 0.1, "overall": "positive"}
    # - mention: {"count": 15, "providers": {"openai": 5, "claude": 4, ...}}
    scores = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="insights")

    def __repr__(self):
        return f"<Insight {self.insight_type.value} for {self.brand_name}>"

    def to_dict(self):
        """Convert insight to dictionary"""
        return {
            "id": str(self.id),
            "analysis_id": str(self.analysis_id),
            "insight_type": self.insight_type.value,
            "brand_name": self.brand_name,
            "competitor_name": self.competitor_name,
            "summary": self.summary,
            "explanation": self.explanation,
            "evidence_references": self.evidence_references,
            "confidence_level": self.confidence_level.value,
            "scores": self.scores,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
