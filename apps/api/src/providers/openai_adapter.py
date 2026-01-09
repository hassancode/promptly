"""
OpenAI Provider Adapter

Adapter for querying OpenAI models with web search and citations.
"""
import os
from typing import List, Dict, Any, Optional
from providers.base_adapter import ProviderAdapter
from schemas.provider import ProviderQueryResult, CitationCreate
from core.logging import get_logger

logger = get_logger(__name__)


class OpenAIAdapter(ProviderAdapter):
    """
    OpenAI provider adapter

    Uses OpenAI's GPT models with web search capabilities.
    Supports citation extraction from web search results.
    """

    def __init__(self):
        """Initialize OpenAI adapter"""
        api_key = os.getenv("OPENAI_API_KEY")
        super().__init__(api_key)

        # Initialize OpenAI client if API key is available
        if self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("OpenAI adapter initialized successfully")
            except ImportError:
                logger.warning("openai package not installed - using mock mode")
                self.client = None
        else:
            logger.warning("OPENAI_API_KEY not set - using mock mode")
            self.client = None

    def get_provider_name(self) -> str:
        return "openai"

    def get_model_name(self) -> str:
        return "gpt-4"  # Can be configured

    def supports_citations(self) -> bool:
        return True  # OpenAI supports web search with citations

    async def query(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> ProviderQueryResult:
        """
        Query OpenAI with web search enabled

        Args:
            prompt: User's query prompt
            brand_name: Brand being analyzed
            competitors: List of competitor names
            context: Optional context (location, etc.)

        Returns:
            ProviderQueryResult with answer and citations
        """
        try:
            if not self.client:
                # Mock response for testing without API key
                return self._mock_response(prompt, brand_name, competitors)

            # Build enhanced prompt with context
            enhanced_prompt = self._build_enhanced_prompt(
                prompt, brand_name, competitors, context
            )

            logger.info(
                f"Querying OpenAI: {enhanced_prompt[:100]}...",
                extra={"provider": "openai", "brand": brand_name}
            )

            # Call OpenAI API
            # TODO: Replace with actual OpenAI API call with web search
            # For now, using a simple completion
            response = self.client.chat.completions.create(
                model=self.get_model_name(),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant analyzing brand mentions and visibility."
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )

            # Extract answer
            answer_text = response.choices[0].message.content

            # Extract citations (if available from web search)
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
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                },
                citation_coverage=self.calculate_citation_coverage(citations),
                status="success"
            )

        except Exception as e:
            logger.error(
                f"OpenAI query failed: {e}",
                exc_info=True,
                extra={"provider": "openai"}
            )
            raise

    def _build_enhanced_prompt(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Build an enhanced prompt with brand and competitor context

        Args:
            prompt: Original user prompt
            brand_name: Brand name
            competitors: Competitor names
            context: Optional additional context

        Returns:
            Enhanced prompt string
        """
        enhanced = f"""Brand Analysis Context:
- Primary Brand: {brand_name}
- Competitors: {', '.join(competitors) if competitors else 'None specified'}

User Question: {prompt}

Please provide a comprehensive answer that specifically mentions these brands where relevant, and cite sources if possible."""

        if context and "location" in context:
            enhanced = f"Location: {context['location']}\n\n" + enhanced

        return enhanced

    def extract_citations(self, raw_response: Any) -> List[CitationCreate]:
        """
        Extract citations from OpenAI response

        Note: This is a placeholder. OpenAI web search responses
        would include citations that need to be extracted.

        Args:
            raw_response: Raw OpenAI response object

        Returns:
            List of citations
        """
        # TODO: Extract actual citations from OpenAI web search results
        # For now, return empty list
        return []

    def _mock_response(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str]
    ) -> ProviderQueryResult:
        """
        Generate a mock response for testing without API key

        Args:
            prompt: User prompt
            brand_name: Brand name
            competitors: Competitor names

        Returns:
            Mock ProviderQueryResult
        """
        competitors_str = ", ".join(competitors) if competitors else "various competitors"

        mock_answer = f"""Based on the analysis, {brand_name} is frequently mentioned alongside {competitors_str}.

{brand_name} is recognized for its innovative approach and market positioning. When compared to competitors, it demonstrates strong brand visibility in AI-generated content.

Key observations:
1. {brand_name} appears in contexts related to industry leadership
2. Competitor mentions include {competitors_str}
3. Brand sentiment appears generally positive

Note: This is a mock response. Configure OPENAI_API_KEY for real results."""

        mock_citations = [
            CitationCreate(
                url="https://example.com/article-1",
                title=f"{brand_name} Industry Analysis",
                snippet=f"Analysis of {brand_name} and its market position...",
                source_type="web",
                position=0
            ),
            CitationCreate(
                url="https://example.com/article-2",
                title=f"Competitive Landscape: {brand_name} vs {competitors[0] if competitors else 'Others'}",
                snippet=f"Comparison of {brand_name} with competitors...",
                source_type="web",
                position=1
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
