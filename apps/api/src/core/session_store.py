"""Redis-backed session store"""
import json
from typing import Optional, Dict, Any
from .redis import get_redis
from .config import settings


class SessionStore:
    """Manages user sessions in Redis"""

    def __init__(self):
        self.ttl = settings.SESSION_TTL_SECONDS

    async def create(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Create a new session

        Args:
            session_id: Unique session identifier
            data: Session data to store (typically contains user_id)
        """
        redis_client = await get_redis()
        session_key = f"session:{session_id}"

        # Store session data as JSON with TTL
        await redis_client.setex(
            session_key, self.ttl, json.dumps(data)
        )

    async def read(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Read session data

        Args:
            session_id: Session identifier to retrieve

        Returns:
            Session data dictionary, or None if session doesn't exist
        """
        redis_client = await get_redis()
        session_key = f"session:{session_id}"

        data = await redis_client.get(session_key)
        if data is None:
            return None

        return json.loads(data)

    async def delete(self, session_id: str) -> None:
        """
        Delete a session

        Args:
            session_id: Session identifier to delete
        """
        redis_client = await get_redis()
        session_key = f"session:{session_id}"

        await redis_client.delete(session_key)

    async def refresh(self, session_id: str) -> bool:
        """
        Refresh session TTL

        Args:
            session_id: Session identifier to refresh

        Returns:
            True if session was refreshed, False if session doesn't exist
        """
        redis_client = await get_redis()
        session_key = f"session:{session_id}"

        # Check if session exists
        exists = await redis_client.exists(session_key)
        if not exists:
            return False

        # Reset TTL
        await redis_client.expire(session_key, self.ttl)
        return True


# Global session store instance
session_store = SessionStore()
