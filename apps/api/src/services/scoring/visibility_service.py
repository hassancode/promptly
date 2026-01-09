"""Visibility scoring service"""
from typing import List, Dict, Optional
from dataclasses import dataclass

from core.logging import get_logger
from .mention_service import MentionService, MentionResult

logger = get_logger(__name__)


@dataclass
class VisibilityScore:
    """Visibility score breakdown"""
    entity_name: str
    presence: float  # 0-1: Whether entity is mentioned at all
    frequency: float  # 0-1: How often entity is mentioned relative to others
    position: float  # 0-1: How prominently positioned (earlier = higher)
    composite: float  # Weighted composite score

    def to_dict(self) -> Dict:
        return {
            "entity_name": self.entity_name,
            "presence": round(self.presence, 3),
            "frequency": round(self.frequency, 3),
            "position": round(self.position, 3),
            "composite": round(self.composite, 3),
        }


class VisibilityService:
    """
    Service for calculating visibility scores.

    Visibility score formula:
    composite = 0.4 * presence + 0.3 * frequency + 0.3 * position

    - Presence: 1.0 if mentioned in any response, 0.0 otherwise
    - Frequency: normalized count relative to max mentions across all entities
    - Position: based on first mention position, with decay (first=1.0, decay 0.1 per position, min 0.5)
    """

    # Weight configuration
    PRESENCE_WEIGHT = 0.4
    FREQUENCY_WEIGHT = 0.3
    POSITION_WEIGHT = 0.3

    # Position scoring config
    POSITION_DECAY = 0.1
    MIN_POSITION_SCORE = 0.5

    def __init__(self):
        self.mention_service = MentionService()

    def calculate_presence_score(self, mention_result: MentionResult) -> float:
        """Calculate presence score (1.0 if mentioned, 0.0 otherwise)"""
        return 1.0 if mention_result.total_count > 0 else 0.0

    def calculate_frequency_score(
        self,
        mention_result: MentionResult,
        max_mentions: int
    ) -> float:
        """
        Calculate normalized frequency score.

        Args:
            mention_result: Mention analysis result
            max_mentions: Maximum mentions across all entities (for normalization)

        Returns:
            Normalized frequency score (0-1)
        """
        if max_mentions == 0:
            return 0.0
        return min(1.0, mention_result.total_count / max_mentions)

    def calculate_position_score(
        self,
        mention_result: MentionResult,
        text_length: int
    ) -> float:
        """
        Calculate position score based on first mention.

        Earlier mentions score higher, with a decay factor.
        Formula: max(MIN_POSITION_SCORE, 1.0 - (relative_position * POSITION_DECAY * 10))

        Args:
            mention_result: Mention analysis result
            text_length: Total length of text for normalization

        Returns:
            Position score (MIN_POSITION_SCORE to 1.0)
        """
        if mention_result.first_mention_position is None or text_length == 0:
            return 0.0

        # Calculate relative position (0 = start, 1 = end)
        relative_position = mention_result.first_mention_position / text_length

        # Apply decay: earlier positions score higher
        score = 1.0 - (relative_position * self.POSITION_DECAY * 10)
        return max(self.MIN_POSITION_SCORE, min(1.0, score))

    def calculate_visibility_score(
        self,
        entity_name: str,
        responses: List[Dict],
        all_mention_results: Optional[Dict[str, MentionResult]] = None
    ) -> VisibilityScore:
        """
        Calculate comprehensive visibility score for an entity.

        Args:
            entity_name: Brand or competitor name
            responses: List of response dicts with text, provider, prompt_id
            all_mention_results: Pre-computed mention results for all entities (for normalization)

        Returns:
            VisibilityScore with all component scores
        """
        # Get mention analysis
        mention_result = self.mention_service.analyze_mentions(entity_name, responses)

        # Calculate total text length for position scoring
        total_text = " ".join(r.get("text", "") for r in responses)
        text_length = len(total_text)

        # Calculate presence
        presence = self.calculate_presence_score(mention_result)

        # Calculate frequency (need max for normalization)
        if all_mention_results:
            max_mentions = max(
                mr.total_count for mr in all_mention_results.values()
            ) if all_mention_results else mention_result.total_count
        else:
            max_mentions = mention_result.total_count

        frequency = self.calculate_frequency_score(mention_result, max_mentions)

        # Calculate position
        position = self.calculate_position_score(mention_result, text_length)

        # Calculate weighted composite
        composite = (
            self.PRESENCE_WEIGHT * presence +
            self.FREQUENCY_WEIGHT * frequency +
            self.POSITION_WEIGHT * position
        )

        score = VisibilityScore(
            entity_name=entity_name,
            presence=presence,
            frequency=frequency,
            position=position,
            composite=composite,
        )

        logger.info(
            "Visibility score calculated",
            extra={
                "entity": entity_name,
                "composite": round(composite, 3),
                "presence": round(presence, 3),
                "frequency": round(frequency, 3),
                "position": round(position, 3),
            }
        )

        return score

    def compare_visibility(
        self,
        brand_name: str,
        competitor_names: List[str],
        responses: List[Dict],
    ) -> Dict[str, VisibilityScore]:
        """
        Compare visibility scores between brand and competitors.

        Args:
            brand_name: Main brand to analyze
            competitor_names: List of competitor names
            responses: List of response dicts

        Returns:
            Dict mapping entity names to their VisibilityScore
        """
        # First, get all mention results for normalization
        all_entities = [brand_name] + competitor_names
        mention_results = self.mention_service.compare_mention_frequencies(
            brand_name, competitor_names, responses
        )

        # Calculate visibility for each entity
        scores = {}
        for entity in all_entities:
            scores[entity] = self.calculate_visibility_score(
                entity, responses, mention_results
            )

        return scores

    def rank_by_visibility(
        self,
        visibility_scores: Dict[str, VisibilityScore]
    ) -> List[VisibilityScore]:
        """
        Rank entities by visibility score (highest first).

        Args:
            visibility_scores: Dict of entity name to VisibilityScore

        Returns:
            List of VisibilityScore sorted by composite score descending
        """
        return sorted(
            visibility_scores.values(),
            key=lambda s: s.composite,
            reverse=True
        )
