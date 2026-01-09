"""
Analysis and Competitor Pydantic schemas

Validation schemas for analysis-related API operations.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Analysis Schemas
# ============================================================================

class AnalysisCreate(BaseModel):
    """Request schema for creating a new analysis"""
    brand_name: str = Field(..., min_length=1, max_length=255)
    context: Optional[str] = Field(None, max_length=500)  # Optional context for disambiguation

    @field_validator('brand_name')
    @classmethod
    def validate_brand_name(cls, v: str) -> str:
        """Validate brand name is not empty or whitespace-only"""
        if not v or not v.strip():
            raise ValueError('Brand name cannot be empty or whitespace-only')
        return v.strip()


class AnalysisResponse(BaseModel):
    """Response schema for analysis operations"""
    id: str
    brand_name: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisWithCompetitors(BaseModel):
    """Response schema for analysis with associated competitors"""
    id: str
    brand_name: str
    status: str
    created_at: datetime
    competitors: List["CompetitorResponse"] = []

    model_config = {"from_attributes": True}


# ============================================================================
# Competitor Schemas
# ============================================================================

class CompetitorSuggestion(BaseModel):
    """Single competitor suggestion from AI"""
    name: str
    is_suggested: bool = True


class CompetitorSuggestResponse(BaseModel):
    """Response schema for competitor suggestions endpoint"""
    competitors: List[CompetitorSuggestion]


class CompetitorAdd(BaseModel):
    """Request schema for adding a competitor"""
    competitor_name: str = Field(..., min_length=1, max_length=255)

    @field_validator('competitor_name')
    @classmethod
    def validate_competitor_name(cls, v: str) -> str:
        """Validate competitor name is not empty or whitespace-only"""
        if not v or not v.strip():
            raise ValueError('Competitor name cannot be empty or whitespace-only')
        return v.strip()


class CompetitorResponse(BaseModel):
    """Response schema for competitor operations"""
    id: str
    name: str
    is_suggested: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Disambiguation Schemas
# ============================================================================

class DisambiguationOption(BaseModel):
    """A single disambiguation option"""
    value: str
    label: str
    description: str


class DisambiguationResponse(BaseModel):
    """Response when brand name is ambiguous"""
    disambiguation_required: bool = True
    brand_name: str
    options: List[DisambiguationOption]
    message: str = "Multiple interpretations found. Please select the correct one."


# Update forward references
AnalysisWithCompetitors.model_rebuild()
