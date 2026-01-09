"""
Health check endpoints for API monitoring
Tasks: T222, T222A [Phase 9]
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.database import get_db
from core.redis import get_redis_client
from core.logging import logger

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint

    Returns 200 OK if the API is running
    """
    return {
        "status": "healthy",
        "service": "promptly-api",
        "version": "0.1.0"
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check endpoint

    Validates connectivity to:
    - PostgreSQL database
    - Redis cache

    Returns 200 OK if all dependencies are healthy
    Returns 503 Service Unavailable if any dependency is unhealthy
    """
    checks = {
        "database": False,
        "redis": False
    }
    errors = []

    # Check PostgreSQL connectivity
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        errors.append(f"Database: {str(e)}")
        logger.error("Database health check failed", extra={
            "operation": "health_check",
            "component": "database",
            "error": str(e)
        })

    # Check Redis connectivity
    try:
        redis_client = await get_redis_client()
        if redis_client:
            await redis_client.ping()
            checks["redis"] = True
        else:
            errors.append("Redis: Client not initialized")
    except Exception as e:
        errors.append(f"Redis: {str(e)}")
        logger.error("Redis health check failed", extra={
            "operation": "health_check",
            "component": "redis",
            "error": str(e)
        })

    # Determine overall status
    all_healthy = all(checks.values())

    response = {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks
    }

    if errors:
        response["errors"] = errors

    if not all_healthy:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail=response
        )

    return response


@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint

    Returns 200 OK if the API process is alive
    Used by orchestration systems to detect hung processes
    """
    return {"status": "alive"}
