"""
Analysis service

Business logic for brand analysis and competitor management.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import status

from models.analysis import Analysis, AnalysisStatus
from models.competitor import Competitor
from models.user import User
from schemas.analysis import (
    AnalysisCreate,
    CompetitorAdd,
    CompetitorSuggestion,
)
from services.claude_adapter import ClaudeAdapter
from core.exceptions import AppException
from core.logging import get_logger

logger = get_logger(__name__)

# Business rules
MAX_COMPETITORS_PER_ANALYSIS = 5


class AnalysisService:
    """
    Service for analysis operations

    Handles:
    - Creating analyses with brand validation
    - Generating AI competitor suggestions
    - Adding competitors with validation
    - Enforcing business rules (max competitors, no duplicates)
    """

    def __init__(self, db: Session):
        self.db = db
        self.claude = ClaudeAdapter()

    def create_analysis(
        self,
        user: User,
        analysis_data: AnalysisCreate
    ) -> Analysis:
        """
        Create a new brand analysis

        Args:
            user: The authenticated user
            analysis_data: Analysis creation data

        Returns:
            Created analysis

        Raises:
            AppException: If validation fails
        """
        logger.info(
            f"Creating analysis for user {user.id}",
            extra={"user_id": str(user.id), "brand_name": analysis_data.brand_name}
        )

        # Validate brand name (Pydantic already validates non-empty)
        brand_name = analysis_data.brand_name.strip()

        # Create analysis
        analysis = Analysis(
            user_id=user.id,
            brand_name=brand_name,
            status=AnalysisStatus.DRAFT,
        )

        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)

        logger.info(
            f"Analysis created successfully",
            extra={"analysis_id": str(analysis.id), "brand_name": brand_name}
        )

        return analysis

    async def suggest_competitors(
        self,
        user: User,
        analysis_id: str
    ) -> List[CompetitorSuggestion]:
        """
        Generate AI competitor suggestions for an analysis

        Args:
            user: The authenticated user
            analysis_id: ID of the analysis

        Returns:
            List of suggested competitors

        Raises:
            AppException: If analysis not found or not owned by user
        """
        # Get and validate analysis ownership
        analysis = self._get_user_analysis(user, analysis_id)

        logger.info(
            f"Generating competitor suggestions for analysis {analysis_id}",
            extra={
                "user_id": str(user.id),
                "analysis_id": analysis_id,
                "brand_name": analysis.brand_name
            }
        )

        try:
            # Get suggestions from Claude
            competitor_names = await self.claude.suggest_competitors(
                brand_name=analysis.brand_name,
                context=None,  # TODO: Add context support if needed
                max_suggestions=3
            )

            # Convert to schema objects
            suggestions = [
                CompetitorSuggestion(name=name, is_suggested=True)
                for name in competitor_names
            ]

            logger.info(
                f"Generated {len(suggestions)} suggestions",
                extra={
                    "analysis_id": analysis_id,
                    "suggestions": [s.name for s in suggestions]
                }
            )

            return suggestions

        except Exception as e:
            logger.error(
                f"Error generating competitor suggestions: {e}",
                exc_info=True,
                extra={"analysis_id": analysis_id}
            )
            # Don't fail completely - return empty suggestions
            return []

    def add_competitor(
        self,
        user: User,
        analysis_id: str,
        competitor_data: CompetitorAdd
    ) -> Competitor:
        """
        Add a competitor to an analysis

        Args:
            user: The authenticated user
            analysis_id: ID of the analysis
            competitor_data: Competitor data

        Returns:
            Created competitor

        Raises:
            AppException: If validation fails or limits exceeded
        """
        # Get and validate analysis ownership
        analysis = self._get_user_analysis(user, analysis_id)

        competitor_name = competitor_data.competitor_name.strip()

        logger.info(
            f"Adding competitor to analysis {analysis_id}",
            extra={
                "user_id": str(user.id),
                "analysis_id": analysis_id,
                "competitor_name": competitor_name
            }
        )

        # Check competitor limit
        existing_count = len(analysis.competitors)
        if existing_count >= MAX_COMPETITORS_PER_ANALYSIS:
            raise AppException(
                f"Maximum {MAX_COMPETITORS_PER_ANALYSIS} competitors allowed per analysis",
                status.HTTP_400_BAD_REQUEST
            )

        # Check for duplicate (case-insensitive)
        duplicate = self.db.query(Competitor).filter(
            and_(
                Competitor.analysis_id == analysis.id,
                Competitor.name.ilike(competitor_name)
            )
        ).first()

        if duplicate:
            raise AppException(
                f"Competitor '{competitor_name}' already added to this analysis",
                status.HTTP_400_BAD_REQUEST
            )

        # Create competitor
        competitor = Competitor(
            analysis_id=analysis.id,
            name=competitor_name,
            is_suggested=False  # User-added, not AI-suggested
        )

        self.db.add(competitor)
        self.db.commit()
        self.db.refresh(competitor)

        logger.info(
            f"Competitor added successfully",
            extra={
                "analysis_id": analysis_id,
                "competitor_id": str(competitor.id),
                "competitor_name": competitor_name
            }
        )

        return competitor

    def _get_user_analysis(self, user: User, analysis_id: str) -> Analysis:
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
        analysis = self.db.query(Analysis).filter(
            Analysis.id == analysis_id
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

    def get_analysis_with_competitors(
        self,
        user: User,
        analysis_id: str
    ) -> Analysis:
        """
        Get analysis with all competitors

        Args:
            user: The authenticated user
            analysis_id: ID of the analysis

        Returns:
            Analysis with competitors loaded

        Raises:
            AppException: If not found or not owned by user
        """
        analysis = self._get_user_analysis(user, analysis_id)

        # Competitors are loaded via relationship
        return analysis
