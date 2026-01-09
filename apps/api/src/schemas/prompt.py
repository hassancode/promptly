"""
Prompt Pydantic schemas

Validation schemas for prompt-related API operations.
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Prompt Schemas
# ============================================================================

class PromptSuggestion(BaseModel):
    """Single prompt suggestion from AI"""
    text: str
    is_suggested: bool = True


class PromptSuggestResponse(BaseModel):
    """Response schema for prompt suggestions endpoint"""
    prompts: List[PromptSuggestion]


class PromptAdd(BaseModel):
    """Request schema for adding a prompt"""
    prompt_text: str = Field(..., min_length=1, max_length=1000)

    @field_validator('prompt_text')
    @classmethod
    def validate_prompt_text(cls, v: str) -> str:
        """Validate prompt text is not empty or whitespace-only"""
        if not v or not v.strip():
            raise ValueError('Prompt text cannot be empty or whitespace-only')
        return v.strip()


class PromptResponse(BaseModel):
    """Response schema for prompt operations"""
    id: str
    text: str
    is_suggested: bool
    created_at: datetime

    model_config = {"from_attributes": True}
