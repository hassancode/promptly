"""Email service for sending verification and notification emails"""
from core.logging import logger
from typing import Optional


class EmailService:
    """
    Service for sending emails

    For MVP: Logs emails to console instead of actually sending them
    In production: Integrate with SMTP server or email service (SendGrid, AWS SES, etc.)
    """

    def __init__(self):
        self.from_email = "noreply@promptly.com"

    async def send_verification_email(self, to_email: str, verification_token: str) -> bool:
        """
        Send email verification link

        Args:
            to_email: Recipient email address
            verification_token: Verification token to include in link

        Returns:
            True if email sent successfully
        """
        # Construct verification URL
        # In production, this should use FRONTEND_URL from config
        verification_url = f"http://localhost:3000/verify?token={verification_token}"

        # For MVP: Log email instead of sending
        logger.info(
            "Verification email",
            extra={
                "operation": "send_verification_email",
                "to_email": to_email,
                "verification_url": verification_url,
            }
        )

        print(f"\n{'='*60}")
        print(f"📧 VERIFICATION EMAIL (MVP - Not Actually Sent)")
        print(f"{'='*60}")
        print(f"To: {to_email}")
        print(f"From: {self.from_email}")
        print(f"Subject: Verify your Promptly account")
        print(f"\nPlease verify your email by clicking this link:")
        print(f"{verification_url}")
        print(f"{'='*60}\n")

        # In production, implement actual email sending:
        # try:
        #     smtp_server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        #     smtp_server.starttls()
        #     smtp_server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        #     ...
        #     return True
        # except Exception as e:
        #     logger.error(f"Failed to send email: {e}")
        #     return False

        return True

    async def send_password_reset_email(
        self, to_email: str, reset_token: str
    ) -> bool:
        """
        Send password reset link

        Args:
            to_email: Recipient email address
            reset_token: Password reset token

        Returns:
            True if email sent successfully
        """
        reset_url = f"http://localhost:3000/reset-password?token={reset_token}"

        logger.info(
            "Password reset email",
            extra={
                "operation": "send_password_reset_email",
                "to_email": to_email,
                "reset_url": reset_url,
            }
        )

        print(f"\n{'='*60}")
        print(f"📧 PASSWORD RESET EMAIL (MVP - Not Actually Sent)")
        print(f"{'='*60}")
        print(f"To: {to_email}")
        print(f"From: {self.from_email}")
        print(f"Subject: Reset your Promptly password")
        print(f"\nReset your password by clicking this link:")
        print(f"{reset_url}")
        print(f"{'='*60}\n")

        return True

    async def send_welcome_email(self, to_email: str, user_name: Optional[str] = None) -> bool:
        """
        Send welcome email after successful verification

        Args:
            to_email: Recipient email address
            user_name: Optional user name

        Returns:
            True if email sent successfully
        """
        logger.info(
            "Welcome email",
            extra={
                "operation": "send_welcome_email",
                "to_email": to_email,
            }
        )

        print(f"\n{'='*60}")
        print(f"📧 WELCOME EMAIL (MVP - Not Actually Sent)")
        print(f"{'='*60}")
        print(f"To: {to_email}")
        print(f"From: {self.from_email}")
        print(f"Subject: Welcome to Promptly!")
        print(f"\nWelcome to Promptly - AI Search Visibility Platform")
        print(f"Start analyzing your brand's visibility in AI-generated answers")
        print(f"{'='*60}\n")

        return True


# Global email service instance
email_service = EmailService()
