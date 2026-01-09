"""
Claude Query Provider Adapter

Adapter for querying Claude AI with web search capabilities.
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

    Uses Anthropic's Claude models with web search tool for real-time
    information retrieval and citations.
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
        return "claude-sonnet-4-20250514"

    def supports_citations(self) -> bool:
        return True  # Claude provides citations via web search tool

    async def query(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> ProviderQueryResult:
        """
        Query Claude AI with web search

        Args:
            prompt: User's query prompt
            brand_name: Brand being analyzed
            competitors: List of competitor names
            context: Optional context

        Returns:
            ProviderQueryResult with answer and citations from web search
        """
        try:
            if not self.client:
                return self._mock_response(prompt, brand_name, competitors)

            # Build enhanced prompt
            enhanced_prompt = self._build_enhanced_prompt(
                prompt, brand_name, competitors, context
            )

            logger.info(
                f"Querying Claude with web search: {enhanced_prompt[:100]}...",
                extra={"provider": "claude", "brand": brand_name}
            )

            # Call Claude API with web search tool
            message = self.client.messages.create(
                model=self.get_model_name(),
                max_tokens=4096,
                tools=[{"type": "web_search_20250305"}],
                messages=[
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ]
            )

            # Extract answer from response content blocks
            answer_text = self._extract_answer_from_response(message)

            # Extract citations from web search results
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
                    "web_search_enabled": True,
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

    def _extract_answer_from_response(self, message: Any) -> str:
        """
        Extract answer text from Claude response with web search

        Args:
            message: Claude API response object

        Returns:
            Extracted answer text
        """
        answer_parts = []

        try:
            for block in message.content:
                if hasattr(block, 'type'):
                    if block.type == 'text':
                        answer_parts.append(block.text)
        except Exception as e:
            logger.warning(f"Failed to extract answer from Claude response: {e}")

        return "\n".join(answer_parts) if answer_parts else ""

    def extract_citations(self, raw_response: Any) -> List[CitationCreate]:
        """
        Extract citations from Claude web search results

        Claude's web search tool returns results in content blocks with
        type 'web_search_tool_result' containing search results.

        Args:
            raw_response: Claude API response object

        Returns:
            List of citations from web search results
        """
        citations = []

        try:
            if not hasattr(raw_response, 'content'):
                return citations

            position = 0
            for block in raw_response.content:
                if hasattr(block, 'type'):
                    # Handle web search tool results
                    if block.type == 'tool_use' and hasattr(block, 'name') and block.name == 'web_search':
                        continue  # This is the tool call, not the result

                    # Web search results come in server_tool_use blocks
                    if block.type == 'web_search_tool_result':
                        if hasattr(block, 'content') and block.content:
                            for result in block.content:
                                if hasattr(result, 'type') and result.type == 'web_search_result':
                                    url = getattr(result, 'url', '')
                                    title = getattr(result, 'title', 'Source')
                                    snippet = getattr(result, 'snippet', '') or getattr(result, 'encrypted_content', '')

                                    if url:
                                        citations.append(
                                            CitationCreate(
                                                url=url,
                                                title=title,
                                                snippet=snippet[:500] if snippet else '',
                                                source_type="web",
                                                position=position
                                            )
                                        )
                                        position += 1

        except Exception as e:
            logger.warning(f"Failed to extract Claude citations: {e}")

        return citations

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
