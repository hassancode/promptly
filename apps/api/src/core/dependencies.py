"""FastAPI dependencies for authentication and database"""
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from core.database import get_db
from core.session_store import SessionStore
from core.exceptions import AppException
from services.user_service import UserService
from models.user import User
from fastapi import status
from typing import Optional


# Session store instance
session_store = SessionStore()


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from session

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        Current authenticated user

    Raises:
        AppException: If user is not authenticated or session is invalid
    """
    # Get session ID from cookie
    session_id = request.cookies.get("promptly_session")

    if not session_id:
        raise AppException(
            message="Not authenticated",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # Get session data from Redis
    session_data = await session_store.read(session_id)

    if not session_data:
        raise AppException(
            message="Invalid or expired session",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # Get user from database
    user_id = session_data.get("user_id")
    if not user_id:
        raise AppException(
            message="Invalid session data",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)

    if not user:
        raise AppException(
            message="User not found",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    return user


async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get current user if authenticated, None otherwise

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        Current user or None if not authenticated
    """
    try:
        return await get_current_user(request, db)
    except AppException:
        return None
