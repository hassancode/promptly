"""
Rate limiting middleware
Task: T196 [Phase 9]

Implements rate limiting for API endpoints:
- 10 analyses per hour per user
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Request, HTTPException
from core.redis import get_redis_client
from core.logging import logger


# Rate limit configuration
ANALYSIS_RATE_LIMIT = 10  # Max analyses per hour
RATE_LIMIT_WINDOW_SECONDS = 3600  # 1 hour


async def check_analysis_rate_limit(user_id: str) -> bool:
    """
    Check if user has exceeded analysis rate limit

    Args:
        user_id: User UUID string

    Returns:
        True if within limit, False if exceeded
    """
    redis = await get_redis_client()

    if not redis:
        # If Redis unavailable, allow the request (fail open)
        logger.warning("Rate limit check skipped - Redis unavailable", extra={
            "operation": "rate_limit_check",
            "user_id": user_id
        })
        return True

    key = f"rate_limit:analysis:{user_id}"

    try:
        # Get current count
        current_count = await redis.get(key)

        if current_count is None:
            # First request in window
            await redis.setex(key, RATE_LIMIT_WINDOW_SECONDS, 1)
            return True

        count = int(current_count)

        if count >= ANALYSIS_RATE_LIMIT:
            logger.info("Rate limit exceeded", extra={
                "operation": "rate_limit_exceeded",
                "user_id": user_id,
                "current_count": count,
                "limit": ANALYSIS_RATE_LIMIT
            })
            return False

        # Increment count
        await redis.incr(key)
        return True

    except Exception as e:
        logger.error(f"Rate limit check error: {e}", extra={
            "operation": "rate_limit_error",
            "user_id": user_id
        })
        # Fail open on errors
        return True


async def get_rate_limit_remaining(user_id: str) -> dict:
    """
    Get remaining rate limit info for user

    Args:
        user_id: User UUID string

    Returns:
        Dict with limit, remaining, and reset time
    """
    redis = await get_redis_client()

    result = {
        "limit": ANALYSIS_RATE_LIMIT,
        "remaining": ANALYSIS_RATE_LIMIT,
        "reset_seconds": RATE_LIMIT_WINDOW_SECONDS
    }

    if not redis:
        return result

    key = f"rate_limit:analysis:{user_id}"

    try:
        current_count = await redis.get(key)
        ttl = await redis.ttl(key)

        if current_count:
            result["remaining"] = max(0, ANALYSIS_RATE_LIMIT - int(current_count))

        if ttl > 0:
            result["reset_seconds"] = ttl

    except Exception:
        pass

    return result


class RateLimitExceeded(HTTPException):
    """Exception raised when rate limit is exceeded"""

    def __init__(self, limit: int, reset_seconds: int):
        super().__init__(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"You have exceeded the limit of {limit} analyses per hour",
                "limit": limit,
                "reset_seconds": reset_seconds
            },
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_seconds),
                "Retry-After": str(reset_seconds)
            }
        )
