"""
AI Responses API

Endpoints for retrieving and managing AI provider responses.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user
from core.logging import get_logger
from core.exceptions import AppException
from models.user import User
from models.analysis import Analysis
from models.prompt import Prompt
from models.ai_response import AIResponse, ResponseStatus, ProviderType
from schemas.provider import AIResponseResponse
from services.provider_orchestrator import ProviderOrchestrator

logger = get_logger(__name__)

router = APIRouter(prefix="/analyses", tags=["responses"])


@router.get(
    "/{analysis_id}/responses",
    response_model=List[AIResponseResponse]
)
def get_analysis_responses(
    analysis_id: UUID,
    provider: Optional[str] = Query(None, description="Filter by provider"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all AI responses for an analysis

    Returns all provider responses collected for this analysis,
    including citations and metadata.

    **Query Parameters:**
    - `provider`: Filter by specific provider (openai, claude, gemini, etc.)
    - `status`: Filter by response status (success, failed, timeout)

    **Requirements:**
    - User must be authenticated
    - Analysis must exist and be owned by user

    **Returns:**
    - 200: List of AI responses with citations
    - 401: Not authenticated
    - 403: Not authorized
    - 404: Analysis not found
    """
    logger.info(
        f"GET /api/v1/analyses/{analysis_id}/responses - User {current_user.id}",
        extra={
            "user_id": str(current_user.id),
            "analysis_id": analysis_id,
            "provider_filter": provider,
            "status_filter": status_filter
        }
    )

    # Verify analysis exists and user owns it
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Validate filter params early (before returning empty list)
    provider_enum = None
    status_enum = None

    if provider:
        try:
            provider_enum = ProviderType(provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid provider: {provider}"
            )

    if status_filter:
        try:
            status_enum = ResponseStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )

    # Get all prompts for this analysis
    prompts = db.query(Prompt).filter(
        Prompt.analysis_id == analysis_id
    ).all()

    if not prompts:
        return []

    # Build query for AI responses
    query = db.query(AIResponse).filter(
        AIResponse.prompt_id.in_([p.id for p in prompts])
    )

    # Apply filters
    if provider_enum:
        query = query.filter(AIResponse.provider == provider_enum)

    if status_enum:
        query = query.filter(AIResponse.status == status_enum)

    # Execute query
    responses = query.all()

    logger.info(
        f"Retrieved {len(responses)} responses",
        extra={
            "analysis_id": analysis_id,
            "count": len(responses),
            "provider_filter": provider,
            "status_filter": status_filter
        }
    )

    # Convert to response schema with citations sorted by position
    return [
        AIResponseResponse(
            id=str(r.id),
            prompt_id=str(r.prompt_id),
            provider=r.provider.value,
            model_name=r.model_name,
            answer_text=r.answer_text,
            metadata=r.response_metadata,
            citation_coverage=r.citation_coverage.value,
            status=r.status.value,
            created_at=r.created_at,
            completed_at=r.completed_at,
            citations=[
                {
                    "id": str(c.id),
                    "url": c.url,
                    "title": c.title,
                    "snippet": c.snippet,
                    "source_type": c.source_type.value,
                    "validity_status": c.validity_status.value,
                    "position": c.position,
                    "created_at": c.created_at
                }
                for c in sorted(r.citations, key=lambda c: c.position)
            ]
        )
        for r in responses
    ]


