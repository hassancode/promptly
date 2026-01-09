"""
Perplexity Provider Adapter

Adapter for querying Perplexity AI with native citation support.
"""
import os
from typing import List, Dict, Any, Optional
from providers.base_adapter import ProviderAdapter
from schemas.provider import ProviderQueryResult, CitationCreate
from core.logging import get_logger

logger = get_logger(__name__)


class PerplexityAdapter(ProviderAdapter):
    """
    Perplexity AI provider adapter

    Perplexity provides native citations in its responses,
    making it ideal for brand visibility analysis.
    """

    def __init__(self):
        """Initialize Perplexity adapter"""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        super().__init__(api_key)

        if self.api_key:
            try:
                # Perplexity uses OpenAI-compatible API
                import openai
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.perplexity.ai"
                )
                logger.info("Perplexity adapter initialized successfully")
            except ImportError:
                logger.warning("openai package not installed - using mock mode")
                self.client = None
        else:
            logger.warning("PERPLEXITY_API_KEY not set - using mock mode")
            self.client = None

    def get_provider_name(self) -> str:
        return "perplexity"

    def get_model_name(self) -> str:
        return "llama-3.1-sonar-large-128k-online"

    def supports_citations(self) -> bool:
        return True  # Perplexity has native citation support

    async def query(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> ProviderQueryResult:
        """
        Query Perplexity AI

        Args:
            prompt: User's query prompt
            brand_name: Brand being analyzed
            competitors: List of competitor names
            context: Optional context

        Returns:
            ProviderQueryResult with answer and native citations
        """
        try:
            if not self.client:
                return self._mock_response(prompt, brand_name, competitors)

            # Build enhanced prompt
            enhanced_prompt = self._build_enhanced_prompt(
                prompt, brand_name, competitors, context
            )

            logger.info(
                f"Querying Perplexity: {enhanced_prompt[:100]}...",
                extra={"provider": "perplexity", "brand": brand_name}
            )

            # Call Perplexity API (OpenAI-compatible)
            response = self.client.chat.completions.create(
                model=self.get_model_name(),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant analyzing brand visibility and competitive positioning. Always cite your sources."
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1500,
                return_citations=True,  # Perplexity-specific parameter
                return_images=False
            )

            # Extract answer
            answer_text = response.choices[0].message.content

            # Extract native citations
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
                    "finish_reason": response.choices[0].finish_reason,
                    "citations_enabled": True
                },
                citation_coverage=self.calculate_citation_coverage(citations),
                status="success"
            )

        except Exception as e:
            logger.error(
                f"Perplexity query failed: {e}",
                exc_info=True,
                extra={"provider": "perplexity"}
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
        enhanced = f"""Analyze the following brands and provide detailed insights with citations:

Primary Brand: {brand_name}
Competitors: {', '.join(competitors) if competitors else 'None specified'}

Question: {prompt}

Please provide a comprehensive answer that:
1. Specifically mentions these brands where relevant
2. Cites authoritative sources for all claims
3. Provides URLs to sources
4. Focuses on factual, verifiable information"""

        if context and "location" in context:
            enhanced = f"Geographic Context: {context['location']}\n\n" + enhanced

        return enhanced

    def extract_citations(self, raw_response: Any) -> List[CitationCreate]:
        """
        Extract native citations from Perplexity response

        Perplexity returns citations in the response metadata.

        Args:
            raw_response: Perplexity response object

        Returns:
            List of citations
        """
        citations = []

        try:
            # Perplexity includes citations in response
            if hasattr(raw_response, 'citations') and raw_response.citations:
                for idx, citation in enumerate(raw_response.citations):
                    citations.append(
                        CitationCreate(
                            url=citation.get('url', ''),
                            title=citation.get('title', 'Source'),
                            snippet=citation.get('text', ''),
                            source_type="web",
                            position=idx
                        )
                    )
        except Exception as e:
            logger.warning(f"Failed to extract Perplexity citations: {e}")

        return citations

    def _mock_response(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str]
    ) -> ProviderQueryResult:
        """Generate mock response with citations"""
        competitors_str = ", ".join(competitors) if competitors else "various competitors"

        mock_answer = f"""**Brand Analysis: {brand_name} vs {competitors_str}**

{brand_name} demonstrates notable market positioning in its sector [1]. Recent market analysis indicates strong brand recognition and competitive advantages [2].

**Competitive Position:**
When compared to {competitors_str}, {brand_name} shows distinctive characteristics. Industry reports highlight differentiation in product offerings and market approach [3].

**Market Dynamics:**
The competitive landscape is characterized by innovation and customer focus. {brand_name} and its competitors are actively pursuing market expansion strategies [4].

**Key Insights:**
- Strong brand visibility in search results
- Competitive pricing and value proposition
- Active engagement in market discourse

[1] Industry Market Report 2026
[2] Brand Recognition Study
[3] Competitive Analysis Brief
[4] Market Trends Report

*Note: This is a mock response. Configure PERPLEXITY_API_KEY for real results with native citations.*"""

        mock_citations = [
            CitationCreate(
                url="https://example.com/market-report-2026",
                title="Industry Market Report 2026",
                snippet=f"Comprehensive analysis of {brand_name} market position and competitive landscape...",
                source_type="web",
                position=0
            ),
            CitationCreate(
                url="https://example.com/brand-recognition-study",
                title="Brand Recognition Study",
                snippet=f"Study analyzing {brand_name} brand awareness metrics...",
                source_type="web",
                position=1
            ),
            CitationCreate(
                url="https://example.com/competitive-analysis",
                title="Competitive Analysis Brief",
                snippet=f"Detailed comparison of {brand_name} versus {competitors_str}...",
                source_type="web",
                position=2
            ),
            CitationCreate(
                url="https://example.com/market-trends",
                title="Market Trends Report",
                snippet="Current trends and future outlook for the industry...",
                source_type="web",
                position=3
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
