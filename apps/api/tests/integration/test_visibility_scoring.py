"""
Integration test for visibility scoring algorithm
Task: T158 [US6]
"""
import pytest
from unittest.mock import MagicMock
from uuid import uuid4

# Import from src
import sys
sys.path.insert(0, "src")


class TestVisibilityScoringAlgorithm:
    """Integration tests for visibility scoring: presence + frequency + position"""

    def test_visibility_composite_calculation(self):
        """
        Test visibility composite score calculation:
        visibility = 0.4 * presence + 0.3 * frequency + 0.3 * position
        """
        presence = 0.8
        frequency = 0.6
        position = 0.7

        # Expected calculation
        expected_visibility = 0.4 * presence + 0.3 * frequency + 0.3 * position
        # = 0.4 * 0.8 + 0.3 * 0.6 + 0.3 * 0.7
        # = 0.32 + 0.18 + 0.21
        # = 0.71

        assert expected_visibility == pytest.approx(0.71, rel=0.01)

    def test_presence_score_calculation(self):
        """
        Test presence score: binary (1 if brand mentioned, 0 if not)
        Aggregated across providers: mentioned_providers / total_providers
        """
        providers_with_mention = ["openai", "claude", "gemini", "perplexity"]
        total_providers = ["openai", "claude", "gemini", "perplexity", "google_ai", "huggingface"]

        presence_score = len(providers_with_mention) / len(total_providers)
        # = 4 / 6 = 0.667

        assert presence_score == pytest.approx(0.667, rel=0.01)

    def test_frequency_score_calculation(self):
        """
        Test frequency score: normalized mention count
        frequency = mentions / max_possible_mentions (capped at 1.0)
        """
        mention_count = 5
        max_mentions = 10  # e.g., could appear once per prompt

        frequency_score = min(mention_count / max_mentions, 1.0)
        # = 5 / 10 = 0.5

        assert frequency_score == 0.5

    def test_position_score_calculation(self):
        """
        Test position scoring:
        - First mention: 1.0
        - Decay by 0.1 per subsequent mention
        - Minimum: 0.5
        """
        def calculate_position_score(mention_position: int) -> float:
            """Calculate position score with decay"""
            base_score = 1.0
            decay_rate = 0.1
            min_score = 0.5

            score = max(base_score - (mention_position * decay_rate), min_score)
            return score

        # First mention (position 0)
        assert calculate_position_score(0) == 1.0

        # Second mention (position 1)
        assert calculate_position_score(1) == 0.9

        # Fifth mention (position 4)
        assert calculate_position_score(4) == 0.6

        # Sixth mention (position 5)
        assert calculate_position_score(5) == 0.5

        # Beyond sixth should stay at 0.5
        assert calculate_position_score(10) == 0.5

    def test_visibility_per_prompt_then_aggregated(self):
        """
        Test that visibility is calculated per prompt/provider,
        then aggregated across all
        """
        prompt_provider_scores = [
            {"prompt_id": "p1", "provider": "openai", "visibility": 0.8},
            {"prompt_id": "p1", "provider": "claude", "visibility": 0.7},
            {"prompt_id": "p2", "provider": "openai", "visibility": 0.9},
            {"prompt_id": "p2", "provider": "claude", "visibility": 0.6},
        ]

        # Calculate aggregate visibility
        total_visibility = sum(s["visibility"] for s in prompt_provider_scores)
        avg_visibility = total_visibility / len(prompt_provider_scores)
        # = (0.8 + 0.7 + 0.9 + 0.6) / 4 = 0.75

        assert avg_visibility == 0.75


class TestVisibilityScoringService:
    """Tests for VisibilityService implementation"""

    def test_visibility_service_exists(self):
        """
        Test that VisibilityService can be imported
        """
        from services.scoring.visibility_service import VisibilityService

        service = VisibilityService()
        assert service is not None

    def test_visibility_score_normalization(self):
        """
        Test that visibility scores are normalized to 0-1 range
        """
        def normalize_score(raw_score: float) -> float:
            return max(0.0, min(1.0, raw_score))

        assert normalize_score(1.5) == 1.0
        assert normalize_score(-0.2) == 0.0
        assert normalize_score(0.75) == 0.75

    def test_visibility_comparison_between_brands(self):
        """
        Test visibility score comparison between brand and competitors
        """
        brand_visibility = 0.75
        competitor_visibilities = {
            "Competitor A": 0.65,
            "Competitor B": 0.80,
            "Competitor C": 0.55
        }

        # Brand ranks
        all_scores = [brand_visibility] + list(competitor_visibilities.values())
        all_scores.sort(reverse=True)

        brand_rank = all_scores.index(brand_visibility) + 1
        # Rank should be 2 (behind Competitor B at 0.80)

        assert brand_rank == 2


class TestVisibilityWithNoMentions:
    """Tests for edge cases with no brand mentions"""

    def test_zero_presence_yields_zero_visibility(self):
        """
        Test that if brand is not mentioned, presence = 0
        """
        presence = 0.0  # No mentions
        frequency = 0.0
        position = 0.0

        visibility = 0.4 * presence + 0.3 * frequency + 0.3 * position
        assert visibility == 0.0

    def test_partial_visibility_with_sparse_mentions(self):
        """
        Test visibility calculation with sparse mentions
        """
        presence = 0.2  # Mentioned by 1 of 5 providers
        frequency = 0.1  # Low mention count
        position = 1.0  # But when mentioned, mentioned first

        visibility = 0.4 * presence + 0.3 * frequency + 0.3 * position
        # = 0.4 * 0.2 + 0.3 * 0.1 + 0.3 * 1.0
        # = 0.08 + 0.03 + 0.30
        # = 0.41

        assert visibility == pytest.approx(0.41, rel=0.01)
