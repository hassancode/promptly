"""
SSE Streaming API

Server-Sent Events endpoint for real-time analysis progress updates.
"""
import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import AsyncGenerator

from core.database import get_db
from core.dependencies import get_current_user
from core.logging import get_logger
from models.user import User
from models.analysis import Analysis
from models.prompt import Prompt
from models.ai_response import AIResponse, ResponseStatus
from services.provider_orchestrator import ProviderOrchestrator
from schemas.provider import StreamEvent

logger = get_logger(__name__)

router = APIRouter(prefix="/analyses", tags=["streaming"])


async def generate_progress_events(
    analysis_id: str,
    user_id: str,
    db: Session
) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events for analysis progress

    Yields SSE-formatted events as the analysis progresses.

    Args:
        analysis_id: Analysis ID to track
        user_id: User ID (for ownership verification)
        db: Database session

    Yields:
        SSE-formatted event strings
    """
    try:
        # Verify analysis exists and user owns it
        analysis = db.query(Analysis).filter(
            Analysis.id == analysis_id,
            Analysis.user_id == user_id
        ).first()

        if not analysis:
            yield f"event: error\ndata: {json.dumps({'error': 'Analysis not found'})}\n\n"
            return

        # Get all prompts for this analysis
        prompts = db.query(Prompt).filter(
            Prompt.analysis_id == analysis_id
        ).all()

        if not prompts:
            yield f"event: error\ndata: {json.dumps({'error': 'No prompts found'})}\n\n"
            return

        # Initialize orchestrator
        orchestrator = ProviderOrchestrator(db)
        total_providers = len(orchestrator.provider_adapters)

        logger.info(
            f"Starting SSE stream for analysis {analysis_id}",
            extra={
                "analysis_id": analysis_id,
                "user_id": user_id,
                "prompts": len(prompts),
                "providers": total_providers
            }
        )

        # Send initial progress event
        yield f"event: progress_update\ndata: {json.dumps({'completed': 0, 'total': len(prompts) * total_providers, 'percentage': 0.0})}\n\n"

        # Query all providers for each prompt
        total_completed = 0
        total_expected = len(prompts) * total_providers

        for prompt in prompts:
            # Send provider_started events
            for provider_name in orchestrator.enabled_providers:
                event_data = {
                    "provider": provider_name,
                    "prompt_id": str(prompt.id),
                    "timestamp": datetime.utcnow().isoformat()
                }
                yield f"event: provider_started\ndata: {json.dumps(event_data)}\n\n"

            # Query all providers for this prompt
            result = await orchestrator.query_all_providers(
                analysis=analysis,
                prompt=prompt,
                timeout_seconds=30
            )

            # Send completion events for each provider
            for provider_name, provider_status in result["provider_statuses"].items():
                total_completed += 1
                percentage = (total_completed / total_expected * 100) if total_expected > 0 else 0

                if provider_status == "success":
                    # Get the response from database
                    ai_response = db.query(AIResponse).filter(
                        AIResponse.prompt_id == prompt.id,
                        AIResponse.provider == provider_name
                    ).first()

                    if ai_response:
                        event_data = {
                            "provider": provider_name,
                            "prompt_id": str(prompt.id),
                            "response_id": str(ai_response.id),
                            "has_citations": len(ai_response.citations) > 0,
                            "citation_count": len(ai_response.citations),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        yield f"event: provider_completed\ndata: {json.dumps(event_data)}\n\n"
                else:
                    # Provider failed or timed out
                    event_data = {
                        "provider": provider_name,
                        "prompt_id": str(prompt.id),
                        "error": provider_status,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    yield f"event: provider_failed\ndata: {json.dumps(event_data)}\n\n"

                # Send progress update
                progress_data = {
                    "completed": total_completed,
                    "total": total_expected,
                    "percentage": round(percentage, 2),
                    "current_provider": provider_name
                }
                yield f"event: progress_update\ndata: {json.dumps(progress_data)}\n\n"

                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.1)

        # Send analysis complete event
        complete_event = {
            "analysis_id": analysis_id,
            "total_responses": total_completed,
            "successful": result["successful"],
            "failed": result["failed"],
            "enabled_providers": orchestrator.enabled_providers,
            "timestamp": datetime.utcnow().isoformat()
        }
        yield f"event: analysis_complete\ndata: {json.dumps(complete_event)}\n\n"

        logger.info(
            f"SSE stream completed for analysis {analysis_id}",
            extra={
                "analysis_id": analysis_id,
                "total_completed": total_completed,
                "successful": result["successful"],
                "failed": result["failed"]
            }
        )

    except Exception as e:
        logger.error(
            f"Error in SSE stream: {e}",
            exc_info=True,
            extra={"analysis_id": analysis_id}
        )
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


@router.get(
    "/{analysis_id}/stream",
    response_class=StreamingResponse
)
async def stream_analysis_progress(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Stream analysis progress via Server-Sent Events

    Returns a text/event-stream that sends real-time updates as
    providers are queried and results are collected.

    **Event Types:**
    - `provider_started`: Provider query has begun
    - `provider_completed`: Provider query succeeded
    - `provider_failed`: Provider query failed or timed out
    - `progress_update`: Progress percentage update
    - `analysis_complete`: All providers finished
    - `error`: Error occurred

    **Requirements:**
    - User must be authenticated
    - Analysis must exist and be owned by user

    **Returns:**
    - 200: SSE stream (text/event-stream)
    - 401: Not authenticated
    - 403: Not authorized
    - 404: Analysis not found
    """
    logger.info(
        f"GET /api/v1/analyses/{analysis_id}/stream - User {current_user.id}",
        extra={"user_id": str(current_user.id), "analysis_id": analysis_id}
    )

    return StreamingResponse(
        generate_progress_events(analysis_id, str(current_user.id), db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
