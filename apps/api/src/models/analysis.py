"""
Analysis model

Represents a brand analysis with associated competitors.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from core.database import Base


class AnalysisStatus(str, enum.Enum):
    """Analysis workflow status"""
    DRAFT = "draft"  # Initial state, competitors being added
    READY = "ready"  # Competitors finalized, ready for querying
    QUERYING = "querying"  # AI providers being queried
    COMPLETED = "completed"  # All queries complete, insights available
    FAILED = "failed"  # Query or processing failed


class Analysis(Base):
    """
    Brand analysis entity

    Represents a user's analysis of their brand against competitors.
    Each analysis tracks one brand and up to 5 competitors.
    """
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    brand_name = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)  # User's location for location-aware queries
    analysis_metadata = Column(JSON, default=dict)  # Additional metadata (location_info, etc.)
    status = Column(
        SQLEnum(AnalysisStatus, name="analysis_status"),
        default=AnalysisStatus.DRAFT,
        nullable=False,
        index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    competitors = relationship(
        "Competitor",
        back_populates="analysis",
        cascade="all, delete-orphan"
    )
    prompts = relationship(
        "Prompt",
        back_populates="analysis",
        cascade="all, delete-orphan"
    )
    insights = relationship(
        "Insight",
        back_populates="analysis",
        cascade="all, delete-orphan"
    )
    recommendations = relationship(
        "Recommendation",
        back_populates="analysis",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Analysis(id={self.id}, brand={self.brand_name}, status={self.status})>"
