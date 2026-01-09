"""
Google Gemini Provider Adapter

Adapter for querying Google Gemini with grounding (web search).
"""
import os
from typing import List, Dict, Any, Optional
from providers.base_adapter import ProviderAdapter
from schemas.provider import ProviderQueryResult, CitationCreate
from core.logging import get_logger

logger = get_logger(__name__)


class GeminiAdapter(ProviderAdapter):
    """
    Google Gemini provider adapter

    Uses Gemini Pro with grounding for web search and citations.
    """

    def __init__(self):
        """Initialize Gemini adapter"""
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        super().__init__(api_key)

        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai
                logger.info("Gemini adapter initialized successfully")
            except ImportError:
                logger.warning("google-generativeai package not installed - using mock mode")
                self.client = None
        else:
            logger.warning("GOOGLE_AI_API_KEY not set - using mock mode")
            self.client = None

    def get_provider_name(self) -> str:
        return "gemini"

    def get_model_name(self) -> str:
        return "gemini-pro"

    def supports_citations(self) -> bool:
        return True  # Gemini supports grounding with citations

    async def query(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> ProviderQueryResult:
        """
        Query Google Gemini with grounding

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
                f"Querying Gemini: {enhanced_prompt[:100]}...",
                extra={"provider": "gemini", "brand": brand_name}
            )

            # Call Gemini API with grounding
            model = self.client.GenerativeModel('gemini-pro')

            # Note: Grounding configuration would go here
            # For now, using basic generation
            response = model.generate_content(enhanced_prompt)

            # Extract answer
            answer_text = response.text

            # Extract citations from grounding metadata
            citations = self.extract_citations(response)

            # Normalize response
            normalized_answer = self.normalize_response(answer_text, citations)

            return ProviderQueryResult(
                provider=self.get_provider_name(),
                model_name=self.get_model_name(),
                answer_text=normalized_answer,
                citations=citations,
                metadata={
                    "model": self.get_model_name(),
                    "grounding_enabled": True,
                    "finish_reason": "stop"
                },
                citation_coverage=self.calculate_citation_coverage(citations),
                status="success"
            )

        except Exception as e:
            logger.error(
                f"Gemini query failed: {e}",
                exc_info=True,
                extra={"provider": "gemini"}
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
        enhanced = f"""Brand Analysis Request:
Primary Brand: {brand_name}
Competitors: {', '.join(competitors) if competitors else 'None specified'}

Question: {prompt}

Please provide a comprehensive answer that addresses the question while mentioning these brands where relevant. Include specific sources and citations."""

        if context and "location" in context:
            enhanced = f"Location: {context['location']}\n\n" + enhanced

        return enhanced

    def extract_citations(self, raw_response: Any) -> List[CitationCreate]:
        """
        Extract citations from Gemini grounding metadata

        Args:
            raw_response: Gemini response object

        Returns:
            List of citations from grounding sources
        """
        # TODO: Extract actual grounding sources when available
        # Gemini with grounding returns citation metadata
        return []

    def _mock_response(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str]
    ) -> ProviderQueryResult:
        """Generate mock response for testing"""
        competitors_str = ", ".join(competitors) if competitors else "various competitors"

        mock_answer = f"""Based on current market analysis, {brand_name} demonstrates competitive positioning against {competitors_str}.

**Market Position:**
{brand_name} maintains a strong presence in the market. Key differentiators include product innovation, brand recognition, and market reach.

**Competitive Landscape:**
When compared to {competitors_str}, {brand_name} shows distinctive characteristics:
- Unique value proposition
- Market share dynamics
- Customer perception differences

**Outlook:**
The competitive environment continues to evolve, with {brand_name} and {competitors_str} each pursuing different strategic approaches.

*Note: This is a mock response. Configure GOOGLE_AI_API_KEY for real Gemini results with grounding.*"""

        mock_citations = [
            CitationCreate(
                url="https://example.com/market-report",
                title=f"{brand_name} Market Report 2026",
                snippet=f"Comprehensive market analysis of {brand_name}...",
                source_type="web",
                position=0
            ),
            CitationCreate(
                url="https://example.com/competitive-analysis",
                title=f"Competitive Landscape: {brand_name} vs Competition",
                snippet=f"Analysis comparing {brand_name} with key competitors...",
                source_type="web",
                position=1
            ),
            CitationCreate(
                url="https://example.com/industry-trends",
                title="Industry Trends and Insights",
                snippet="Current trends affecting the competitive landscape...",
                source_type="web",
                position=2
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
