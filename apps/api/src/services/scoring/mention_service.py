"""Mention frequency calculation service"""
import re
from typing import List, Dict, Optional
from dataclasses import dataclass

from core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class MentionResult:
    """Result of mention frequency analysis"""
    entity_name: str
    total_count: int
    by_provider: Dict[str, int]
    by_prompt: Dict[str, int]
    positions: List[int]  # Character positions of mentions
    first_mention_position: Optional[int]


class MentionService:
    """
    Service for calculating mention frequency of brands and competitors.

    Counts how many times an entity is mentioned across AI responses,
    tracking frequency by provider and prompt.
    """

    def __init__(self):
        self._cache: Dict[str, MentionResult] = {}

    def count_mentions(
        self,
        entity_name: str,
        text: str,
        case_sensitive: bool = False
    ) -> int:
        """
        Count occurrences of entity name in text.

        Args:
            entity_name: The brand or competitor name to search for
            text: The text to search in
            case_sensitive: Whether to perform case-sensitive matching

        Returns:
            Number of mentions found
        """
        if not text or not entity_name:
            return 0

        # Escape special regex characters in entity name
        escaped_name = re.escape(entity_name)

        # Build pattern with word boundaries to avoid partial matches
        pattern = rf'\b{escaped_name}\b'
        flags = 0 if case_sensitive else re.IGNORECASE

        matches = re.findall(pattern, text, flags)
        return len(matches)

    def find_mention_positions(
        self,
        entity_name: str,
        text: str,
        case_sensitive: bool = False
    ) -> List[int]:
        """
        Find character positions of all mentions.

        Args:
            entity_name: The brand or competitor name to search for
            text: The text to search in
            case_sensitive: Whether to perform case-sensitive matching

        Returns:
            List of character positions where mentions start
        """
        if not text or not entity_name:
            return []

        escaped_name = re.escape(entity_name)
        pattern = rf'\b{escaped_name}\b'
        flags = 0 if case_sensitive else re.IGNORECASE

        positions = [match.start() for match in re.finditer(pattern, text, flags)]
        return positions

    def analyze_mentions(
        self,
        entity_name: str,
        responses: List[Dict],
    ) -> MentionResult:
        """
        Perform comprehensive mention analysis across multiple responses.

        Args:
            entity_name: The brand or competitor name to analyze
            responses: List of response dicts with keys:
                - text: The response text
                - provider: Provider name (e.g., "openai", "claude")
                - prompt_id: ID of the prompt that generated this response

        Returns:
            MentionResult with comprehensive frequency data
        """
        total_count = 0
        by_provider: Dict[str, int] = {}
        by_prompt: Dict[str, int] = {}
        all_positions: List[int] = []
        first_position: Optional[int] = None

        for response in responses:
            text = response.get("text", "")
            provider = response.get("provider", "unknown")
            prompt_id = response.get("prompt_id", "unknown")

            # Count mentions in this response
            count = self.count_mentions(entity_name, text)
            total_count += count

            # Track by provider
            by_provider[provider] = by_provider.get(provider, 0) + count

            # Track by prompt
            by_prompt[prompt_id] = by_prompt.get(prompt_id, 0) + count

            # Find positions
            positions = self.find_mention_positions(entity_name, text)
            if positions:
                all_positions.extend(positions)
                if first_position is None or positions[0] < first_position:
                    first_position = positions[0]

        result = MentionResult(
            entity_name=entity_name,
            total_count=total_count,
            by_provider=by_provider,
            by_prompt=by_prompt,
            positions=sorted(all_positions),
            first_mention_position=first_position,
        )

        logger.info(
            "Mention analysis complete",
            extra={
                "entity": entity_name,
                "total_mentions": total_count,
                "providers": list(by_provider.keys()),
            }
        )

        return result

    def compare_mention_frequencies(
        self,
        brand_name: str,
        competitor_names: List[str],
        responses: List[Dict],
    ) -> Dict[str, MentionResult]:
        """
        Compare mention frequencies between brand and competitors.

        Args:
            brand_name: The main brand to analyze
            competitor_names: List of competitor names
            responses: List of response dicts

        Returns:
            Dict mapping entity names to their MentionResult
        """
        results = {}

        # Analyze brand
        results[brand_name] = self.analyze_mentions(brand_name, responses)

        # Analyze each competitor
        for competitor in competitor_names:
            results[competitor] = self.analyze_mentions(competitor, responses)

        return results
