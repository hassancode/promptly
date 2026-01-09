"""
Base Provider Adapter

Abstract base class for all AI provider adapters.
Defines the interface and common functionality for querying AI providers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from schemas.provider import ProviderQueryResult, CitationCreate
from core.logging import get_logger

logger = get_logger(__name__)


class ProviderAdapter(ABC):
    """
    Abstract base class for AI provider adapters

    All provider implementations (OpenAI, Claude, Gemini, etc.)
    must inherit from this class and implement the query() method.

    The adapter is responsible for:
    1. Calling the provider's API
    2. Normalizing the response to a common format
    3. Extracting citations if available
    4. Handling provider-specific errors
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the provider adapter

        Args:
            api_key: Optional API key for the provider
        """
        self.api_key = api_key
        self.provider_name = self.get_provider_name()

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the provider's name

        Returns:
            Provider name (e.g., "openai", "claude", "gemini")
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the model name used by this adapter

        Returns:
            Model name (e.g., "gpt-4", "claude-3-sonnet", "gemini-pro")
        """
        pass

    @abstractmethod
    def supports_citations(self) -> bool:
        """
        Whether this provider supports citations

        Returns:
            True if the provider can return citations/sources
        """
        pass

    @abstractmethod
    async def query(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> ProviderQueryResult:
        """
        Query the AI provider with a prompt

        Args:
            prompt: The user's query prompt
            brand_name: The brand being analyzed
            competitors: List of competitor names
            context: Optional additional context (location, etc.)

        Returns:
            ProviderQueryResult with normalized response

        Raises:
            Exception: If the query fails (caller should handle gracefully)
        """
        pass

    def normalize_response(
        self,
        raw_response: Any,
        citations: Optional[List[CitationCreate]] = None
    ) -> Dict[str, Any]:
        """
        Normalize provider-specific response to common format

        Args:
            raw_response: Raw response from the provider
            citations: Extracted citations (if any)

        Returns:
            Normalized answer_text dictionary with:
            - text: str (main response text)
            - structured_data: dict (any structured info)
            - raw: any (original response for debugging)
        """
        # Default normalization - can be overridden by subclasses
        if isinstance(raw_response, str):
            return {
                "text": raw_response,
                "structured_data": {},
                "raw": raw_response
            }
        elif isinstance(raw_response, dict):
            return {
                "text": raw_response.get("text", str(raw_response)),
                "structured_data": raw_response,
                "raw": raw_response
            }
        else:
            return {
                "text": str(raw_response),
                "structured_data": {},
                "raw": raw_response
            }

    def extract_citations(self, raw_response: Any) -> List[CitationCreate]:
        """
        Extract citations from provider response

        Args:
            raw_response: Raw response from the provider

        Returns:
            List of citations (empty if none found)

        Note:
            Default implementation returns empty list.
            Providers with citation support should override this.
        """
        return []

    def calculate_citation_coverage(
        self,
        citations: List[CitationCreate]
    ) -> str:
        """
        Calculate citation coverage level

        Args:
            citations: List of citations

        Returns:
            "none", "partial", or "complete"
        """
        if not citations:
            return "none"
        elif len(citations) >= 3:
            return "complete"
        else:
            return "partial"

    async def query_with_timeout(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str],
        timeout_seconds: int = 30,
        context: Optional[Dict[str, Any]] = None
    ) -> ProviderQueryResult:
        """
        Query with timeout handling

        Args:
            prompt: The user's query prompt
            brand_name: The brand being analyzed
            competitors: List of competitor names
            timeout_seconds: Maximum time to wait (default: 30s)
            context: Optional additional context

        Returns:
            ProviderQueryResult (may have status="timeout" or "failed")
        """
        import asyncio

        try:
            result = await asyncio.wait_for(
                self.query(prompt, brand_name, competitors, context),
                timeout=timeout_seconds
            )
            return result

        except asyncio.TimeoutError:
            logger.warning(
                f"{self.provider_name} query timed out after {timeout_seconds}s",
                extra={"provider": self.provider_name, "timeout": timeout_seconds}
            )
            return ProviderQueryResult(
                provider=self.provider_name,
                model_name=self.get_model_name(),
                answer_text={"text": "", "error": "Query timed out"},
                citations=[],
                metadata={"timeout": timeout_seconds},
                citation_coverage="none",
                status="timeout",
                error_message=f"Query timed out after {timeout_seconds} seconds"
            )

        except Exception as e:
            logger.error(
                f"{self.provider_name} query failed: {e}",
                exc_info=True,
                extra={"provider": self.provider_name}
            )
            return ProviderQueryResult(
                provider=self.provider_name,
                model_name=self.get_model_name(),
                answer_text={"text": "", "error": str(e)},
                citations=[],
                metadata={"error": str(e)},
                citation_coverage="none",
                status="failed",
                error_message=str(e)
            )
