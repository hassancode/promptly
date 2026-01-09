"""User service for authentication business logic"""
import secrets
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.user import User
from schemas.user import UserRegister, UserLogin
from core.security import hash_password, verify_password
from core.exceptions import AppException
from fastapi import status
from typing import Optional, Union


class UserService:
    """Service for user-related operations"""

    def __init__(self, db: Session):
        self.db = db

    def register(self, user_data: UserRegister) -> User:
        """
        Register a new user

        Args:
            user_data: Registration data (email, password)

        Returns:
            Created user object

        Raises:
            AppException: If email already exists
        """
        # Check if email already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise AppException(
                message="Email already registered",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Generate verification token
        verification_token = secrets.token_urlsafe(32)

        # Create user
        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            verified=False,  # Require email verification
            verification_token=verification_token,
        )

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError:
            self.db.rollback()
            raise AppException(
                message="Email already registered",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        return user

    def verify_email(self, token: str) -> User:
        """
        Verify user email with token

        Args:
            token: Verification token from email

        Returns:
            Verified user object

        Raises:
            AppException: If token is invalid or expired
        """
        user = self.db.query(User).filter(User.verification_token == token).first()

        if not user:
            raise AppException(
                message="Invalid or expired verification token",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if user.verified:
            return user  # Already verified, just return

        # Mark as verified and clear token
        user.verified = True
        user.verification_token = None
        self.db.commit()
        self.db.refresh(user)

        return user

    def login(self, credentials: UserLogin) -> User:
        """
        Authenticate user and create session

        Args:
            credentials: Login credentials (email, password)

        Returns:
            Authenticated user object

        Raises:
            AppException: If credentials are invalid or user not verified
        """
        # Find user by email
        user = self.db.query(User).filter(User.email == credentials.email).first()

        if not user:
            raise AppException(
                message="Invalid email or password",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        # Verify password
        if not verify_password(credentials.password, user.password_hash):
            raise AppException(
                message="Invalid email or password",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        # Check if email is verified
        # NOTE: For MVP, we'll allow unverified users to login
        # In production, uncomment this block:
        # if not user.verified:
        #     raise AppException(
        #         message="Please verify your email before logging in",
        #         status_code=status.HTTP_403_FORBIDDEN
        #     )

        return user

    def get_user_by_id(self, user_id: Union[str, UUID]) -> Optional[User]:
        """
        Get user by ID

        Args:
            user_id: User UUID (string or UUID object)

        Returns:
            User object or None if not found
        """
        # Convert string to UUID if necessary
        if isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except (ValueError, AttributeError):
                return None  # Invalid UUID string

        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email

        Args:
            email: User email address

        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.email == email).first()
