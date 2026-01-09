"""Insights API router"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from core.logging import get_logger
from models.user import User
from schemas.insight import (
    InsightGenerateRequest,
    InsightResponse,
    RecommendationResponse,
    InsightsResponse,
    InsightsSummary,
)
from services.insight_service import InsightService
from services.recommendation_service import RecommendationService

logger = get_logger(__name__)

router = APIRouter(prefix="/analyses/{analysis_id}/insights", tags=["insights"])


@router.post(
    "/generate",
    response_model=InsightsResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate insights for an analysis",
    description="Generates visibility, sentiment, theme, gap, and comparison insights. Target: <5 seconds.",
)
async def generate_insights(
    analysis_id: UUID,
    request: InsightGenerateRequest = InsightGenerateRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate comprehensive insights for an analysis.

    This endpoint orchestrates all scoring services to produce:
    - Visibility insights (presence, frequency, position)
    - Sentiment analysis (positive/neutral/negative)
    - Theme identification (key topics)
    - Gap analysis (missing coverage vs competitors)
    - Mention frequency analysis

    Also generates minimum 5 actionable recommendations.
    """
    logger.info(
        "Insight generation requested",
        extra={
            "analysis_id": str(analysis_id),
            "user_id": str(current_user.id),
            "regenerate": request.regenerate,
        }
    )

    insight_service = InsightService(db)
    recommendation_service = RecommendationService(db)

    try:
        # Generate insights
        result = await insight_service.generate_insights(
            analysis_id=analysis_id,
            user_id=current_user.id,
            regenerate=request.regenerate,
        )

        # Generate recommendations
        recommendations = await recommendation_service.generate_recommendations(
            analysis_id=analysis_id,
            user_id=current_user.id,
            regenerate=request.regenerate,
        )

        result["recommendations"] = [r.to_dict() for r in recommendations]

        logger.info(
            "Insight generation complete",
            extra={
                "analysis_id": str(analysis_id),
                "insight_count": len(result.get("insights", [])),
                "recommendation_count": len(recommendations),
                "generation_time_ms": result.get("generation_time_ms"),
            }
        )

        return result

    except Exception as e:
        logger.error(
            "Insight generation failed",
            extra={
                "analysis_id": str(analysis_id),
                "error": str(e),
            }
        )
        raise


@router.get(
    "",
    response_model=List[InsightResponse],
    status_code=status.HTTP_200_OK,
    summary="Get insights for an analysis",
)
async def get_insights(
    analysis_id: UUID,
    insight_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve existing insights for an analysis.

    Optionally filter by insight type:
    - visibility
    - sentiment
    - theme
    - gap
    - comparison
    - mention
    """
    logger.info(
        "Getting insights",
        extra={
            "analysis_id": str(analysis_id),
            "user_id": str(current_user.id),
            "filter_type": insight_type,
        }
    )

    insight_service = InsightService(db)

    insights = insight_service.get_insights(analysis_id, current_user.id)

    # Filter by type if specified
    if insight_type:
        insights = [i for i in insights if i.insight_type.value == insight_type]

    return [i.to_dict() for i in insights]


@router.get(
    "/summary",
    response_model=InsightsSummary,
    status_code=status.HTTP_200_OK,
    summary="Get insight summary for an analysis",
)
async def get_insights_summary(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a summary of insights for an analysis.

    Returns:
    - Total insight and recommendation counts
    - Visibility score
    - Overall sentiment
    - Available insight types
    """
    insight_service = InsightService(db)
    recommendation_service = RecommendationService(db)

    summary = insight_service.get_insight_summary(analysis_id, current_user.id)

    # Add recommendation count
    recommendations = recommendation_service.get_recommendations(analysis_id, current_user.id)
    summary["total_recommendations"] = len(recommendations)

    return summary


@router.get(
    "/recommendations",
    response_model=List[RecommendationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get recommendations for an analysis",
)
async def get_recommendations(
    analysis_id: UUID,
    impact_level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve recommendations for an analysis.

    Optionally filter by impact level:
    - high
    - medium
    - low
    """
    logger.info(
        "Getting recommendations",
        extra={
            "analysis_id": str(analysis_id),
            "user_id": str(current_user.id),
            "filter_impact": impact_level,
        }
    )

    recommendation_service = RecommendationService(db)

    recommendations = recommendation_service.get_recommendations(analysis_id, current_user.id)

    # Filter by impact if specified
    if impact_level:
        recommendations = [r for r in recommendations if r.expected_impact.value == impact_level]

    return [r.to_dict() for r in recommendations]
