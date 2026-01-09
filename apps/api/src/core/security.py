"""Security utilities for authentication and password hashing"""
import secrets
from passlib.context import CryptContext
from fastapi import Response, Request
from typing import Optional
from .config import settings

# Password hashing context using bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",  # Force bcrypt 2b variant to avoid auto-detection issues
    bcrypt__truncate_error=False  # Allow bcrypt to truncate passwords > 72 bytes
)

# Session cookie configuration
SESSION_COOKIE_NAME = "promptly_session"
SESSION_COOKIE_MAX_AGE = settings.SESSION_TTL_SECONDS


def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_session_id() -> str:
    """
    Generate a secure random session ID

    Returns:
        Cryptographically secure random session ID
    """
    return secrets.token_urlsafe(32)


def set_session_cookie(response: Response, session_id: str) -> None:
    """
    Set session cookie with security flags

    Args:
        response: FastAPI response object
        session_id: Session ID to store in cookie
    """
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        max_age=SESSION_COOKIE_MAX_AGE,
        httponly=True,  # Prevent JavaScript access
        samesite="lax",  # CSRF protection
        secure=settings.ENVIRONMENT == "production",  # HTTPS only in production
    )


def get_session_id(request: Request) -> Optional[str]:
    """
    Extract session ID from request cookies

    Args:
        request: FastAPI request object

    Returns:
        Session ID if present, None otherwise
    """
    return request.cookies.get(SESSION_COOKIE_NAME)


def clear_session_cookie(response: Response) -> None:
    """
    Clear session cookie (for logout)

    Args:
        response: FastAPI response object
    """
    response.delete_cookie(key=SESSION_COOKIE_NAME, samesite="lax")
