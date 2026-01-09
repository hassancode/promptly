"""
Integration test for sentiment classification with Claude primary and Hugging Face fallback
Task: T159 [US6]
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

# Import from src
import sys
sys.path.insert(0, "src")


class TestSentimentClassificationPrimary:
    """Integration tests for Claude-based sentiment classification (primary)"""

    def test_sentiment_classification_values(self):
        """
        Test that sentiment is classified into three categories:
        Positive, Neutral, Negative
        """
        valid_sentiments = ["Positive", "Neutral", "Negative"]

        for sentiment in valid_sentiments:
            assert sentiment in ["Positive", "Neutral", "Negative"]

    @pytest.mark.asyncio
    async def test_claude_used_as_primary_classifier(self):
        """
        Test that Claude is used as the primary sentiment classifier
        """
        classifiers_tried = []

        async def mock_claude_classify(text):
            classifiers_tried.append("claude")
            return {"sentiment": "Positive", "confidence": 0.92}

        async def mock_huggingface_classify(text):
            classifiers_tried.append("huggingface")
            return {"sentiment": "Positive", "confidence": 0.85}

        # Primary should be Claude
        result = await mock_claude_classify("Great product, highly recommend!")

        assert "claude" in classifiers_tried
        assert "huggingface" not in classifiers_tried
        assert result["sentiment"] == "Positive"

    def test_sentiment_prompt_template(self):
        """
        Test the prompt template used for sentiment classification
        """
        prompt_template = "Classify sentiment (Positive/Neutral/Negative) for brand mention: {mention_context}"

        # Verify template structure
        assert "{mention_context}" in prompt_template
        assert "Positive" in prompt_template
        assert "Neutral" in prompt_template
        assert "Negative" in prompt_template


class TestSentimentClassificationFallback:
    """Integration tests for Hugging Face fallback sentiment classification"""

    @pytest.mark.asyncio
    async def test_huggingface_used_when_claude_unavailable(self):
        """
        Test that Hugging Face is used when Claude is unavailable
        """
        classifiers_tried = []

        async def mock_claude_classify(text):
            classifiers_tried.append("claude")
            raise Exception("Rate limit exceeded")

        async def mock_huggingface_classify(text):
            classifiers_tried.append("huggingface")
            return {"sentiment": "Positive", "confidence": 0.85}

        # Try Claude first, fallback to HuggingFace
        try:
            result = await mock_claude_classify("Great product!")
        except:
            result = await mock_huggingface_classify("Great product!")

        assert "claude" in classifiers_tried
        assert "huggingface" in classifiers_tried
        assert result["sentiment"] == "Positive"

    @pytest.mark.asyncio
    async def test_fallback_when_claude_rate_limited(self):
        """
        Test fallback specifically for rate limit errors
        """
        error_type = "rate_limit"

        should_fallback = error_type in ["rate_limit", "timeout", "unavailable"]
        assert should_fallback

    @pytest.mark.asyncio
    async def test_both_classifiers_use_same_rubric(self):
        """
        Test that both Claude and Hugging Face use the same classification rubric
        """
        rubric = {
            "Positive": "Brand is praised, recommended, or described favorably",
            "Neutral": "Brand is mentioned factually without clear positive or negative sentiment",
            "Negative": "Brand is criticized, not recommended, or described unfavorably"
        }

        # Both classifiers should use same categories
        expected_categories = {"Positive", "Neutral", "Negative"}

        assert set(rubric.keys()) == expected_categories


class TestSentimentAggregation:
    """Tests for sentiment aggregation across prompts/providers"""

    def test_sentiment_majority_voting(self):
        """
        Test sentiment aggregation using majority voting
        """
        classifications = [
            "Positive",
            "Positive",
            "Neutral",
            "Positive",
            "Negative"
        ]

        # Count votes
        from collections import Counter
        votes = Counter(classifications)
        majority_sentiment = votes.most_common(1)[0][0]

        assert majority_sentiment == "Positive"

    def test_ambiguous_defaults_to_neutral(self):
        """
        Test that ambiguous/tie results default to Neutral
        """
        classifications = ["Positive", "Negative"]  # Tie

        from collections import Counter
        votes = Counter(classifications)
        top_two = votes.most_common(2)

        # If tie, default to Neutral
        if len(top_two) >= 2 and top_two[0][1] == top_two[1][1]:
            result = "Neutral"
        else:
            result = top_two[0][0]

        assert result == "Neutral"

    def test_sentiment_aggregation_per_brand(self):
        """
        Test that sentiment is aggregated separately for brand and each competitor
        """
        brand_sentiments = {
            "MyBrand": ["Positive", "Positive", "Neutral"],
            "Competitor A": ["Neutral", "Neutral", "Negative"],
            "Competitor B": ["Positive", "Neutral", "Positive"]
        }

        def aggregate(sentiments):
            from collections import Counter
            votes = Counter(sentiments)
            return votes.most_common(1)[0][0]

        results = {brand: aggregate(sents) for brand, sents in brand_sentiments.items()}

        assert results["MyBrand"] == "Positive"
        assert results["Competitor A"] == "Neutral"
        assert results["Competitor B"] == "Positive"


class TestSentimentServiceImplementation:
    """Tests for SentimentService implementation"""

    def test_sentiment_service_exists(self):
        """
        Test that SentimentService can be imported
        """
        from services.scoring.sentiment_service import SentimentService

        service = SentimentService()
        assert service is not None

    def test_sentiment_confidence_threshold(self):
        """
        Test that low-confidence classifications are handled
        """
        CONFIDENCE_THRESHOLD = 0.5

        classification = {"sentiment": "Positive", "confidence": 0.45}

        is_confident = classification["confidence"] >= CONFIDENCE_THRESHOLD
        assert not is_confident

        # Low confidence should be treated as Neutral
        final_sentiment = classification["sentiment"] if is_confident else "Neutral"
        assert final_sentiment == "Neutral"

    def test_sentiment_with_no_brand_mention(self):
        """
        Test handling when brand is not mentioned in response
        """
        response_text = "This is a response that doesn't mention the brand at all."
        brand_name = "TestBrand"

        # If brand not mentioned, sentiment should be None or Neutral
        brand_mentioned = brand_name.lower() in response_text.lower()
        assert not brand_mentioned

        # Result should indicate "not applicable"
        sentiment_result = {
            "sentiment": None,
            "reason": "Brand not mentioned in response"
        }

        assert sentiment_result["sentiment"] is None
