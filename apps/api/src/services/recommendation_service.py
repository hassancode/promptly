"""Recommendation generation service"""
from typing import List, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy.orm import Session

from core.logging import get_logger
from core.exceptions import AppException
from models.analysis import Analysis, AnalysisStatus
from models.insight import Insight, InsightType, ConfidenceLevel
from models.recommendation import Recommendation, ImpactLevel

logger = get_logger(__name__)


# Recommendation templates based on insight types
RECOMMENDATION_TEMPLATES = {
    InsightType.VISIBILITY: [
        {
            "condition": lambda scores: scores.get("composite", 0) < 0.3,
            "text": "Increase brand visibility by creating more content optimized for AI search engines",
            "rationale": "Your brand has low visibility in AI responses. Creating targeted content that addresses common queries can improve your presence.",
            "impact": ImpactLevel.HIGH,
        },
        {
            "condition": lambda scores: scores.get("frequency", 0) < scores.get("presence", 0),
            "text": "Improve mention frequency by addressing more diverse topics in your content strategy",
            "rationale": "While your brand is mentioned, the frequency is lower than your presence score suggests potential.",
            "impact": ImpactLevel.MEDIUM,
        },
        {
            "condition": lambda scores: scores.get("position", 0) < 0.5,
            "text": "Work on establishing your brand as a primary reference in your industry",
            "rationale": "Your brand tends to be mentioned later in AI responses. Building thought leadership can improve position prominence.",
            "impact": ImpactLevel.MEDIUM,
        },
    ],
    InsightType.SENTIMENT: [
        {
            "condition": lambda scores: scores.get("negative", 0) > 0.3,
            "text": "Address negative sentiment through improved customer experience and public relations",
            "rationale": "A significant portion of AI responses reflect negative sentiment. Proactive reputation management is recommended.",
            "impact": ImpactLevel.HIGH,
        },
        {
            "condition": lambda scores: scores.get("positive", 0) < 0.3,
            "text": "Amplify positive customer stories and success cases to improve sentiment",
            "rationale": "Positive sentiment is lower than ideal. Showcasing customer success can shift the narrative.",
            "impact": ImpactLevel.MEDIUM,
        },
        {
            "condition": lambda scores: scores.get("neutral", 0) > 0.5,
            "text": "Differentiate your brand to move from neutral to positive sentiment",
            "rationale": "Most mentions are neutral. Creating more distinctive brand experiences can generate positive associations.",
            "impact": ImpactLevel.MEDIUM,
        },
    ],
    InsightType.GAP: [
        {
            "condition": lambda scores: scores.get("high_priority_gaps", 0) >= 3,
            "text": "Prioritize addressing the top 3 content gaps to improve competitive positioning",
            "rationale": "Multiple high-priority gaps were identified where competitors have coverage but your brand doesn't.",
            "impact": ImpactLevel.HIGH,
        },
        {
            "condition": lambda scores: scores.get("total_gaps", 0) >= 5,
            "text": "Develop a content strategy to systematically address identified coverage gaps",
            "rationale": "Several topic areas are underrepresented in your brand's AI presence.",
            "impact": ImpactLevel.MEDIUM,
        },
    ],
    InsightType.THEME: [
        {
            "condition": lambda scores: True,  # Always suggest if themes exist
            "text": "Leverage identified themes in marketing and content to reinforce brand associations",
            "rationale": "These themes are already associated with your brand. Amplifying them can strengthen your positioning.",
            "impact": ImpactLevel.LOW,
        },
    ],
    InsightType.COMPARISON: [
        {
            "condition": lambda scores: scores.get("difference", 0) < -0.2,
            "text": "Analyze and adapt successful strategies from higher-visibility competitors",
            "rationale": "Competitors significantly outperform your brand in visibility. Understanding their approach could help close the gap.",
            "impact": ImpactLevel.HIGH,
        },
    ],
}


