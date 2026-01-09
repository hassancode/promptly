"""Gap identification service"""
from typing import List, Dict, Set
from dataclasses import dataclass

from core.logging import get_logger
from .theme_service import ThemeService, ThemeResult

logger = get_logger(__name__)


@dataclass
class Gap:
    """Identified content/coverage gap"""
    name: str
    description: str
    competitor_coverage: Dict[str, bool]  # Which competitors cover this topic
    importance: str  # high, medium, low
    recommendation: str

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "competitor_coverage": self.competitor_coverage,
            "importance": self.importance,
            "recommendation": self.recommendation,
        }


@dataclass
class GapResult:
    """Result of gap analysis"""
    brand_name: str
    gaps: List[Gap]
    total_gaps: int
    high_priority_gaps: int

    def to_dict(self) -> Dict:
        return {
            "brand_name": self.brand_name,
            "gaps": [g.to_dict() for g in self.gaps],
            "total_gaps": self.total_gaps,
            "high_priority_gaps": self.high_priority_gaps,
        }


class GapService:
    """
    Service for identifying content and coverage gaps.

    Compares themes and topics covered by competitors but missing
    from the brand's coverage to identify opportunities.
    """

    # Topics that are generally important for brand visibility
    IMPORTANT_TOPICS = {
        "innovation": "high",
        "sustainability": "high",
        "quality": "high",
        "service": "medium",
        "price": "medium",
        "performance": "medium",
        "trust": "high",
        "design": "low",
        "market": "medium",
        "growth": "medium",
    }

    def __init__(self):
        self.theme_service = ThemeService()

    def identify_gaps(
        self,
        brand_themes: ThemeResult,
        competitor_themes: Dict[str, ThemeResult],
    ) -> GapResult:
        """
        Identify gaps in brand coverage vs competitors.

        Args:
            brand_themes: Themes identified for the brand
            competitor_themes: Dict of competitor name to their ThemeResult

        Returns:
            GapResult with identified gaps
        """
        brand_theme_names = {t.name for t in brand_themes.themes}
        gaps = []

        # Collect all competitor themes
        all_competitor_themes: Dict[str, Set[str]] = {}
        for comp_name, comp_result in competitor_themes.items():
            all_competitor_themes[comp_name] = {t.name for t in comp_result.themes}

        # Find themes covered by competitors but not by brand
        competitor_only_themes: Set[str] = set()
        for themes in all_competitor_themes.values():
            competitor_only_themes.update(themes)
        competitor_only_themes -= brand_theme_names

        # Create gap entries for missing themes
        for theme_name in competitor_only_themes:
            # Check which competitors cover this theme
            coverage = {
                comp: theme_name in themes
                for comp, themes in all_competitor_themes.items()
            }
            coverage[brand_themes.entity_name] = False

            # Determine importance
            importance = self.IMPORTANT_TOPICS.get(theme_name, "low")

            # Count how many competitors cover it
            competitor_count = sum(1 for v in coverage.values() if v)

            # Generate recommendation
            if competitor_count >= len(competitor_themes) / 2:
                recommendation = f"Consider developing content around '{theme_name}' - most competitors are addressing this topic."
            else:
                recommendation = f"'{theme_name}' is covered by some competitors - evaluate if this aligns with your brand strategy."

            gap = Gap(
                name=theme_name,
                description=f"Topic '{theme_name}' is covered by competitors but not prominently associated with your brand.",
                competitor_coverage=coverage,
                importance=importance,
                recommendation=recommendation,
            )
            gaps.append(gap)

        # Also check important topics that no one covers well
        for topic, importance in self.IMPORTANT_TOPICS.items():
            if topic not in brand_theme_names:
                # Check if any competitor covers it well
                any_competitor_covers = any(
                    topic in themes
                    for themes in all_competitor_themes.values()
                )

                if not any_competitor_covers and importance == "high":
                    # Opportunity gap - important topic no one covers
                    coverage = {comp: False for comp in all_competitor_themes.keys()}
                    coverage[brand_themes.entity_name] = False

                    gap = Gap(
                        name=f"{topic}_opportunity",
                        description=f"High-importance topic '{topic}' is not well-covered by any brand in this space.",
                        competitor_coverage=coverage,
                        importance="high",
                        recommendation=f"First-mover opportunity: establish thought leadership in '{topic}'.",
                    )
                    gaps.append(gap)

        # Sort by importance
        importance_order = {"high": 0, "medium": 1, "low": 2}
        gaps.sort(key=lambda g: importance_order.get(g.importance, 3))

        high_priority = sum(1 for g in gaps if g.importance == "high")

        result = GapResult(
            brand_name=brand_themes.entity_name,
            gaps=gaps,
            total_gaps=len(gaps),
            high_priority_gaps=high_priority,
        )

        logger.info(
            "Gap analysis complete",
            extra={
                "brand": brand_themes.entity_name,
                "total_gaps": len(gaps),
                "high_priority": high_priority,
            }
        )

        return result

    def analyze_gaps(
        self,
        brand_name: str,
        competitor_names: List[str],
        responses: List[Dict],
    ) -> GapResult:
        """
        Perform complete gap analysis.

        Args:
            brand_name: Main brand
            competitor_names: Competitors to compare
            responses: Response dicts with text

        Returns:
            GapResult with identified gaps
        """
        # Get themes for all entities
        all_themes = self.theme_service.compare_themes(
            brand_name, competitor_names, responses
        )

        brand_themes = all_themes[brand_name]
        competitor_themes = {
            name: result
            for name, result in all_themes.items()
            if name != brand_name
        }

        return self.identify_gaps(brand_themes, competitor_themes)
