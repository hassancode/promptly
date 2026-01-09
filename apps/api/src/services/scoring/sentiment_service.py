"""Sentiment classification service with Claude primary and Hugging Face fallback"""
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from core.logging import get_logger
from core.config import settings

logger = get_logger(__name__)


class Sentiment(str, Enum):
    """Sentiment classification"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


@dataclass
class SentimentResult:
    """Result of sentiment analysis"""
    entity_name: str
    overall: Sentiment
    positive_ratio: float
    neutral_ratio: float
    negative_ratio: float
    confidence: float
    by_provider: Dict[str, Sentiment]
    by_prompt: Dict[str, Sentiment]

    def to_dict(self) -> Dict:
        return {
            "entity_name": self.entity_name,
            "overall": self.overall.value,
            "positive": round(self.positive_ratio, 3),
            "neutral": round(self.neutral_ratio, 3),
            "negative": round(self.negative_ratio, 3),
            "confidence": round(self.confidence, 3),
        }


class SentimentService:
    """
    Service for sentiment classification of brand mentions.

    Uses Claude (Anthropic) as primary classifier with Hugging Face fallback.
    Both use the same rubric: Positive/Neutral/Negative.
    """

    # Sentiment keywords for rule-based fallback
    POSITIVE_KEYWORDS = [
        "excellent", "great", "amazing", "best", "leading", "innovative",
        "reliable", "trusted", "quality", "recommend", "love", "favorite",
        "superior", "outstanding", "impressive", "successful", "top-rated"
    ]

    NEGATIVE_KEYWORDS = [
        "poor", "bad", "worst", "disappointing", "unreliable", "avoid",
        "issues", "problems", "complaints", "expensive", "overpriced",
        "terrible", "awful", "failing", "decline", "controversy"
    ]

    def __init__(self):
        self._claude_available = bool(settings.ANTHROPIC_API_KEY)
        self._huggingface_available = bool(settings.HUGGINGFACE_API_KEY)

    async def classify_with_claude(
        self,
        text: str,
        entity_name: str
    ) -> Tuple[Sentiment, float]:
        """
        Classify sentiment using Claude API.

        Args:
            text: Text to analyze
            entity_name: Entity to focus sentiment on

        Returns:
            Tuple of (Sentiment, confidence)
        """
        if not self._claude_available:
            raise RuntimeError("Claude API not available")

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

            prompt = f"""Analyze the sentiment toward "{entity_name}" in the following text.

Text: {text[:2000]}  # Limit text length

Classify the sentiment as exactly one of: POSITIVE, NEUTRAL, or NEGATIVE.
Also provide a confidence score from 0.0 to 1.0.

