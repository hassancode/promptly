"""Authentication router for user registration, login, and verification"""
from fastapi import APIRouter, Depends, Response, Request, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.dependencies import get_current_user, session_store
from core.security import generate_session_id, set_session_cookie, clear_session_cookie
from core.exceptions import AppException
from core.logging import logger
from services.user_service import UserService
from services.email_service import email_service
from schemas.user import UserRegister, UserLogin, UserResponse, UserVerify
from models.user import User


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Register a new user account

    - Creates user with email and hashed password
    - Generates verification token
    - Sends verification email
    - Returns user data (excluding password)
    """
    logger.info(
        "User registration attempt",
        extra={"operation": "register", "email": user_data.email}
    )

    user_service = UserService(db)

    try:
        # Register user
        user = user_service.register(user_data)

        # Send verification email
        await email_service.send_verification_email(
            to_email=user.email,
            verification_token=user.verification_token
        )

        logger.info(
            "User registered successfully",
            extra={
                "operation": "register",
                "user_id": str(user.id),
                "email": user.email
            }
        )

        # Convert to response model
        return UserResponse(
            id=str(user.id),
            email=user.email,
            verified=user.verified,
            created_at=user.created_at
        )

    except AppException:
        raise
    except Exception as e:
        logger.error(
            f"Registration failed: {e}",
            extra={"operation": "register", "email": user_data.email}
        )
        raise AppException(
            message="Registration failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/verify", response_model=UserResponse)
async def verify_email(
    verification_data: UserVerify,
    db: Session = Depends(get_db)
):
    """
    Verify user email address with token from email

    - Validates verification token
    - Marks user as verified
    - Sends welcome email
    - Returns updated user data
    """
    logger.info(
        "Email verification attempt",
        extra={"operation": "verify_email"}
    )

    user_service = UserService(db)

    try:
        # Verify email
        user = user_service.verify_email(verification_data.token)

        # Send welcome email
        await email_service.send_welcome_email(to_email=user.email)

        logger.info(
            "Email verified successfully",
            extra={
                "operation": "verify_email",
                "user_id": str(user.id),
                "email": user.email
            }
        )

        return UserResponse(
            id=str(user.id),
            email=user.email,
            verified=user.verified,
            created_at=user.created_at
        )

    except AppException:
        raise
    except Exception as e:
        logger.error(
            f"Email verification failed: {e}",
            extra={"operation": "verify_email"}
        )
        raise AppException(
            message="Email verification failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/login", response_model=UserResponse)
async def login(
    credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and create session

    - Validates credentials
    - Creates session in Redis
    - Sets HTTP-only session cookie
    - Returns user data
    """
    logger.info(
        "Login attempt",
        extra={"operation": "login", "email": credentials.email}
    )

    user_service = UserService(db)

    try:
        # Authenticate user
        user = user_service.login(credentials)

        # Create session
        session_id = generate_session_id()
        session_data = {
            "user_id": str(user.id),
            "email": user.email,
        }

        await session_store.create(session_id, session_data)

        # Set session cookie
        set_session_cookie(response, session_id)

        logger.info(
            "User logged in successfully",
            extra={
                "operation": "login",
                "user_id": str(user.id),
                "email": user.email
            }
        )

        return UserResponse(
            id=str(user.id),
            email=user.email,
            verified=user.verified,
            created_at=user.created_at
        )

    except AppException:
        raise
    except Exception as e:
        logger.error(
            f"Login failed: {e}",
            extra={"operation": "login", "email": credentials.email}
        )
        raise AppException(
            message="Login failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response
):
    """
    Logout user and destroy session

    - Deletes session from Redis
    - Clears session cookie
    - Returns success message
    """
    # Get session ID from cookie
    session_id = request.cookies.get("promptly_session")

    if session_id:
        # Delete session from Redis
        await session_store.delete(session_id)

        logger.info(
            "User logged out",
            extra={"operation": "logout"}
        )

    # Clear session cookie
    clear_session_cookie(response)

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information

    - Requires valid session
    - Returns current user data
    """
    logger.info(
        "Get current user",
        extra={
            "operation": "get_me",
            "user_id": str(current_user.id)
        }
    )

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        verified=current_user.verified,
        created_at=current_user.created_at
    )
