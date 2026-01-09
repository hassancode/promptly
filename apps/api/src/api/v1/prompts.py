"""
Prompt API endpoints

Endpoints for prompt configuration and AI suggestions.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from models.user import User
from schemas.prompt import (
    PromptAdd,
    PromptResponse,
    PromptSuggestResponse,
)
from services.prompt_service import PromptService
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/analyses/{analysis_id}/prompts", tags=["prompts"])


@router.get(
    "",
    response_model=list[PromptResponse],
    status_code=status.HTTP_200_OK
)
def get_prompts(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all prompts for an analysis

    Returns all prompts associated with the analysis.

    **Requirements:**
    - User must be authenticated
    - Analysis must exist and be owned by the user

    **Returns:**
    - 200: List of prompts
    - 401: Not authenticated
    - 403: Not authorized (analysis belongs to another user)
    - 404: Analysis not found
    """
    logger.info(
        f"GET /api/v1/analyses/{analysis_id}/prompts - User {current_user.id}",
        extra={"user_id": str(current_user.id), "analysis_id": analysis_id}
    )

    service = PromptService(db)
    analysis = service.get_analysis(current_user, analysis_id)

    return [
        PromptResponse(
            id=str(p.id),
            text=p.text,
            is_suggested=p.is_suggested,
            created_at=p.created_at
        )
        for p in analysis.prompts
    ]


@router.post(
    "/suggest",
    response_model=PromptSuggestResponse,
    status_code=status.HTTP_200_OK
)
async def suggest_prompts(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered prompt suggestions

    Uses Claude AI to suggest up to 5 relevant prompts for the analysis.
    Prompts are contextually relevant based on the brand and competitors.

    **Requirements:**
    - User must be authenticated
    - Analysis must exist and be owned by the user

    **Returns:**
    - 200: Suggestions generated successfully
    - 401: Not authenticated
    - 403: Not authorized (analysis belongs to another user)
    - 404: Analysis not found
    """
    logger.info(
        f"POST /api/v1/analyses/{analysis_id}/prompts/suggest - User {current_user.id}",
        extra={"user_id": str(current_user.id), "analysis_id": analysis_id}
    )

    service = PromptService(db)
    analysis = service.get_analysis(current_user, analysis_id)
    suggestions = await service.suggest_prompts(current_user, analysis)

    return PromptSuggestResponse(prompts=suggestions)


@router.post(
    "",
    response_model=PromptResponse,
    status_code=status.HTTP_201_CREATED
)
def add_prompt(
    analysis_id: str,
    prompt_data: PromptAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a custom prompt to an analysis

    Adds a user-defined prompt to the analysis. User can add prompts
    suggested by AI or their own custom prompts.

    **Business Rules:**
    - Maximum 7 prompts per analysis
    - No duplicate prompts (case-insensitive)
    - Prompt text must be non-empty (1-1000 characters)

    **Requirements:**
    - User must be authenticated
    - Analysis must exist and be owned by the user

    **Returns:**
    - 201: Prompt added successfully
    - 400: Business rule violation (max prompts, duplicate)
    - 401: Not authenticated
    - 403: Not authorized (analysis belongs to another user)
    - 404: Analysis not found
    - 422: Validation error (invalid prompt text)
    """
    logger.info(
        f"POST /api/v1/analyses/{analysis_id}/prompts - User {current_user.id}",
        extra={
            "user_id": str(current_user.id),
            "analysis_id": analysis_id,
            "prompt_length": len(prompt_data.prompt_text)
        }
    )

    service = PromptService(db)
    analysis = service.get_analysis(current_user, analysis_id)
    prompt = service.add_prompt(current_user, analysis, prompt_data)

    return PromptResponse(
        id=str(prompt.id),
        text=prompt.text,
        is_suggested=prompt.is_suggested,
        created_at=prompt.created_at
    )