Respond in this exact format:
SENTIMENT: <POSITIVE|NEUTRAL|NEGATIVE>
CONFIDENCE: <0.0-1.0>"""

            response = client.messages.create(
                model="claude-3-haiku-20240307",  # Use fast model for classification
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text.strip()

            # Parse response
            sentiment = Sentiment.NEUTRAL
            confidence = 0.7

            if "POSITIVE" in result_text.upper():
                sentiment = Sentiment.POSITIVE
            elif "NEGATIVE" in result_text.upper():
                sentiment = Sentiment.NEGATIVE

            # Extract confidence
            conf_match = re.search(r'CONFIDENCE:\s*([\d.]+)', result_text)
            if conf_match:
                confidence = float(conf_match.group(1))

            return sentiment, confidence

        except Exception as e:
            logger.warning(f"Claude sentiment classification failed: {e}")
            raise

    async def classify_with_huggingface(
        self,
        text: str,
        entity_name: str
    ) -> Tuple[Sentiment, float]:
        """
        Classify sentiment using Hugging Face API (fallback).

        Args:
            text: Text to analyze
            entity_name: Entity to focus sentiment on

        Returns:
            Tuple of (Sentiment, confidence)
        """
        if not self._huggingface_available:
            raise RuntimeError("Hugging Face API not available")

        try:
            import httpx

            # Use a sentiment analysis model
            api_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_url,
                    headers={"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"},
                    json={"inputs": text[:512]},  # Model limit
                    timeout=30.0
                )

                if response.status_code != 200:
                    raise RuntimeError(f"HuggingFace API error: {response.status_code}")

                results = response.json()

                # Parse results (format: [[{"label": "positive", "score": 0.9}, ...]])
                if results and isinstance(results[0], list):
                    results = results[0]

                best_label = max(results, key=lambda x: x["score"])
                label = best_label["label"].lower()
                confidence = best_label["score"]

                if "positive" in label:
                    sentiment = Sentiment.POSITIVE
                elif "negative" in label:
                    sentiment = Sentiment.NEGATIVE
                else:
                    sentiment = Sentiment.NEUTRAL

                return sentiment, confidence

        except Exception as e:
            logger.warning(f"Hugging Face sentiment classification failed: {e}")
            raise

    def classify_with_rules(
        self,
        text: str,
        entity_name: str
    ) -> Tuple[Sentiment, float]:
        """
        Rule-based sentiment classification (ultimate fallback).

        Args:
            text: Text to analyze
            entity_name: Entity to focus sentiment on

        Returns:
            Tuple of (Sentiment, confidence)
        """
        text_lower = text.lower()

        # Find context around entity mentions
        entity_lower = entity_name.lower()
        context_window = 100  # characters around mention

        # Extract contexts around mentions
        contexts = []
        start = 0
        while True:
            pos = text_lower.find(entity_lower, start)
            if pos == -1:
                break
            context_start = max(0, pos - context_window)
            context_end = min(len(text), pos + len(entity_name) + context_window)
            contexts.append(text_lower[context_start:context_end])
            start = pos + 1

        if not contexts:
            contexts = [text_lower]  # Use full text if no mentions

        # Count sentiment keywords in contexts
        positive_count = 0
        negative_count = 0

        for context in contexts:
            for keyword in self.POSITIVE_KEYWORDS:
                if keyword in context:
                    positive_count += 1
            for keyword in self.NEGATIVE_KEYWORDS:
                if keyword in context:
                    negative_count += 1

        # Determine sentiment
        total = positive_count + negative_count
        if total == 0:
            return Sentiment.NEUTRAL, 0.5

        if positive_count > negative_count * 1.5:
            sentiment = Sentiment.POSITIVE
            confidence = min(0.8, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count * 1.5:
            sentiment = Sentiment.NEGATIVE
            confidence = min(0.8, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = Sentiment.NEUTRAL
            confidence = 0.6

        return sentiment, confidence

    async def classify_sentiment(
        self,
        text: str,
        entity_name: str
    ) -> Tuple[Sentiment, float]:
        """
        Classify sentiment with fallback chain: Claude -> HuggingFace -> Rules.

        Args:
            text: Text to analyze
            entity_name: Entity to focus sentiment on

        Returns:
            Tuple of (Sentiment, confidence)
        """
        # Try Claude first
        if self._claude_available:
            try:
                return await self.classify_with_claude(text, entity_name)
            except Exception as e:
                logger.warning(f"Claude classification failed, trying fallback: {e}")

        # Try Hugging Face
        if self._huggingface_available:
            try:
                return await self.classify_with_huggingface(text, entity_name)
            except Exception as e:
                logger.warning(f"Hugging Face classification failed, using rules: {e}")

        # Fall back to rule-based
        return self.classify_with_rules(text, entity_name)

    async def analyze_sentiment(
        self,
        entity_name: str,
        responses: List[Dict],
    ) -> SentimentResult:
        """
        Perform comprehensive sentiment analysis across responses.

        Args:
            entity_name: Brand or competitor name
            responses: List of response dicts with text, provider, prompt_id

        Returns:
            SentimentResult with aggregated sentiment data
        """
        sentiments: List[Sentiment] = []
        confidences: List[float] = []
        by_provider: Dict[str, Sentiment] = {}
        by_prompt: Dict[str, Sentiment] = {}

        for response in responses:
            text = response.get("text", "")
            provider = response.get("provider", "unknown")
            prompt_id = response.get("prompt_id", "unknown")

            if not text:
                continue

            sentiment, confidence = await self.classify_sentiment(text, entity_name)
            sentiments.append(sentiment)
            confidences.append(confidence)
            by_provider[provider] = sentiment
            by_prompt[prompt_id] = sentiment

        # Calculate ratios
        total = len(sentiments) if sentiments else 1
        positive_ratio = sum(1 for s in sentiments if s == Sentiment.POSITIVE) / total
        neutral_ratio = sum(1 for s in sentiments if s == Sentiment.NEUTRAL) / total
        negative_ratio = sum(1 for s in sentiments if s == Sentiment.NEGATIVE) / total

        # Determine overall sentiment (majority, with neutral as tiebreaker)
        if positive_ratio > neutral_ratio and positive_ratio > negative_ratio:
            overall = Sentiment.POSITIVE
        elif negative_ratio > neutral_ratio and negative_ratio > positive_ratio:
            overall = Sentiment.NEGATIVE
        else:
            overall = Sentiment.NEUTRAL

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        result = SentimentResult(
            entity_name=entity_name,
            overall=overall,
            positive_ratio=positive_ratio,
            neutral_ratio=neutral_ratio,
            negative_ratio=negative_ratio,
            confidence=avg_confidence,
            by_provider=by_provider,
            by_prompt=by_prompt,
        )

        logger.info(
            "Sentiment analysis complete",
            extra={
                "entity": entity_name,
                "overall": overall.value,
                "confidence": round(avg_confidence, 3),
            }
        )

        return result
