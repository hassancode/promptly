"""
Metadata Router

Endpoints for retrieving analysis metadata (progress, location, etc.)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user
from models.analysis import Analysis
from models.ai_response import AIResponse, ResponseStatus
from models.prompt import Prompt
from models.user import User

router = APIRouter(prefix="/metadata", tags=["metadata"])


@router.get("/analyses/{analysis_id}/progress")
async def get_analysis_progress(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get analysis progress information.

    Returns:
        {
            "analysis_id": str,
            "status": str (pending/in_progress/completed/failed),
            "total_providers": int,
            "completed_providers": int,
            "failed_providers": int,
            "progress_percentage": int (0-100),
            "providers": [
                {
                    "provider": str,
                    "status": str,
                    "model": str | null,
                    "has_citations": bool,
                    "citation_count": int
                }
            ]
        }
    """
    # Convert analysis_id to UUID
    try:
        analysis_uuid = UUID(analysis_id)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid analysis ID"
        )

    # Get analysis
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_uuid,
        Analysis.user_id == current_user.id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Get all responses for this analysis (join through Prompt)
    responses = db.query(AIResponse).join(
        Prompt, AIResponse.prompt_id == Prompt.id
    ).filter(
        Prompt.analysis_id == analysis_uuid
    ).all()

    # Calculate progress based on unique providers in responses
    unique_providers = list(set(r.provider.value for r in responses))
    total_providers = len(unique_providers)
    completed_count = sum(1 for r in responses if r.status == ResponseStatus.COMPLETED)
    failed_count = sum(1 for r in responses if r.status in [ResponseStatus.FAILED, ResponseStatus.TIMEOUT])

    progress_percentage = 0
    if total_providers > 0:
        progress_percentage = int((completed_count / total_providers) * 100)

    # Build provider status list
    provider_statuses = []
    response_map = {r.provider.value: r for r in responses}

    for provider in unique_providers:
        response = response_map.get(provider)

        if response:
            provider_statuses.append({
                "provider": provider,
                "status": response.status.value,
                "model": response.model_name,
                "has_citations": len(response.citations) > 0 if response.citations else False,
                "citation_count": len(response.citations) if response.citations else 0,
            })
        else:
            provider_statuses.append({
                "provider": provider,
                "status": "pending",
                "model": None,
                "has_citations": False,
                "citation_count": 0,
            })

    return {
        "analysis_id": analysis_id,
        "status": analysis.status,
        "total_providers": total_providers,
        "completed_providers": completed_count,
        "failed_providers": failed_count,
        "progress_percentage": progress_percentage,
        "providers": provider_statuses,
    }


@router.get("/analyses/{analysis_id}/location")
async def get_analysis_location(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get analysis location information.

    Returns:
        {
            "analysis_id": str,
            "location": str | null,
            "location_detected": bool,
            "detection_method": str | null (ip/manual/default)
        }
    """
    # Convert analysis_id to UUID
    try:
        analysis_uuid = UUID(analysis_id)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid analysis ID"
        )

    # Get analysis
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_uuid,
        Analysis.user_id == current_user.id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Extract location metadata
    location_info = analysis.analysis_metadata.get("location_info", {}) if analysis.analysis_metadata else {}

    return {
        "analysis_id": analysis_id,
        "location": analysis.location,
        "location_detected": location_info.get("detected", False),
        "detection_method": location_info.get("method", None),
    }
