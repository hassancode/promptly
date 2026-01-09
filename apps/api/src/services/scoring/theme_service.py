"""Theme identification service"""
import re
from typing import List, Dict, Set
from dataclasses import dataclass
from collections import Counter

from core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Theme:
    """Identified theme"""
    name: str
    frequency: int
    related_terms: List[str]
    sample_contexts: List[str]
    relevance_score: float  # 0-1 relevance to the entity

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "frequency": self.frequency,
            "related_terms": self.related_terms,
            "sample_contexts": self.sample_contexts[:3],  # Limit contexts
            "relevance_score": round(self.relevance_score, 3),
        }


@dataclass
class ThemeResult:
    """Result of theme identification"""
    entity_name: str
    themes: List[Theme]
    top_themes: List[str]

    def to_dict(self) -> Dict:
        return {
            "entity_name": self.entity_name,
            "themes": [t.to_dict() for t in self.themes],
            "top_themes": self.top_themes,
        }


class ThemeService:
    """
    Service for identifying key themes in AI responses.

    Extracts recurring topics and themes associated with brands
    and competitors from AI response text.
    """

    # Common stopwords to filter out
    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "this",
        "that", "these", "those", "it", "its", "they", "their", "them",
        "we", "our", "us", "you", "your", "he", "she", "him", "her", "his",
        "i", "my", "me", "not", "no", "yes", "so", "if", "then", "than",
        "more", "most", "less", "least", "very", "just", "only", "also",
        "about", "into", "over", "after", "before", "between", "under",
        "again", "further", "once", "here", "there", "when", "where", "why",
        "how", "all", "each", "every", "both", "few", "more", "most", "other",
        "some", "such", "any", "own", "same", "which", "who", "whom",
    }

    # Business/industry theme categories
    THEME_CATEGORIES = {
        "innovation": ["innovation", "innovative", "technology", "tech", "ai", "digital", "future"],
        "quality": ["quality", "reliable", "durable", "premium", "excellence", "superior"],
        "price": ["price", "cost", "affordable", "expensive", "value", "budget", "cheap"],
        "service": ["service", "support", "customer", "help", "assistance", "care"],
        "sustainability": ["sustainable", "green", "eco", "environment", "carbon", "renewable"],
        "design": ["design", "aesthetic", "style", "look", "appearance", "elegant"],
        "performance": ["performance", "fast", "speed", "powerful", "efficient", "capability"],
        "trust": ["trust", "trusted", "reputation", "credibility", "reliable", "honest"],
        "market": ["market", "share", "leader", "competitor", "industry", "sector"],
        "growth": ["growth", "growing", "expansion", "expanding", "scale", "scaling"],
    }

    def __init__(self):
        self._theme_patterns = self._compile_theme_patterns()

    def _compile_theme_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for theme categories"""
        patterns = {}
        for category, terms in self.THEME_CATEGORIES.items():
            pattern = r'\b(' + '|'.join(re.escape(t) for t in terms) + r')\b'
            patterns[category] = re.compile(pattern, re.IGNORECASE)
        return patterns

    def extract_keywords(
        self,
        text: str,
        min_word_length: int = 4,
        max_keywords: int = 50
    ) -> List[str]:
        """
        Extract significant keywords from text.

        Args:
            text: Text to analyze
            min_word_length: Minimum word length to consider
            max_keywords: Maximum keywords to return

        Returns:
            List of keywords sorted by frequency
        """
        # Tokenize and clean
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

        # Filter
        filtered = [
            w for w in words
            if len(w) >= min_word_length and w not in self.STOPWORDS
        ]

        # Count frequencies
        word_counts = Counter(filtered)

        # Return top keywords
        return [word for word, _ in word_counts.most_common(max_keywords)]

    def identify_category_themes(
        self,
        text: str,
        entity_name: str
    ) -> Dict[str, int]:
        """
        Identify predefined theme categories in text.

        Args:
            text: Text to analyze
            entity_name: Entity to focus on

        Returns:
            Dict mapping theme category to occurrence count
        """
        results = {}
        for category, pattern in self._theme_patterns.items():
            matches = pattern.findall(text)
            if matches:
                results[category] = len(matches)
        return results

    def extract_context_around_entity(
        self,
        text: str,
        entity_name: str,
        window: int = 200
    ) -> List[str]:
        """
        Extract text contexts around entity mentions.

        Args:
            text: Full text
            entity_name: Entity to find
            window: Characters before and after mention

        Returns:
            List of context strings
        """
        contexts = []
        text_lower = text.lower()
        entity_lower = entity_name.lower()

        start = 0
        while True:
            pos = text_lower.find(entity_lower, start)
            if pos == -1:
                break

            context_start = max(0, pos - window)
            context_end = min(len(text), pos + len(entity_name) + window)
            contexts.append(text[context_start:context_end])
            start = pos + 1

        return contexts

    def identify_themes(
        self,
        entity_name: str,
        responses: List[Dict],
        max_themes: int = 10
    ) -> ThemeResult:
        """
        Identify key themes associated with an entity.

        Args:
            entity_name: Brand or competitor name
            responses: List of response dicts with text
            max_themes: Maximum themes to return

        Returns:
            ThemeResult with identified themes
        """
        # Combine all response texts
        all_text = " ".join(r.get("text", "") for r in responses)

        # Get contexts around entity mentions
        contexts = self.extract_context_around_entity(all_text, entity_name)
        context_text = " ".join(contexts) if contexts else all_text

        # Identify category themes
        category_counts = self.identify_category_themes(context_text, entity_name)

        # Extract additional keywords
        keywords = self.extract_keywords(context_text)

        # Build theme list
        themes = []

        # Add category themes
        for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            related = self.THEME_CATEGORIES.get(category, [])
            theme = Theme(
                name=category,
                frequency=count,
                related_terms=related,
                sample_contexts=contexts[:2],
                relevance_score=min(1.0, count / 10),  # Normalize
            )
            themes.append(theme)

        # Add keyword-based themes (that aren't already categories)
        existing_names = {t.name for t in themes}
        for keyword in keywords[:20]:
            if keyword not in existing_names:
                count = context_text.lower().count(keyword)
                if count >= 2:  # Only include if mentioned multiple times
                    theme = Theme(
                        name=keyword,
                        frequency=count,
                        related_terms=[],
                        sample_contexts=contexts[:1],
                        relevance_score=min(1.0, count / 15),
                    )
                    themes.append(theme)

        # Sort by relevance and limit
        themes.sort(key=lambda t: t.relevance_score, reverse=True)
        themes = themes[:max_themes]

        top_themes = [t.name for t in themes[:5]]

        result = ThemeResult(
            entity_name=entity_name,
            themes=themes,
            top_themes=top_themes,
        )

        logger.info(
            "Theme identification complete",
            extra={
                "entity": entity_name,
                "theme_count": len(themes),
                "top_themes": top_themes,
            }
        )

        return result

    def compare_themes(
        self,
        brand_name: str,
        competitor_names: List[str],
        responses: List[Dict],
    ) -> Dict[str, ThemeResult]:
        """
        Compare themes across brand and competitors.

        Args:
            brand_name: Main brand
            competitor_names: Competitors to compare
            responses: Response dicts

        Returns:
            Dict mapping entity names to ThemeResult
        """
        results = {}

        results[brand_name] = self.identify_themes(brand_name, responses)
        for competitor in competitor_names:
            results[competitor] = self.identify_themes(competitor, responses)

        return results