@router.post(
    "/{analysis_id}/responses/{response_id}/retry",
    response_model=AIResponseResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def retry_failed_response(
    analysis_id: UUID,
    response_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retry a failed or timed-out provider response

    Re-queries a single provider that previously failed or timed out.
    Useful for recovering from transient failures.

    **Requirements:**
    - User must be authenticated
    - Analysis must exist and be owned by user
    - Response must be in failed or timeout status

    **Returns:**
    - 202: Retry initiated, returns updated response
    - 400: Response not in retryable status
    - 401: Not authenticated
    - 403: Not authorized
    - 404: Analysis or response not found
    """
    logger.info(
        f"POST /api/v1/analyses/{analysis_id}/responses/{response_id}/retry - User {current_user.id}",
        extra={
            "user_id": str(current_user.id),
            "analysis_id": analysis_id,
            "response_id": response_id
        }
    )

    # Verify analysis exists and user owns it
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Get the response
    ai_response = db.query(AIResponse).filter(
        AIResponse.id == response_id
    ).first()

    if not ai_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found"
        )

    # Verify response belongs to this analysis
    prompt = db.query(Prompt).filter(
        Prompt.id == ai_response.prompt_id,
        Prompt.analysis_id == analysis_id
    ).first()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Response does not belong to this analysis"
        )

    # Check if response is retryable
    if ai_response.status not in [ResponseStatus.FAILED, ResponseStatus.TIMEOUT]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Response status '{ai_response.status.value}' is not retryable. Only 'failed' or 'timeout' responses can be retried."
        )

    # Initialize orchestrator
    orchestrator = ProviderOrchestrator(db)

    # Get the provider adapter
    provider_name = ai_response.provider.value
    if provider_name not in orchestrator.provider_adapters:
        raise AppException(
            f"Provider '{provider_name}' not available",
            status.HTTP_503_SERVICE_UNAVAILABLE
        )

    adapter = orchestrator.provider_adapters[provider_name]

    # Update status to in_progress
    ai_response.status = ResponseStatus.IN_PROGRESS
    db.commit()

    logger.info(
        f"Retrying provider {provider_name} for response {response_id}",
        extra={
            "provider": provider_name,
            "response_id": response_id,
            "prompt_id": str(prompt.id)
        }
    )

    # Query the provider
    brand_name = analysis.brand_name
    competitors = [c.name for c in analysis.competitors]

    try:
        result = await orchestrator._query_single_provider(
            adapter=adapter,
            prompt=prompt.text,
            brand_name=brand_name,
            competitors=competitors,
            timeout_seconds=30
        )

        # Update the response with new results
        ai_response.answer_text = result.answer_text
        ai_response.response_metadata = result.metadata
        ai_response.citation_coverage = result.citation_coverage
        ai_response.status = ResponseStatus(result.status)
        ai_response.completed_at = db.func.now()

        # Delete old citations and add new ones
        for citation in ai_response.citations:
            db.delete(citation)

        for citation_data in result.citations:
            from models.citation import Citation
            citation = Citation(
                ai_response_id=ai_response.id,
                url=citation_data.url,
                title=citation_data.title,
                snippet=citation_data.snippet,
                source_type=citation_data.source_type,
                position=citation_data.position
            )
            db.add(citation)

        db.commit()
        db.refresh(ai_response)

        logger.info(
            f"Provider retry completed: {result.status}",
            extra={
                "provider": provider_name,
                "response_id": response_id,
                "new_status": result.status
            }
        )

        # Return updated response
        return AIResponseResponse(
            id=str(ai_response.id),
            prompt_id=str(ai_response.prompt_id),
            provider=ai_response.provider.value,
            model_name=ai_response.model_name,
            answer_text=ai_response.answer_text,
            metadata=ai_response.response_metadata,
            citation_coverage=ai_response.citation_coverage.value,
            status=ai_response.status.value,
            created_at=ai_response.created_at,
            completed_at=ai_response.completed_at,
            citations=[
                {
                    "id": str(c.id),
                    "url": c.url,
                    "title": c.title,
                    "snippet": c.snippet,
                    "source_type": c.source_type.value,
                    "validity_status": c.validity_status.value,
                    "position": c.position,
                    "created_at": c.created_at
                }
                for c in ai_response.citations
            ]
        )

    except Exception as e:
        # Revert status if retry fails
        ai_response.status = ResponseStatus.FAILED
        ai_response.response_metadata = {"retry_error": str(e)}
        db.commit()

        logger.error(
            f"Provider retry failed: {e}",
            exc_info=True,
            extra={"provider": provider_name, "response_id": response_id}
        )

        raise AppException(
            f"Retry failed: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
