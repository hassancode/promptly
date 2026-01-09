"""Pydantic schemas for insights and recommendations"""
from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class InsightTypeEnum(str, Enum):
    """Types of insights"""
    VISIBILITY = "visibility"
    SENTIMENT = "sentiment"
    THEME = "theme"
    GAP = "gap"
    COMPARISON = "comparison"
    MENTION = "mention"


class ConfidenceLevelEnum(str, Enum):
    """Confidence levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class ImpactLevelEnum(str, Enum):
    """Impact levels for recommendations"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EvidenceReference(BaseModel):
    """Reference to evidence supporting an insight"""
    response_id: Optional[UUID] = None
    citation_ids: List[UUID] = Field(default_factory=list)
    excerpt: Optional[str] = None
    insight_id: Optional[UUID] = None  # For recommendation -> insight linking


class VisibilityScore(BaseModel):
    """Visibility scoring breakdown"""
    presence: float = Field(ge=0, le=1, description="Brand presence score (0-1)")
    frequency: float = Field(ge=0, le=1, description="Mention frequency score (0-1)")
    position: float = Field(ge=0, le=1, description="Position prominence score (0-1)")
    composite: float = Field(ge=0, le=1, description="Weighted composite score (0-1)")


class SentimentScore(BaseModel):
    """Sentiment analysis breakdown"""
    positive: float = Field(ge=0, le=1, description="Positive sentiment ratio")
    neutral: float = Field(ge=0, le=1, description="Neutral sentiment ratio")
    negative: float = Field(ge=0, le=1, description="Negative sentiment ratio")
    overall: str = Field(description="Overall sentiment (positive/neutral/negative)")


class MentionScore(BaseModel):
    """Mention frequency breakdown"""
    count: int = Field(ge=0, description="Total mention count")
    providers: dict = Field(default_factory=dict, description="Mentions by provider")


# Request schemas
class InsightGenerateRequest(BaseModel):
    """Request to generate insights for an analysis"""
    regenerate: bool = Field(default=False, description="Regenerate existing insights")


# Response schemas
class InsightResponse(BaseModel):
    """Single insight response"""
    id: UUID
    analysis_id: UUID
    insight_type: InsightTypeEnum
    brand_name: str
    competitor_name: Optional[str] = None
    summary: str
    explanation: str
    evidence_references: List[EvidenceReference]
    confidence_level: ConfidenceLevelEnum
    scores: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationResponse(BaseModel):
    """Single recommendation response"""
    id: UUID
    analysis_id: UUID
    text: str
    rationale: str
    expected_impact: ImpactLevelEnum
    confidence_level: ConfidenceLevelEnum
    evidence_references: List[EvidenceReference]
    priority: int
    created_at: datetime

    model_config = {"from_attributes": True}


class InsightsResponse(BaseModel):
    """Full insights response including all insights and recommendations"""
    analysis_id: UUID
    brand_name: str
    insights: List[InsightResponse]
    recommendations: List[RecommendationResponse]
    generated_at: datetime
    generation_time_ms: int = Field(description="Time to generate insights in milliseconds")


class InsightsSummary(BaseModel):
    """Summary of insights for an analysis"""
    analysis_id: UUID
    brand_name: str
    total_insights: int
    total_recommendations: int
    visibility_score: Optional[float] = None
    overall_sentiment: Optional[str] = None
    insight_types: List[InsightTypeEnum]
    has_insights: bool


# Scoring input schemas
class VisibilityScoreInput(BaseModel):
    """Input data for visibility scoring"""
    brand_name: str
    response_texts: List[str]
    provider_names: List[str]


class SentimentScoreInput(BaseModel):
    """Input data for sentiment scoring"""
    brand_name: str
    response_texts: List[str]


class ComparisonInput(BaseModel):
    """Input data for brand vs competitor comparison"""
    brand_name: str
    competitor_names: List[str]
    response_texts: List[str]
