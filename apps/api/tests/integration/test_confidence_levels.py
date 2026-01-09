"""
Integration Tests for Confidence Level Calculation

Tests that confidence levels are calculated correctly based on citation coverage.
"""
import pytest
from services.confidence_service import (
    ConfidenceLevel,
    calculate_confidence_level,
    calculate_aggregate_confidence,
    get_confidence_color,
    get_confidence_description,
)
from models.ai_response import AIResponse, CitationCoverage
from models.citation import Citation


class MockAIResponse:
    """Mock AIResponse for testing"""
    def __init__(self, text: str, citations: list, coverage: str):
        self.answer_text = {"text": text}
        self.citations = citations
        self.citation_coverage = coverage


class MockCitation:
    """Mock Citation for testing"""
    def __init__(self):
        self.id = "test-citation"
        self.url = "https://example.com"
        self.title = "Test Citation"


def test_high_confidence_calculation():
    """
    Test HIGH confidence: 3+ citations with complete coverage
    """
    citations = [MockCitation() for _ in range(3)]
    response = MockAIResponse(
        text="This is a well-cited response",
        citations=citations,
        coverage="complete"
    )

    confidence = calculate_confidence_level(response)
    assert confidence == ConfidenceLevel.HIGH


def test_medium_confidence_with_partial_coverage():
    """
    Test MEDIUM confidence: Partial coverage
    """
    citations = [MockCitation() for _ in range(2)]
    response = MockAIResponse(
        text="This response has partial coverage",
        citations=citations,
        coverage="partial"
    )

    confidence = calculate_confidence_level(response)
    assert confidence == ConfidenceLevel.MEDIUM


def test_medium_confidence_with_few_citations():
    """
    Test MEDIUM confidence: 1-2 citations
    """
    citations = [MockCitation()]
    response = MockAIResponse(
        text="This response has one citation",
        citations=citations,
        coverage="none"
    )

    confidence = calculate_confidence_level(response)
    assert confidence == ConfidenceLevel.MEDIUM


def test_low_confidence_no_citations():
    """
    Test LOW confidence: Has content but no citations
    """
    response = MockAIResponse(
        text="This response has no citations",
        citations=[],
        coverage="none"
    )

    confidence = calculate_confidence_level(response)
    assert confidence == ConfidenceLevel.LOW


def test_none_confidence_no_content():
    """
    Test NONE confidence: No content
    """
    response = MockAIResponse(
        text="",
        citations=[],
        coverage="none"
    )

    confidence = calculate_confidence_level(response)
    assert confidence == ConfidenceLevel.NONE


def test_none_confidence_null_text():
    """
    Test NONE confidence: Null answer_text
    """
    response = MockAIResponse(
        text=None,
        citations=[],
        coverage="none"
    )
    response.answer_text = None

    confidence = calculate_confidence_level(response)
    assert confidence == ConfidenceLevel.NONE


def test_confidence_threshold_customization():
    """
    Test custom confidence thresholds
    """
    citations = [MockCitation() for _ in range(2)]
    response = MockAIResponse(
        text="Response with 2 citations",
        citations=citations,
        coverage="complete"
    )

    # With default thresholds (high=3, medium=1), 2 citations = MEDIUM
    confidence_default = calculate_confidence_level(response)
    assert confidence_default == ConfidenceLevel.MEDIUM

    # With custom thresholds (high=2, medium=1), 2 citations + complete = HIGH
    confidence_custom = calculate_confidence_level(
        response,
        citation_threshold_high=2,
        citation_threshold_medium=1
    )
    assert confidence_custom == ConfidenceLevel.HIGH


def test_aggregate_confidence_all_high():
    """
    Test aggregate confidence: Majority HIGH -> aggregate HIGH
    """
    responses = [
        MockAIResponse(
            text=f"Response {i}",
            citations=[MockCitation() for _ in range(3)],
            coverage="complete"
        )
        for i in range(3)
    ]

    aggregate = calculate_aggregate_confidence(responses)
    assert aggregate == ConfidenceLevel.HIGH


def test_aggregate_confidence_mixed():
    """
    Test aggregate confidence: Some HIGH, some MEDIUM -> MEDIUM
    """
    responses = [
        # 1 HIGH
        MockAIResponse(
            text="High response",
            citations=[MockCitation() for _ in range(3)],
            coverage="complete"
        ),
        # 2 MEDIUM
        MockAIResponse(
            text="Medium response 1",
            citations=[MockCitation()],
            coverage="partial"
        ),
        MockAIResponse(
            text="Medium response 2",
            citations=[MockCitation()],
            coverage="partial"
        ),
    ]

    aggregate = calculate_aggregate_confidence(responses)
    # Only 1/3 are HIGH (not >50%), so aggregate is MEDIUM
    assert aggregate == ConfidenceLevel.MEDIUM


def test_aggregate_confidence_mostly_low():
    """
    Test aggregate confidence: Mostly LOW -> LOW
    """
    responses = [
        MockAIResponse(
            text=f"Low response {i}",
            citations=[],
            coverage="none"
        )
        for i in range(3)
    ]

    aggregate = calculate_aggregate_confidence(responses)
    assert aggregate == ConfidenceLevel.LOW


