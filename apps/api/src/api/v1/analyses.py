"""
Analysis API endpoints

Endpoints for brand analysis and competitor management.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from models.user import User
from schemas.analysis import (
    AnalysisCreate,
    AnalysisResponse,
    CompetitorAdd,
    CompetitorResponse,
    CompetitorSuggestResponse,
)
from services.analysis_service import AnalysisService
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
def create_analysis(
    analysis_data: AnalysisCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new brand analysis

    Creates an analysis for the authenticated user's brand.
    The analysis starts in 'draft' status and can have up to 5 competitors added.

    **Requirements:**
    - User must be authenticated
    - Brand name must be non-empty (1-255 characters)

    **Returns:**
    - 201: Analysis created successfully
    - 401: Not authenticated
    - 422: Validation error (invalid brand name)
    """
    logger.info(
        f"POST /api/v1/analyses - User {current_user.id}",
        extra={"user_id": str(current_user.id), "brand_name": analysis_data.brand_name}
    )

    service = AnalysisService(db)
    analysis = service.create_analysis(current_user, analysis_data)

    return AnalysisResponse(
        id=str(analysis.id),
        brand_name=analysis.brand_name,
        status=analysis.status.value,
        created_at=analysis.created_at
    )


@router.post(
    "/{analysis_id}/competitors/suggest",
    response_model=CompetitorSuggestResponse,
    status_code=status.HTTP_200_OK
)
async def suggest_competitors(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered competitor suggestions

    Uses Claude AI to suggest up to 3 relevant competitors for the brand.
    Suggestions are contextually relevant based on the brand name.

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
        f"POST /api/v1/analyses/{analysis_id}/competitors/suggest - User {current_user.id}",
        extra={"user_id": str(current_user.id), "analysis_id": analysis_id}
    )

    service = AnalysisService(db)
    suggestions = await service.suggest_competitors(current_user, analysis_id)

    return CompetitorSuggestResponse(competitors=suggestions)


@router.post(
    "/{analysis_id}/competitors",
    response_model=CompetitorResponse,
    status_code=status.HTTP_201_CREATED
)
def add_competitor(
    analysis_id: str,
    competitor_data: CompetitorAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a competitor to an analysis

    Adds a custom competitor to the analysis. User can add competitors
    suggested by AI or their own custom competitors.

    **Business Rules:**
    - Maximum 5 competitors per analysis
    - No duplicate competitors (case-insensitive)
    - Competitor name must be non-empty (1-255 characters)

    **Requirements:**
    - User must be authenticated
    - Analysis must exist and be owned by the user

    **Returns:**
    - 201: Competitor added successfully
    - 400: Business rule violation (max competitors, duplicate)
    - 401: Not authenticated
    - 403: Not authorized (analysis belongs to another user)
    - 404: Analysis not found
    - 422: Validation error (invalid competitor name)
    """
    logger.info(
        f"POST /api/v1/analyses/{analysis_id}/competitors - User {current_user.id}",
        extra={
            "user_id": str(current_user.id),
            "analysis_id": analysis_id,
            "competitor_name": competitor_data.competitor_name
        }
    )

    service = AnalysisService(db)
    competitor = service.add_competitor(current_user, analysis_id, competitor_data)

    return CompetitorResponse(
        id=str(competitor.id),
        name=competitor.name,
        is_suggested=competitor.is_suggested,
        created_at=competitor.created_at
    )