class RecommendationService:
    """
    Service for generating actionable recommendations from insights.

    Generates minimum 5 recommendations based on insight analysis,
    prioritized by expected impact.
    """

    MIN_RECOMMENDATIONS = 5

    def __init__(self, db: Session):
        self.db = db

    def _get_analysis_with_validation(self, analysis_id: UUID, user_id: UUID) -> Analysis:
        """Get analysis with ownership validation"""
        analysis = self.db.query(Analysis).filter(
            Analysis.id == analysis_id,
            Analysis.user_id == user_id
        ).first()

        if not analysis:
            raise AppException("Analysis not found", status_code=404)

        return analysis

    def _determine_confidence(self, insight: Insight, condition_strength: float = 0.7) -> ConfidenceLevel:
        """Determine confidence level for recommendation"""
        if insight.confidence_level == ConfidenceLevel.HIGH:
            return ConfidenceLevel.HIGH if condition_strength > 0.7 else ConfidenceLevel.MEDIUM
        elif insight.confidence_level == ConfidenceLevel.MEDIUM:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    def _build_evidence_references(self, insight: Insight) -> List[Dict]:
        """Build evidence references linking back to insight"""
        return [{
            "insight_id": str(insight.id),
            "response_id": ref.get("response_id") if isinstance(ref, dict) else None,
            "citation_ids": ref.get("citation_ids", []) if isinstance(ref, dict) else [],
        } for ref in (insight.evidence_references or [])[:3]]

    def generate_from_insight(self, insight: Insight) -> List[Recommendation]:
        """Generate recommendations from a single insight"""
        recommendations = []

        templates = RECOMMENDATION_TEMPLATES.get(insight.insight_type, [])
        scores = insight.scores or {}

        for idx, template in enumerate(templates):
            try:
                if template["condition"](scores):
                    rec = Recommendation(
                        id=uuid4(),
                        analysis_id=insight.analysis_id,
                        text=template["text"],
                        rationale=template["rationale"],
                        expected_impact=template["impact"],
                        confidence_level=self._determine_confidence(insight),
                        evidence_references=self._build_evidence_references(insight),
                        priority=self._calculate_priority(template["impact"], idx),
                    )
                    recommendations.append(rec)
            except Exception as e:
                logger.warning(f"Error evaluating recommendation template: {e}")
                continue

        return recommendations

    def _calculate_priority(self, impact: ImpactLevel, order: int) -> int:
        """Calculate priority score (lower = higher priority)"""
        base = {
            ImpactLevel.HIGH: 1,
            ImpactLevel.MEDIUM: 4,
            ImpactLevel.LOW: 7,
        }.get(impact, 5)

        return base + order

    def _add_default_recommendations(
        self,
        analysis: Analysis,
        existing_count: int
    ) -> List[Recommendation]:
        """Add default recommendations to meet minimum count"""
        defaults = [
            {
                "text": "Regularly monitor AI search visibility to track brand performance",
                "rationale": "AI-powered search is becoming increasingly important. Regular monitoring helps identify trends and opportunities.",
                "impact": ImpactLevel.MEDIUM,
            },
            {
                "text": "Create FAQ content that directly addresses common customer queries",
                "rationale": "AI assistants often reference FAQ-style content. Well-structured Q&A can improve brand visibility.",
                "impact": ImpactLevel.MEDIUM,
            },
            {
                "text": "Ensure consistent brand messaging across all digital touchpoints",
                "rationale": "AI systems aggregate information from multiple sources. Consistency helps build clear brand associations.",
                "impact": ImpactLevel.LOW,
            },
            {
                "text": "Build relationships with industry publications and thought leaders",
                "rationale": "AI systems often cite authoritative sources. Being mentioned by trusted voices improves credibility.",
                "impact": ImpactLevel.MEDIUM,
            },
            {
                "text": "Optimize technical SEO to ensure content is easily discoverable",
                "rationale": "AI systems rely on crawlable, structured content. Technical optimization improves discoverability.",
                "impact": ImpactLevel.LOW,
            },
        ]

        recommendations = []
        needed = self.MIN_RECOMMENDATIONS - existing_count

        for idx, default in enumerate(defaults[:needed]):
            rec = Recommendation(
                id=uuid4(),
                analysis_id=analysis.id,
                text=default["text"],
                rationale=default["rationale"],
                expected_impact=default["impact"],
                confidence_level=ConfidenceLevel.MEDIUM,
                evidence_references=[],
                priority=8 + idx,  # Lower priority than insight-based recommendations
            )
            recommendations.append(rec)

        return recommendations

    async def generate_recommendations(
        self,
        analysis_id: UUID,
        user_id: UUID,
        regenerate: bool = False
    ) -> List[Recommendation]:
        """
        Generate recommendations for an analysis based on its insights.

        Ensures minimum 5 recommendations are generated.

        Args:
            analysis_id: Analysis to generate recommendations for
            user_id: User ID for authorization
            regenerate: If True, delete existing recommendations first

        Returns:
            List of Recommendation objects
        """
        logger.info(
            "Generating recommendations",
            extra={"analysis_id": str(analysis_id), "regenerate": regenerate}
        )

        analysis = self._get_analysis_with_validation(analysis_id, user_id)

        # Delete existing if regenerating
        if regenerate:
            self.db.query(Recommendation).filter(
                Recommendation.analysis_id == analysis_id
            ).delete()
            self.db.commit()

        # Check for existing
        existing = self.db.query(Recommendation).filter(
            Recommendation.analysis_id == analysis_id
        ).all()

        if existing and not regenerate:
            return existing

        # Get insights
        insights = self.db.query(Insight).filter(
            Insight.analysis_id == analysis_id
        ).all()

        if not insights:
            raise AppException(
                "No insights found. Generate insights first.",
                status_code=400
            )

        # Generate recommendations from insights
        all_recommendations = []
        for insight in insights:
            recs = self.generate_from_insight(insight)
            all_recommendations.extend(recs)

        # Deduplicate by text
        seen_texts = set()
        unique_recommendations = []
        for rec in all_recommendations:
            if rec.text not in seen_texts:
                seen_texts.add(rec.text)
                unique_recommendations.append(rec)

        # Add defaults if needed
        if len(unique_recommendations) < self.MIN_RECOMMENDATIONS:
            defaults = self._add_default_recommendations(
                analysis, len(unique_recommendations)
            )
            unique_recommendations.extend(defaults)

        # Sort by priority
        unique_recommendations.sort(key=lambda r: r.priority)

        # Save to database
        for rec in unique_recommendations:
            self.db.add(rec)

        self.db.commit()

        logger.info(
            "Recommendations generated",
            extra={
                "analysis_id": str(analysis_id),
                "count": len(unique_recommendations),
            }
        )

        return unique_recommendations

    def get_recommendations(self, analysis_id: UUID, user_id: UUID) -> List[Recommendation]:
        """Get existing recommendations for an analysis"""
        self._get_analysis_with_validation(analysis_id, user_id)

        return self.db.query(Recommendation).filter(
            Recommendation.analysis_id == analysis_id
        ).order_by(Recommendation.priority).all()

    def prioritize_recommendations(
        self,
        recommendations: List[Recommendation]
    ) -> List[Recommendation]:
        """Re-prioritize recommendations by impact and confidence"""
        def score(rec: Recommendation) -> float:
            impact_score = {
                ImpactLevel.HIGH: 3,
                ImpactLevel.MEDIUM: 2,
                ImpactLevel.LOW: 1,
            }.get(rec.expected_impact, 1)

            confidence_score = {
                ConfidenceLevel.HIGH: 1.5,
                ConfidenceLevel.MEDIUM: 1.0,
                ConfidenceLevel.LOW: 0.5,
            }.get(rec.confidence_level, 1.0)

            return impact_score * confidence_score

        sorted_recs = sorted(recommendations, key=score, reverse=True)

        # Update priorities
        for idx, rec in enumerate(sorted_recs):
            rec.priority = idx + 1

        return sorted_recs