def test_aggregate_confidence_empty_list():
    """
    Test aggregate confidence: No responses -> NONE
    """
    aggregate = calculate_aggregate_confidence([])
    assert aggregate == ConfidenceLevel.NONE


def test_aggregate_confidence_all_none():
    """
    Test aggregate confidence: All responses have NONE -> NONE
    """
    responses = [
        MockAIResponse(text="", citations=[], coverage="none")
        for _ in range(3)
    ]

    aggregate = calculate_aggregate_confidence(responses)
    assert aggregate == ConfidenceLevel.NONE


def test_confidence_color_mapping():
    """
    Test confidence level color mapping for UI
    """
    assert get_confidence_color(ConfidenceLevel.HIGH) == "green"
    assert get_confidence_color(ConfidenceLevel.MEDIUM) == "yellow"
    assert get_confidence_color(ConfidenceLevel.LOW) == "orange"
    assert get_confidence_color(ConfidenceLevel.NONE) == "gray"


def test_confidence_description():
    """
    Test confidence level descriptions
    """
    high_desc = get_confidence_description(ConfidenceLevel.HIGH)
    assert "multiple" in high_desc.lower()
    assert "citation" in high_desc.lower()

    medium_desc = get_confidence_description(ConfidenceLevel.MEDIUM)
    assert "moderate" in medium_desc.lower()

    low_desc = get_confidence_description(ConfidenceLevel.LOW)
    assert "limited" in low_desc.lower()

    none_desc = get_confidence_description(ConfidenceLevel.NONE)
    assert "no evidence" in none_desc.lower() or "unavailable" in none_desc.lower()


def test_confidence_edge_case_exactly_threshold():
    """
    Test edge case: Exactly at threshold boundary
    """
    # Exactly 3 citations with complete coverage = HIGH
    citations_3 = [MockCitation() for _ in range(3)]
    response_3 = MockAIResponse(
        text="3 citations",
        citations=citations_3,
        coverage="complete"
    )
    assert calculate_confidence_level(response_3) == ConfidenceLevel.HIGH

    # Exactly 1 citation = MEDIUM
    citations_1 = [MockCitation()]
    response_1 = MockAIResponse(
        text="1 citation",
        citations=citations_1,
        coverage="none"
    )
    assert calculate_confidence_level(response_1) == ConfidenceLevel.MEDIUM

    # 0 citations but has content = LOW
    response_0 = MockAIResponse(
        text="No citations",
        citations=[],
        coverage="none"
    )
    assert calculate_confidence_level(response_0) == ConfidenceLevel.LOW


def test_confidence_with_incomplete_coverage_but_many_citations():
    """
    Test: Many citations but incomplete coverage
    """
    # 5 citations but only partial coverage -> should be MEDIUM (not HIGH)
    citations = [MockCitation() for _ in range(5)]
    response = MockAIResponse(
        text="Many citations, partial coverage",
        citations=citations,
        coverage="partial"
    )

    confidence = calculate_confidence_level(response)
    # Requires both 3+ citations AND complete coverage for HIGH
    # With partial coverage, it's MEDIUM
    assert confidence == ConfidenceLevel.MEDIUM


def test_aggregate_confidence_exactly_half_high():
    """
    Test edge case: Exactly 50% HIGH (should not be aggregate HIGH)
    """
    responses = [
        # 2 HIGH
        MockAIResponse(
            text="High 1",
            citations=[MockCitation() for _ in range(3)],
            coverage="complete"
        ),
        MockAIResponse(
            text="High 2",
            citations=[MockCitation() for _ in range(3)],
            coverage="complete"
        ),
        # 2 MEDIUM
        MockAIResponse(
            text="Medium 1",
            citations=[MockCitation()],
            coverage="partial"
        ),
        MockAIResponse(
            text="Medium 2",
            citations=[MockCitation()],
            coverage="partial"
        ),
    ]

    aggregate = calculate_aggregate_confidence(responses)
    # 2/4 = 50%, which is NOT > 50%, so aggregate is MEDIUM
    assert aggregate == ConfidenceLevel.MEDIUM


def test_aggregate_confidence_just_over_half_high():
    """
    Test: Just over 50% HIGH should be aggregate HIGH
    """
    responses = [
        # 3 HIGH (60%)
        MockAIResponse(
            text="High 1",
            citations=[MockCitation() for _ in range(3)],
            coverage="complete"
        ),
        MockAIResponse(
            text="High 2",
            citations=[MockCitation() for _ in range(3)],
            coverage="complete"
        ),
        MockAIResponse(
            text="High 3",
            citations=[MockCitation() for _ in range(3)],
            coverage="complete"
        ),
        # 2 MEDIUM (40%)
        MockAIResponse(
            text="Medium 1",
            citations=[MockCitation()],
            coverage="partial"
        ),
        MockAIResponse(
            text="Medium 2",
            citations=[MockCitation()],
            coverage="partial"
        ),
    ]

    aggregate = calculate_aggregate_confidence(responses)
    # 3/5 = 60% > 50%, so aggregate is HIGH
    assert aggregate == ConfidenceLevel.HIGH
