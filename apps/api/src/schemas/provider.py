"""
Provider and AIResponse Pydantic schemas

Validation schemas for AI provider operations.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Citation Schemas
# ============================================================================

class CitationCreate(BaseModel):
    """Schema for creating a citation"""
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    source_type: str = "web"
    position: int = 0


class CitationResponse(BaseModel):
    """Response schema for citation"""
    id: str
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    source_type: str
    validity_status: str
    position: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# AIResponse Schemas
# ============================================================================

class AIResponseCreate(BaseModel):
    """Schema for creating an AI response"""
    prompt_id: str
    provider: str
    model_name: str
    answer_text: Dict[str, Any]  # JSONB - flexible structure
    metadata: Dict[str, Any] = Field(default_factory=dict)
    citation_coverage: str = "none"
    status: str = "success"


class AIResponseResponse(BaseModel):
    """Response schema for AI response"""
    id: str
    prompt_id: str
    provider: str
    model_name: str
    answer_text: Dict[str, Any]
    metadata: Dict[str, Any]
    citation_coverage: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    citations: List[CitationResponse] = []

    model_config = {"from_attributes": True}


# ============================================================================
# Provider Query Result (Internal use by adapters)
# ============================================================================

class ProviderQueryResult(BaseModel):
    """
    Normalized result from a provider adapter query

    This is the internal format that all provider adapters
    must return. It gets converted to AIResponse for storage.
    """
    provider: str
    model_name: str
    answer_text: Dict[str, Any]  # Structured answer
    citations: List[CitationCreate] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)
    citation_coverage: str = "none"
    status: str = "success"
    error_message: Optional[str] = None


# ============================================================================
# SSE Stream Event Schemas
# ============================================================================

class StreamEvent(BaseModel):
    """
    Server-Sent Event for analysis progress streaming

    Event types:
    - provider_started: Provider query has begun
    - provider_completed: Provider query succeeded
    - provider_failed: Provider query failed
    - analysis_complete: All enabled providers finished
    - progress_update: Progress percentage update
    """
    event: str  # Event type
    data: Dict[str, Any]  # Event payload


class ProviderStartedEvent(BaseModel):
    """Event data for provider_started"""
    provider: str
    prompt_id: str
    timestamp: datetime


class ProviderCompletedEvent(BaseModel):
    """Event data for provider_completed"""
    provider: str
    prompt_id: str
    response_id: str
    has_citations: bool
    citation_count: int
    timestamp: datetime


class ProviderFailedEvent(BaseModel):
    """Event data for provider_failed"""
    provider: str
    prompt_id: str
    error: str
    timestamp: datetime


class AnalysisCompleteEvent(BaseModel):
    """Event data for analysis_complete"""
    analysis_id: str
    total_responses: int
    successful: int
    failed: int
    enabled_providers: List[str]
    timestamp: datetime


class ProgressUpdateEvent(BaseModel):
    """Event data for progress_update"""
    completed: int
    total: int
    percentage: float
    current_provider: Optional[str] = None


# ============================================================================
# Provider Configuration
# ============================================================================

class ProviderInfo(BaseModel):
    """Information about a provider's capabilities and status"""
    name: str
    enabled: bool
    supports_citations: bool
    supports_streaming: bool = False
    model_name: str


class ProviderListResponse(BaseModel):
    """List of all providers with their status"""
    providers: List[ProviderInfo]
    enabled_count: int
    total_count: int
