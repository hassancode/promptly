"""
Confidence Level Service

Calculates confidence levels for AI responses based on citation coverage.
"""
from enum import Enum
from typing import List, Optional

from models.ai_response import AIResponse
from models.citation import Citation


class ConfidenceLevel(str, Enum):
    """Confidence level enumeration"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


def calculate_confidence_level(
    response: AIResponse,
    citation_threshold_high: int = 3,
    citation_threshold_medium: int = 1,
) -> ConfidenceLevel:
    """
    Calculate confidence level for an AI response based on citation coverage.

    Logic:
    - HIGH: Response has 3+ citations and complete coverage
    - MEDIUM: Response has 1-2 citations OR partial coverage
    - LOW: Response has no citations but has content
    - NONE: Response has no content or failed

    Args:
        response: AIResponse object
        citation_threshold_high: Minimum citations for HIGH confidence (default: 3)
        citation_threshold_medium: Minimum citations for MEDIUM confidence (default: 1)

    Returns:
        ConfidenceLevel enum value
    """
    # Check if response has content
    if not response.answer_text or not response.answer_text.get("text"):
        return ConfidenceLevel.NONE

    # Count citations
    citation_count = len(response.citations) if response.citations else 0

    # Check citation coverage
    coverage = response.citation_coverage or "none"

    # HIGH: 3+ citations with complete coverage
    if citation_count >= citation_threshold_high and coverage == "complete":
        return ConfidenceLevel.HIGH

    # MEDIUM: 1-2 citations OR partial coverage
    if citation_count >= citation_threshold_medium or coverage == "partial":
        return ConfidenceLevel.MEDIUM

    # LOW: Has content but no/few citations
    if citation_count < citation_threshold_medium:
        return ConfidenceLevel.LOW

    # Default to LOW
    return ConfidenceLevel.LOW


def calculate_aggregate_confidence(
    responses: List[AIResponse],
) -> ConfidenceLevel:
    """
    Calculate aggregate confidence level across multiple responses.

    Logic:
    - HIGH: Majority (>50%) of responses have HIGH confidence
    - MEDIUM: At least one response has MEDIUM+ confidence
    - LOW: At least one response has LOW+ confidence
    - NONE: All responses are NONE or no responses

    Args:
        responses: List of AIResponse objects

    Returns:
        ConfidenceLevel enum value
    """
    if not responses:
        return ConfidenceLevel.NONE

    # Calculate individual confidence levels
    confidence_levels = [calculate_confidence_level(r) for r in responses]

    # Count by level
    high_count = sum(1 for c in confidence_levels if c == ConfidenceLevel.HIGH)
    medium_count = sum(1 for c in confidence_levels if c == ConfidenceLevel.MEDIUM)
    low_count = sum(1 for c in confidence_levels if c == ConfidenceLevel.LOW)
    none_count = sum(1 for c in confidence_levels if c == ConfidenceLevel.NONE)

    total_count = len(confidence_levels)

    # Aggregate logic
    if high_count > total_count / 2:
        return ConfidenceLevel.HIGH
    elif medium_count > 0 or high_count > 0:
        return ConfidenceLevel.MEDIUM
    elif low_count > 0:
        return ConfidenceLevel.LOW
    else:
        return ConfidenceLevel.NONE


def get_confidence_color(level: ConfidenceLevel) -> str:
    """
    Get Tailwind CSS color class for confidence level.

    Args:
        level: ConfidenceLevel enum value

    Returns:
        Tailwind color class string (e.g., "green", "yellow", "red")
    """
    color_map = {
        ConfidenceLevel.HIGH: "green",
        ConfidenceLevel.MEDIUM: "yellow",
        ConfidenceLevel.LOW: "orange",
        ConfidenceLevel.NONE: "gray",
    }
    return color_map.get(level, "gray")


def get_confidence_description(level: ConfidenceLevel) -> str:
    """
    Get human-readable description for confidence level.

    Args:
        level: ConfidenceLevel enum value

    Returns:
        Description string
    """
    descriptions = {
        ConfidenceLevel.HIGH: "Strong evidence with multiple credible citations",
        ConfidenceLevel.MEDIUM: "Moderate evidence with some citations",
        ConfidenceLevel.LOW: "Limited evidence or missing citations",
        ConfidenceLevel.NONE: "No evidence or response unavailable",
    }
    return descriptions.get(level, "Unknown confidence level")
