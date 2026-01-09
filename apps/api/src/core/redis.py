"""Redis client for session management"""
import redis.asyncio as redis
from typing import Optional
from .config import settings

# Global Redis client instance
_redis_client: Optional[redis.Redis] = None


async def get_redis() -> Optional[redis.Redis]:
    """
    Get or create Redis client

    Returns:
        Redis client instance
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )

    return _redis_client


async def close_redis():
    """Close Redis connection on shutdown"""
    global _redis_client

    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


# Alias for backward compatibility
get_redis_client = get_redis
