"""
Claude Query Provider Adapter

Adapter for querying Claude AI with search capabilities.
"""
import os
from typing import List, Dict, Any, Optional
from providers.base_adapter import ProviderAdapter
from schemas.provider import ProviderQueryResult, CitationCreate
from core.logging import get_logger

logger = get_logger(__name__)


class ClaudeQueryAdapter(ProviderAdapter):
    """
    Claude query adapter

    Uses Anthropic's Claude models with search capabilities.
    """

    def __init__(self):
        """Initialize Claude adapter"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        super().__init__(api_key)

        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("Claude query adapter initialized successfully")
            except ImportError:
                logger.warning("anthropic package not installed - using mock mode")
                self.client = None
        else:
            logger.warning("ANTHROPIC_API_KEY not set - using mock mode")
            self.client = None

    def get_provider_name(self) -> str:
        return "claude"

    def get_model_name(self) -> str:
        return "claude-3-5-sonnet-20241022"

    def supports_citations(self) -> bool:
        return True  # Claude can provide citations when using search

    async def query(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> ProviderQueryResult:
        """
        Query Claude AI

        Args:
            prompt: User's query prompt
            brand_name: Brand being analyzed
            competitors: List of competitor names
            context: Optional context

        Returns:
            ProviderQueryResult with answer and citations
        """
        try:
            if not self.client:
                return self._mock_response(prompt, brand_name, competitors)

            # Build enhanced prompt
            enhanced_prompt = self._build_enhanced_prompt(
                prompt, brand_name, competitors, context
            )

            logger.info(
                f"Querying Claude: {enhanced_prompt[:100]}...",
                extra={"provider": "claude", "brand": brand_name}
            )

            # Call Claude API
            message = self.client.messages.create(
                model=self.get_model_name(),
                max_tokens=1500,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ]
            )

            # Extract answer
            answer_text = message.content[0].text

            # Extract citations
            citations = self.extract_citations(message)

            # Normalize response
            normalized_answer = self.normalize_response(answer_text, citations)

            return ProviderQueryResult(
                provider=self.get_provider_name(),
                model_name=self.get_model_name(),
                answer_text=normalized_answer,
                citations=citations,
                metadata={
                    "model": self.get_model_name(),
                    "stop_reason": message.stop_reason,
                    "usage": {
                        "input_tokens": message.usage.input_tokens,
                        "output_tokens": message.usage.output_tokens
                    }
                },
                citation_coverage=self.calculate_citation_coverage(citations),
                status="success"
            )

        except Exception as e:
            logger.error(
                f"Claude query failed: {e}",
                exc_info=True,
                extra={"provider": "claude"}
            )
            raise

    def _build_enhanced_prompt(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build enhanced prompt with context"""
        enhanced = f"""You are analyzing brand visibility and mentions in AI-generated content.

Brand: {brand_name}
Competitors: {', '.join(competitors) if competitors else 'None specified'}

User Question: {prompt}

Provide a comprehensive answer that addresses the question while specifically mentioning these brands where relevant. Include citations or sources if possible."""

        if context and "location" in context:
            enhanced = f"Location Context: {context['location']}\n\n" + enhanced

        return enhanced

    def _mock_response(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str]
    ) -> ProviderQueryResult:
        """Generate mock response for testing"""
        competitors_str = ", ".join(competitors) if competitors else "various competitors"

        mock_answer = f"""Analyzing {brand_name} in comparison to {competitors_str}:

{brand_name} demonstrates strong market presence and brand recognition. When evaluated against competitors, several key factors emerge:

1. **Brand Visibility**: {brand_name} frequently appears in industry discussions and AI-generated content
2. **Competitive Position**: Compared to {competitors_str}, {brand_name} shows distinctive characteristics
3. **Market Perception**: Overall sentiment towards {brand_name} appears favorable

Note: This is a mock response. Configure ANTHROPIC_API_KEY for actual Claude analysis."""

        mock_citations = [
            CitationCreate(
                url="https://example.com/brand-analysis",
                title=f"{brand_name} Market Analysis 2026",
                snippet=f"Comprehensive analysis of {brand_name}'s market position...",
                source_type="web",
                position=0
            )
        ]

        normalized_answer = self.normalize_response(mock_answer, mock_citations)

        return ProviderQueryResult(
            provider=self.get_provider_name(),
            model_name=self.get_model_name(),
            answer_text=normalized_answer,
            citations=mock_citations,
            metadata={"mode": "mock", "reason": "No API key configured"},
            citation_coverage=self.calculate_citation_coverage(mock_citations),
            status="success"
        )
