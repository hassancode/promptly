"""
Prompt service

Business logic for prompt management and AI suggestions.
"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import status

from models.analysis import Analysis
from models.prompt import Prompt
from models.user import User
from schemas.prompt import PromptAdd, PromptSuggestion
from services.claude_adapter import ClaudeAdapter
from core.exceptions import AppException
from core.logging import get_logger

logger = get_logger(__name__)

# Business rules
MAX_PROMPTS_PER_ANALYSIS = 7


class PromptService:
    """
    Service for prompt operations

    Handles:
    - Generating AI prompt suggestions
    - Adding custom prompts with validation
    - Enforcing business rules (max prompts, no duplicates)
    """

    def __init__(self, db: Session):
        self.db = db
        self.claude = ClaudeAdapter()

    async def suggest_prompts(
        self,
        user: User,
        analysis: Analysis
    ) -> List[PromptSuggestion]:
        """
        Generate AI prompt suggestions for an analysis

        Args:
            user: The authenticated user
            analysis: The analysis to generate prompts for

        Returns:
            List of suggested prompts

        Raises:
            AppException: If analysis not owned by user
        """
        # Verify ownership
        if str(analysis.user_id) != str(user.id):
            raise AppException(
                "Not authorized to access this analysis",
                status.HTTP_403_FORBIDDEN
            )

        logger.info(
            f"Generating prompt suggestions for analysis {analysis.id}",
            extra={
                "user_id": str(user.id),
                "analysis_id": str(analysis.id),
                "brand_name": analysis.brand_name
            }
        )

        try:
            # Get competitor names
            competitor_names = [c.name for c in analysis.competitors]

            # Get suggestions from Claude
            prompt_texts = await self.claude.suggest_prompts(
                brand_name=analysis.brand_name,
                competitors=competitor_names,
                max_suggestions=5
            )

            # Convert to schema objects
            suggestions = [
                PromptSuggestion(text=text, is_suggested=True)
                for text in prompt_texts
            ]

            logger.info(
                f"Generated {len(suggestions)} prompt suggestions",
                extra={
                    "analysis_id": str(analysis.id),
                    "suggestions_count": len(suggestions)
                }
            )

            return suggestions

        except Exception as e:
            logger.error(
                f"Error generating prompt suggestions: {e}",
                exc_info=True,
                extra={"analysis_id": str(analysis.id)}
            )
            # Don't fail completely - return empty suggestions
            return []

    def add_prompt(
        self,
        user: User,
        analysis: Analysis,
        prompt_data: PromptAdd
    ) -> Prompt:
        """
        Add a custom prompt to an analysis

        Args:
            user: The authenticated user
            analysis: The analysis to add prompt to
            prompt_data: Prompt data

        Returns:
            Created prompt

        Raises:
            AppException: If validation fails or limits exceeded
        """
        # Verify ownership
        if str(analysis.user_id) != str(user.id):
            raise AppException(
                "Not authorized to access this analysis",
                status.HTTP_403_FORBIDDEN
            )

        prompt_text = prompt_data.prompt_text.strip()

        logger.info(
            f"Adding prompt to analysis {analysis.id}",
            extra={
                "user_id": str(user.id),
                "analysis_id": str(analysis.id),
                "prompt_length": len(prompt_text)
            }
        )

        # Check prompt limit
        existing_count = len(analysis.prompts)
        if existing_count >= MAX_PROMPTS_PER_ANALYSIS:
            raise AppException(
                f"Maximum {MAX_PROMPTS_PER_ANALYSIS} prompts allowed per analysis",
                status.HTTP_400_BAD_REQUEST
            )

        # Check for duplicate (case-insensitive)
        duplicate = self.db.query(Prompt).filter(
            Prompt.analysis_id == analysis.id,
            Prompt.text.ilike(prompt_text)
        ).first()

        if duplicate:
            raise AppException(
                "This prompt has already been added to this analysis",
                status.HTTP_400_BAD_REQUEST
            )

        # Create prompt
        prompt = Prompt(
            analysis_id=analysis.id,
            text=prompt_text,
            is_suggested=False  # User-added, not AI-suggested
        )

        self.db.add(prompt)
        self.db.commit()
        self.db.refresh(prompt)

        logger.info(
            f"Prompt added successfully",
            extra={
                "analysis_id": str(analysis.id),
                "prompt_id": str(prompt.id)
            }
        )

        return prompt

    def get_analysis(self, user: User, analysis_id: str) -> Analysis:
        """
        Get analysis and verify user ownership

        Args:
            user: The authenticated user
            analysis_id: ID of the analysis

        Returns:
            Analysis if found and owned by user

        Raises:
            AppException: If not found or not owned by user
        """
        # Convert string to UUID if necessary for SQLite compatibility
        try:
            uuid_id = UUID(analysis_id) if isinstance(analysis_id, str) else analysis_id
        except ValueError:
            raise AppException(
                "Invalid analysis ID format",
                status.HTTP_400_BAD_REQUEST
            )

        analysis = self.db.query(Analysis).filter(
            Analysis.id == uuid_id
        ).first()

        if not analysis:
            raise AppException(
                "Analysis not found",
                status.HTTP_404_NOT_FOUND
            )

        # Verify ownership
        if str(analysis.user_id) != str(user.id):
            raise AppException(
                "Not authorized to access this analysis",
                status.HTTP_403_FORBIDDEN
            )

        return analysis
