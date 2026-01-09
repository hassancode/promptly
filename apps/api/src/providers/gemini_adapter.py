"""
Google Gemini Provider Adapter

Adapter for querying Google Gemini with grounding (Google Search).
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

    Uses Gemini 2.0 Flash with Google Search grounding for real-time
    web information and citations.
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
        return "gemini-2.0-flash"

    def supports_citations(self) -> bool:
        return True  # Gemini supports grounding with Google Search citations

    async def query(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> ProviderQueryResult:
        """
        Query Google Gemini with Google Search grounding

        Args:
            prompt: User's query prompt
            brand_name: Brand being analyzed
            competitors: List of competitor names
            context: Optional context

        Returns:
            ProviderQueryResult with answer and citations from Google Search
        """
        try:
            if not self.client:
                return self._mock_response(prompt, brand_name, competitors)

            # Build enhanced prompt
            enhanced_prompt = self._build_enhanced_prompt(
                prompt, brand_name, competitors, context
            )

            logger.info(
                f"Querying Gemini with Google Search grounding: {enhanced_prompt[:100]}...",
                extra={"provider": "gemini", "brand": brand_name}
            )

            # Configure Google Search grounding tool
            from google.generativeai.types import Tool

            google_search_tool = Tool(
                google_search=self.client.protos.GoogleSearch()
            )

            # Create model with grounding
            model = self.client.GenerativeModel(
                model_name=self.get_model_name(),
                tools=[google_search_tool]
            )

            # Generate content with grounding
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
                    "google_search": True,
                    "finish_reason": getattr(response.candidates[0], 'finish_reason', 'stop') if response.candidates else "stop"
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

        Gemini with Google Search grounding returns grounding_metadata
        containing search_entry_point and grounding_chunks with web sources.

        Args:
            raw_response: Gemini response object

        Returns:
            List of citations from grounding sources
        """
        citations = []

        try:
            if not hasattr(raw_response, 'candidates') or not raw_response.candidates:
                return citations

            candidate = raw_response.candidates[0]

            # Check for grounding metadata
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                grounding = candidate.grounding_metadata

                # Extract from grounding_chunks (web sources)
                if hasattr(grounding, 'grounding_chunks') and grounding.grounding_chunks:
                    for idx, chunk in enumerate(grounding.grounding_chunks):
                        if hasattr(chunk, 'web') and chunk.web:
                            web_source = chunk.web
                            url = getattr(web_source, 'uri', '') or getattr(web_source, 'url', '')
                            title = getattr(web_source, 'title', 'Source')

                            if url:
                                citations.append(
                                    CitationCreate(
                                        url=url,
                                        title=title,
                                        snippet="",  # Gemini doesn't provide snippets in grounding
                                        source_type="web",
                                        position=idx
                                    )
                                )

                # Also check grounding_supports for inline citations
                if hasattr(grounding, 'grounding_supports') and grounding.grounding_supports:
                    existing_urls = {c.url for c in citations}
                    for support in grounding.grounding_supports:
                        if hasattr(support, 'grounding_chunk_indices'):
                            # These reference the grounding_chunks we already processed
                            pass
                        if hasattr(support, 'web_search_queries'):
                            # Store search queries in metadata if needed
                            pass

        except Exception as e:
            logger.warning(f"Failed to extract Gemini citations: {e}")

        return citations

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
