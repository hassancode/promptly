"""Insight generation service"""
import time
from typing import List, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy.orm import Session

from core.logging import get_logger
from core.exceptions import AppException
from models.analysis import Analysis, AnalysisStatus
from models.ai_response import AIResponse
from models.insight import Insight, InsightType, ConfidenceLevel
from services.scoring import (
    MentionService,
    VisibilityService,
    SentimentService,
    ThemeService,
    GapService,
)

logger = get_logger(__name__)


class InsightService:
    """
    Service for generating comprehensive insights from AI responses.

    Orchestrates all scoring services to generate visibility, sentiment,
    theme, gap, and comparison insights synchronously (<5s target).
    """

    def __init__(self, db: Session):
        self.db = db
        self.mention_service = MentionService()
        self.visibility_service = VisibilityService()
        self.sentiment_service = SentimentService()
        self.theme_service = ThemeService()
        self.gap_service = GapService()

    def _get_analysis_with_validation(self, analysis_id: UUID, user_id: UUID) -> Analysis:
        """Get analysis with ownership validation"""
        analysis = self.db.query(Analysis).filter(
            Analysis.id == analysis_id,
            Analysis.user_id == user_id
        ).first()

        if not analysis:
            raise AppException("Analysis not found", status_code=404)

        if analysis.status != AnalysisStatus.COMPLETED:
            raise AppException(
                "Analysis must be completed before generating insights",
                status_code=400
            )

        return analysis

    def _get_responses_as_dicts(self, analysis: Analysis) -> List[Dict]:
        """Convert AI responses to dict format for scoring services"""
        responses = []

        for prompt in analysis.prompts:
            for response in self.db.query(AIResponse).filter(
                AIResponse.prompt_id == prompt.id
            ).all():
                # Extract text from answer_text JSONB
                answer_text = response.answer_text or {}
                text = answer_text.get("text", "") if isinstance(answer_text, dict) else str(answer_text)

                responses.append({
                    "text": text,
                    "provider": response.provider.value if response.provider else "unknown",
                    "prompt_id": str(prompt.id),
                    "response_id": str(response.id),
                })

        return responses

    def _get_competitor_names(self, analysis: Analysis) -> List[str]:
        """Get list of competitor names for analysis"""
        return [c.name for c in analysis.competitors]

    def _build_evidence_references(
        self,
        response_ids: List[str],
        excerpts: Optional[List[str]] = None
    ) -> List[Dict]:
        """Build evidence reference list"""
        references = []
        for i, resp_id in enumerate(response_ids[:5]):  # Limit to 5 references
            ref = {
                "response_id": resp_id,
                "citation_ids": [],
            }
            if excerpts and i < len(excerpts):
                ref["excerpt"] = excerpts[i][:200]  # Limit excerpt length
            references.append(ref)
        return references

    def _determine_confidence(self, score: float) -> ConfidenceLevel:
        """Determine confidence level from score"""
        if score >= 0.8:
            return ConfidenceLevel.HIGH
        elif score >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif score > 0:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.NONE

    async def generate_visibility_insights(
        self,
        analysis: Analysis,
        responses: List[Dict],
        competitor_names: List[str],
    ) -> List[Insight]:
        """Generate visibility insights for brand and competitors"""
        insights = []

        # Get visibility scores
        visibility_scores = self.visibility_service.compare_visibility(
            analysis.brand_name, competitor_names, responses
        )

        # Create insight for brand
        brand_score = visibility_scores.get(analysis.brand_name)
        if brand_score:
            # Determine how brand ranks
            ranked = self.visibility_service.rank_by_visibility(visibility_scores)
            brand_rank = next(
                (i + 1 for i, s in enumerate(ranked) if s.entity_name == analysis.brand_name),
                len(ranked)
            )

            summary = f"{analysis.brand_name} ranks #{brand_rank} in AI visibility with a composite score of {brand_score.composite:.1%}"

            explanation = (
                f"Visibility breakdown for {analysis.brand_name}:\n"
                f"- Presence score: {brand_score.presence:.1%} (mentioned in AI responses)\n"
                f"- Frequency score: {brand_score.frequency:.1%} (relative mention frequency)\n"
                f"- Position score: {brand_score.position:.1%} (prominence in responses)\n\n"
                f"Compared to {len(competitor_names)} competitors, your brand ranks #{brand_rank} overall."
            )

            insight = Insight(
                id=uuid4(),
                analysis_id=analysis.id,
                insight_type=InsightType.VISIBILITY,
                brand_name=analysis.brand_name,
                summary=summary,
                explanation=explanation,
                evidence_references=self._build_evidence_references(
                    [r["response_id"] for r in responses[:5]]
                ),
                confidence_level=self._determine_confidence(brand_score.composite),
                scores=brand_score.to_dict(),
            )
            insights.append(insight)

        # Create comparison insights for top competitors
        for comp_name in competitor_names[:3]:
            comp_score = visibility_scores.get(comp_name)
            if comp_score and brand_score:
                diff = brand_score.composite - comp_score.composite

                if diff > 0.1:
                    summary = f"{analysis.brand_name} outperforms {comp_name} in visibility by {diff:.1%}"
                elif diff < -0.1:
                    summary = f"{comp_name} outperforms {analysis.brand_name} in visibility by {abs(diff):.1%}"
                else:
                    summary = f"{analysis.brand_name} and {comp_name} have similar visibility levels"

                explanation = (
                    f"Visibility comparison:\n"
                    f"- {analysis.brand_name}: {brand_score.composite:.1%}\n"
                    f"- {comp_name}: {comp_score.composite:.1%}\n"
                    f"Difference: {diff:+.1%}"
                )

                insight = Insight(
                    id=uuid4(),
                    analysis_id=analysis.id,
                    insight_type=InsightType.COMPARISON,
                    brand_name=analysis.brand_name,
                    competitor_name=comp_name,
                    summary=summary,
                    explanation=explanation,
                    evidence_references=[],
                    confidence_level=ConfidenceLevel.MEDIUM,
                    scores={
                        "brand_score": brand_score.composite,
                        "competitor_score": comp_score.composite,
                        "difference": diff,
                    },
                )
                insights.append(insight)

        return insights

    async def generate_sentiment_insights(
        self,
        analysis: Analysis,
        responses: List[Dict],
    ) -> List[Insight]:
        """Generate sentiment insights"""
        insights = []

        sentiment_result = await self.sentiment_service.analyze_sentiment(
            analysis.brand_name, responses
        )

        summary = f"Overall sentiment toward {analysis.brand_name} is {sentiment_result.overall.value}"

        explanation = (
            f"Sentiment analysis for {analysis.brand_name}:\n"
            f"- Positive mentions: {sentiment_result.positive_ratio:.1%}\n"
            f"- Neutral mentions: {sentiment_result.neutral_ratio:.1%}\n"
            f"- Negative mentions: {sentiment_result.negative_ratio:.1%}\n\n"
            f"Analysis confidence: {sentiment_result.confidence:.1%}"
        )

        insight = Insight(
            id=uuid4(),
            analysis_id=analysis.id,
            insight_type=InsightType.SENTIMENT,
            brand_name=analysis.brand_name,
            summary=summary,
            explanation=explanation,
            evidence_references=self._build_evidence_references(
                [r["response_id"] for r in responses[:3]]
            ),
            confidence_level=self._determine_confidence(sentiment_result.confidence),
            scores=sentiment_result.to_dict(),
        )
        insights.append(insight)

        return insights

    async def generate_theme_insights(
        self,
        analysis: Analysis,
        responses: List[Dict],
    ) -> List[Insight]:
        """Generate theme insights"""
        insights = []

        theme_result = self.theme_service.identify_themes(
            analysis.brand_name, responses
        )

        if theme_result.themes:
            top_themes = ", ".join(theme_result.top_themes[:5])
            summary = f"Key themes for {analysis.brand_name}: {top_themes}"

            theme_details = "\n".join(
                f"- {t.name}: mentioned {t.frequency} times (relevance: {t.relevance_score:.1%})"
                for t in theme_result.themes[:5]
            )

            explanation = (
                f"Theme analysis for {analysis.brand_name}:\n\n"
                f"{theme_details}\n\n"
                f"These themes represent the most common topics associated with your brand in AI responses."
            )

            insight = Insight(
                id=uuid4(),
                analysis_id=analysis.id,
                insight_type=InsightType.THEME,
                brand_name=analysis.brand_name,
                summary=summary,
                explanation=explanation,
                evidence_references=[],
                confidence_level=ConfidenceLevel.MEDIUM,
                scores=theme_result.to_dict(),
            )
            insights.append(insight)

        return insights

    async def generate_gap_insights(
        self,
        analysis: Analysis,
        responses: List[Dict],
        competitor_names: List[str],
    ) -> List[Insight]:
        """Generate gap insights"""
        insights = []

        gap_result = self.gap_service.analyze_gaps(
            analysis.brand_name, competitor_names, responses
        )

        if gap_result.gaps:
            high_priority = [g for g in gap_result.gaps if g.importance == "high"]

            if high_priority:
                gap_names = ", ".join(g.name for g in high_priority[:3])
                summary = f"High-priority content gaps identified: {gap_names}"

                gap_details = "\n".join(
                    f"- {g.name}: {g.description}\n  Recommendation: {g.recommendation}"
                    for g in high_priority[:5]
                )

                explanation = (
                    f"Gap analysis for {analysis.brand_name}:\n\n"
                    f"Found {gap_result.total_gaps} total gaps, "
                    f"{gap_result.high_priority_gaps} high-priority.\n\n"
                    f"High-priority gaps:\n{gap_details}"
                )

                insight = Insight(
                    id=uuid4(),
                    analysis_id=analysis.id,
                    insight_type=InsightType.GAP,
                    brand_name=analysis.brand_name,
                    summary=summary,
                    explanation=explanation,
                    evidence_references=[],
                    confidence_level=ConfidenceLevel.MEDIUM,
                    scores=gap_result.to_dict(),
                )
                insights.append(insight)

        return insights

    async def generate_mention_insights(
        self,
        analysis: Analysis,
        responses: List[Dict],
        competitor_names: List[str],
    ) -> List[Insight]:
        """Generate mention frequency insights"""
        insights = []

        mention_results = self.mention_service.compare_mention_frequencies(
            analysis.brand_name, competitor_names, responses
        )

        brand_mentions = mention_results.get(analysis.brand_name)
        if brand_mentions:
            summary = f"{analysis.brand_name} was mentioned {brand_mentions.total_count} times across AI responses"

            provider_breakdown = "\n".join(
                f"- {provider}: {count} mentions"
                for provider, count in sorted(brand_mentions.by_provider.items(), key=lambda x: -x[1])
            )

            explanation = (
                f"Mention frequency analysis for {analysis.brand_name}:\n\n"
                f"Total mentions: {brand_mentions.total_count}\n\n"
                f"By provider:\n{provider_breakdown}"
            )

            insight = Insight(
                id=uuid4(),
                analysis_id=analysis.id,
                insight_type=InsightType.MENTION,
                brand_name=analysis.brand_name,
                summary=summary,
                explanation=explanation,
                evidence_references=[],
                confidence_level=ConfidenceLevel.HIGH if brand_mentions.total_count > 5 else ConfidenceLevel.MEDIUM,
                scores={
                    "count": brand_mentions.total_count,
                    "providers": brand_mentions.by_provider,
                },
            )
            insights.append(insight)

        return insights

    async def generate_insights(
        self,
        analysis_id: UUID,
        user_id: UUID,
        regenerate: bool = False
    ) -> Dict:
        """
        Generate all insights for an analysis.

        Target: Complete within 5 seconds.

        Args:
            analysis_id: Analysis to generate insights for
            user_id: User ID for authorization
            regenerate: If True, delete existing insights first

        Returns:
            Dict with insights, recommendations, and timing info
        """
        start_time = time.time()

        logger.info(
            "Starting insight generation",
            extra={"analysis_id": str(analysis_id), "regenerate": regenerate}
        )

        # Get and validate analysis
        analysis = self._get_analysis_with_validation(analysis_id, user_id)

        # Delete existing insights if regenerating
        if regenerate:
            self.db.query(Insight).filter(Insight.analysis_id == analysis_id).delete()
            self.db.commit()
            logger.info("Deleted existing insights for regeneration")

        # Check for existing insights
        existing_insights = self.db.query(Insight).filter(
            Insight.analysis_id == analysis_id
        ).count()

        if existing_insights > 0 and not regenerate:
            # Return existing insights
            insights = self.db.query(Insight).filter(
                Insight.analysis_id == analysis_id
            ).all()

            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                "analysis_id": str(analysis_id),
                "brand_name": analysis.brand_name,
                "insights": [i.to_dict() for i in insights],
                "recommendations": [],  # Fetch separately
                "generated_at": datetime.utcnow().isoformat(),
                "generation_time_ms": elapsed_ms,
                "from_cache": True,
            }

        # Get response data
        responses = self._get_responses_as_dicts(analysis)
        competitor_names = self._get_competitor_names(analysis)

        if not responses:
            raise AppException("No AI responses found for analysis", status_code=400)

        # Generate all insights concurrently
        all_insights = []

        # Visibility insights
        visibility_insights = await self.generate_visibility_insights(
            analysis, responses, competitor_names
        )
        all_insights.extend(visibility_insights)

        # Sentiment insights
        sentiment_insights = await self.generate_sentiment_insights(
            analysis, responses
        )
        all_insights.extend(sentiment_insights)

        # Theme insights
        theme_insights = await self.generate_theme_insights(analysis, responses)
        all_insights.extend(theme_insights)

        # Gap insights
        gap_insights = await self.generate_gap_insights(
            analysis, responses, competitor_names
        )
        all_insights.extend(gap_insights)

        # Mention insights
        mention_insights = await self.generate_mention_insights(
            analysis, responses, competitor_names
        )
        all_insights.extend(mention_insights)

        # Save all insights
        for insight in all_insights:
            self.db.add(insight)

        self.db.commit()

        elapsed_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "Insight generation complete",
            extra={
                "analysis_id": str(analysis_id),
                "insight_count": len(all_insights),
                "elapsed_ms": elapsed_ms,
            }
        )

        return {
            "analysis_id": str(analysis_id),
            "brand_name": analysis.brand_name,
            "insights": [i.to_dict() for i in all_insights],
            "recommendations": [],  # Generated by RecommendationService
            "generated_at": datetime.utcnow().isoformat(),
            "generation_time_ms": elapsed_ms,
            "from_cache": False,
        }

    def get_insights(self, analysis_id: UUID, user_id: UUID) -> List[Insight]:
        """Get existing insights for an analysis"""
        analysis = self._get_analysis_with_validation(analysis_id, user_id)

        return self.db.query(Insight).filter(
            Insight.analysis_id == analysis_id
        ).all()

    def get_insight_summary(self, analysis_id: UUID, user_id: UUID) -> Dict:
        """Get summary of insights for an analysis"""
        analysis = self._get_analysis_with_validation(analysis_id, user_id)

        insights = self.db.query(Insight).filter(
            Insight.analysis_id == analysis_id
        ).all()

        # Extract visibility score
        visibility_insight = next(
            (i for i in insights if i.insight_type == InsightType.VISIBILITY),
            None
        )
        visibility_score = None
        if visibility_insight and visibility_insight.scores:
            visibility_score = visibility_insight.scores.get("composite")

        # Extract sentiment
        sentiment_insight = next(
            (i for i in insights if i.insight_type == InsightType.SENTIMENT),
            None
        )
        overall_sentiment = None
        if sentiment_insight and sentiment_insight.scores:
            overall_sentiment = sentiment_insight.scores.get("overall")

        return {
            "analysis_id": str(analysis_id),
            "brand_name": analysis.brand_name,
            "total_insights": len(insights),
            "total_recommendations": 0,  # Fetch separately
            "visibility_score": visibility_score,
            "overall_sentiment": overall_sentiment,
            "insight_types": list(set(i.insight_type.value for i in insights)),
            "has_insights": len(insights) > 0,
        }
