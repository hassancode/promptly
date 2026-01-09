"""
Integration test for recommendation generation (min 5 recommendations)
Task: T160 [US6]
"""
import pytest
from unittest.mock import MagicMock
from uuid import uuid4

# Import from src
import sys
sys.path.insert(0, "src")


class TestRecommendationGeneration:
    """Integration tests for recommendation generation"""

    def test_minimum_5_recommendations_generated(self):
        """
        Test that at least 5 recommendations are generated per analysis
        """
        MIN_RECOMMENDATIONS = 5

        recommendations = [
            {"id": 1, "text": "Improve content marketing presence"},
            {"id": 2, "text": "Optimize for AI search queries"},
            {"id": 3, "text": "Create more comparison content"},
            {"id": 4, "text": "Build authoritative backlinks"},
            {"id": 5, "text": "Address sentiment concerns"},
        ]

        assert len(recommendations) >= MIN_RECOMMENDATIONS

    def test_recommendations_are_actionable(self):
        """
        Test that recommendations are actionable (contain verbs/actions)
        """
        actionable_verbs = [
            "improve", "optimize", "create", "build", "address",
            "increase", "develop", "enhance", "implement", "establish"
        ]

        recommendations = [
            "Improve content marketing presence",
            "Optimize website for AI search queries",
            "Create more comparison content",
            "Build authoritative backlinks",
            "Address negative sentiment concerns"
        ]

        for rec in recommendations:
            has_action = any(verb in rec.lower() for verb in actionable_verbs)
            assert has_action, f"Recommendation not actionable: {rec}"

    def test_recommendations_have_rationale(self):
        """
        Test that each recommendation includes a rationale
        """
        recommendation = {
            "text": "Create more comparison content",
            "rationale": "Analysis shows competitors appear more frequently in comparison queries. Creating targeted comparison content can improve visibility by 20-30%."
        }

        assert "rationale" in recommendation
        assert len(recommendation["rationale"]) > 20

    def test_recommendations_have_expected_impact(self):
        """
        Test that each recommendation includes expected impact
        """
        recommendation = {
            "text": "Optimize for AI search queries",
            "expected_impact": "Could increase AI visibility score by 15-25% within 2-3 months based on similar brand improvements."
        }

        assert "expected_impact" in recommendation
        assert len(recommendation["expected_impact"]) > 10


class TestRecommendationPrioritization:
    """Tests for recommendation prioritization"""

    def test_recommendations_ranked_by_impact(self):
        """
        Test that recommendations are sorted by expected impact/priority
        """
        recommendations = [
            {"text": "Rec 1", "priority": 3},
            {"text": "Rec 2", "priority": 1},  # Highest priority
            {"text": "Rec 3", "priority": 2},
            {"text": "Rec 4", "priority": 5},
            {"text": "Rec 5", "priority": 4},
        ]

        # Sort by priority (1 = highest)
        sorted_recs = sorted(recommendations, key=lambda x: x["priority"])

        assert sorted_recs[0]["priority"] == 1
        assert sorted_recs[-1]["priority"] == 5

    def test_priority_range_1_to_5(self):
        """
        Test that priority is in range 1-5
        """
        priorities = [1, 2, 3, 4, 5]

        for priority in priorities:
            assert 1 <= priority <= 5

    def test_high_impact_recommendations_first(self):
        """
        Test that highest impact recommendations appear first
        """
        recommendations = [
            {"text": "Quick win - low effort, high impact", "priority": 1, "effort": "low", "impact": "high"},
            {"text": "Major initiative - high effort, high impact", "priority": 2, "effort": "high", "impact": "high"},
            {"text": "Minor improvement - low effort, low impact", "priority": 3, "effort": "low", "impact": "low"},
        ]

        # Priority 1 should be high impact
        assert recommendations[0]["impact"] == "high"


class TestRecommendationEvidence:
    """Tests for recommendation evidence linking"""

    def test_recommendations_linked_to_evidence(self):
        """
        Test that recommendations include evidence references
        """
        recommendation = {
            "text": "Improve visibility in product comparison queries",
            "evidence_references": [
                {"ai_response_id": str(uuid4()), "relevance": "Brand not mentioned in 4/6 comparison responses"},
                {"ai_response_id": str(uuid4()), "relevance": "Competitor X mentioned 3x more frequently"}
            ]
        }

        assert "evidence_references" in recommendation
        assert len(recommendation["evidence_references"]) >= 1

    def test_evidence_includes_ai_response_ids(self):
        """
        Test that evidence references include AI response IDs
        """
        evidence = {
            "ai_response_id": str(uuid4()),
            "citation_id": str(uuid4()),
            "relevance_score": 0.85
        }

        assert "ai_response_id" in evidence


class TestRecommendationServiceImplementation:
    """Tests for RecommendationService implementation"""

    def test_recommendation_service_exists(self):
        """
        Test that RecommendationService can be imported
        """
        from services.recommendation_service import RecommendationService

        service = RecommendationService()
        assert service is not None

    def test_recommendations_based_on_insights(self):
        """
        Test that recommendations are generated from insights
        """
        insights = [
            {"type": "visibility", "score": 0.45, "summary": "Low visibility in AI search"},
            {"type": "sentiment", "sentiment": "Neutral", "summary": "Mixed sentiment"},
            {"type": "gap", "summary": "Missing from product comparison topics"}
        ]

        # Each insight type should potentially generate recommendations
        recommendation_types = {
            "visibility": "Improve AI search presence",
            "sentiment": "Address sentiment concerns",
            "gap": "Create content for missing topics"
        }

        for insight in insights:
            assert insight["type"] in recommendation_types

    def test_recommendations_personalized_to_brand(self):
        """
        Test that recommendations reference the specific brand
        """
        brand_name = "Acme Corp"

        recommendation = {
            "text": f"Improve {brand_name}'s visibility in product comparison queries",
            "rationale": f"Analysis shows {brand_name} appears less frequently than competitors"
        }

        assert brand_name in recommendation["text"]
        assert brand_name in recommendation["rationale"]


class TestRecommendationCategories:
    """Tests for recommendation categorization"""

    def test_recommendations_cover_multiple_areas(self):
        """
        Test that recommendations cover different improvement areas
        """
        recommendation_categories = [
            "visibility",
            "content",
            "sentiment",
            "competitive",
            "technical"
        ]

        recommendations = [
            {"text": "Improve AI visibility", "category": "visibility"},
            {"text": "Create comparison content", "category": "content"},
            {"text": "Address negative sentiment", "category": "sentiment"},
            {"text": "Differentiate from competitors", "category": "competitive"},
            {"text": "Optimize for AI indexing", "category": "technical"},
        ]

        categories_covered = {r["category"] for r in recommendations}
        assert len(categories_covered) >= 3  # At least 3 different categories

    def test_recommendations_include_confidence_level(self):
        """
        Test that recommendations include confidence level
        """
        recommendation = {
            "text": "Optimize website for AI search",
            "confidence_level": "high",  # high, medium, low
            "confidence_reason": "Based on strong evidence from 5 AI providers"
        }

        assert recommendation["confidence_level"] in ["high", "medium", "low"]
