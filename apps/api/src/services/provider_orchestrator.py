"""
Provider Orchestrator

Manages concurrent querying of multiple AI providers.
Handles timeouts, failures, and progress tracking.
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from core.config import settings
from core.logging import get_logger
from models.analysis import Analysis
from models.prompt import Prompt
from models.ai_response import AIResponse, ResponseStatus, CitationCoverage
from models.citation import Citation
from schemas.provider import ProviderQueryResult, ProviderInfo
from providers.base_adapter import ProviderAdapter

logger = get_logger(__name__)


class ProviderOrchestrator:
    """
    Orchestrates concurrent AI provider queries

    Responsibilities:
    - Query only enabled providers from configuration
    - Run queries concurrently with timeout handling
    - Track provider success/failure (non-blocking)
    - Calculate progress based on enabled providers only
    - Persist results to database
    """

    def __init__(self, db: Session):
        """
        Initialize the orchestrator

        Args:
            db: Database session
        """
        self.db = db
        self.enabled_providers = self._get_enabled_providers()
        self.provider_adapters = self._initialize_adapters()

        logger.info(
            f"Provider Orchestrator initialized with {len(self.enabled_providers)} enabled providers",
            extra={
                "enabled_providers": self.enabled_providers,
                "total_adapters": len(self.provider_adapters)
            }
        )

    def _get_enabled_providers(self) -> List[str]:
        """
        Get list of enabled providers from configuration

        Returns:
            List of enabled provider names

        Raises:
            ValueError: If no providers are enabled
        """
        # Get from environment variable (comma-separated)
        enabled = getattr(settings, 'ENABLED_PROVIDERS', 'openai,claude,gemini,perplexity,google_ai,huggingface')

        if isinstance(enabled, str):
            providers = [p.strip() for p in enabled.split(',') if p.strip()]
        else:
            providers = enabled

        if not providers:
            raise ValueError("At least one provider must be enabled")

        logger.info(f"Enabled providers: {providers}")
        return providers

    def _initialize_adapters(self) -> Dict[str, ProviderAdapter]:
        """
        Initialize provider adapters for enabled providers

        Returns:
            Dictionary of provider_name -> adapter instance

        Note:
            Only initializes adapters for enabled providers
        """
        adapters = {}

        # Import adapters only for enabled providers
        # This allows the system to run even if some provider SDKs aren't installed

        for provider in self.enabled_providers:
            try:
                if provider == "openai":
                    from providers.openai_adapter import OpenAIAdapter
                    adapters["openai"] = OpenAIAdapter()
                elif provider == "claude":
                    from providers.claude_query_adapter import ClaudeQueryAdapter
                    adapters["claude"] = ClaudeQueryAdapter()
                elif provider == "gemini":
                    from providers.gemini_adapter import GeminiAdapter
                    adapters["gemini"] = GeminiAdapter()
                elif provider == "perplexity":
                    from providers.perplexity_adapter import PerplexityAdapter
                    adapters["perplexity"] = PerplexityAdapter()
                elif provider == "google_ai":
                    from providers.google_ai_adapter import GoogleAIAdapter
                    adapters["google_ai"] = GoogleAIAdapter()
                elif provider == "huggingface":
                    from providers.huggingface_adapter import HuggingFaceAdapter
                    adapters["huggingface"] = HuggingFaceAdapter()
                else:
                    logger.warning(f"Unknown provider: {provider}")

            except ImportError as e:
                logger.warning(
                    f"Could not import adapter for {provider}: {e}. Provider will be skipped.",
                    extra={"provider": provider}
                )
            except Exception as e:
                logger.error(
                    f"Error initializing adapter for {provider}: {e}",
                    exc_info=True,
                    extra={"provider": provider}
                )

        return adapters

    async def query_all_providers(
        self,
        analysis: Analysis,
        prompt: Prompt,
        timeout_seconds: int = 30
    ) -> Dict[str, Any]:
        """
        Query all enabled providers concurrently for a single prompt

        Args:
            analysis: The analysis being performed
            prompt: The prompt to query
            timeout_seconds: Timeout per provider (default: 30s)

        Returns:
            Dictionary with:
            - total: Total enabled providers
            - successful: Number of successful queries
            - failed: Number of failed queries
            - responses: List of AIResponse IDs
            - provider_statuses: Dict of provider -> status
        """
        brand_name = analysis.brand_name
        competitors = [c.name for c in analysis.competitors]

        logger.info(
            f"Starting concurrent queries for analysis {analysis.id}, prompt {prompt.id}",
            extra={
                "analysis_id": str(analysis.id),
                "prompt_id": str(prompt.id),
                "enabled_providers": self.enabled_providers,
                "total_providers": len(self.provider_adapters)
            }
        )

        # Create query tasks for all enabled providers
        tasks = []
        provider_names = []

        for provider_name, adapter in self.provider_adapters.items():
            task = self._query_single_provider(
                adapter,
                prompt.text,
                brand_name,
                competitors,
                timeout_seconds
            )
            tasks.append(task)
            provider_names.append(provider_name)

        # Execute all queries concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        successful = 0
        failed = 0
        response_ids = []
        provider_statuses = {}

        for provider_name, result in zip(provider_names, results):
            if isinstance(result, Exception):
                logger.error(
                    f"Provider {provider_name} raised exception: {result}",
                    exc_info=result,
                    extra={"provider": provider_name}
                )
                failed += 1
                provider_statuses[provider_name] = "failed"
            elif result.status in ["success"]:
                # Save successful result to database
                response_id = self._save_response(prompt.id, result)
                response_ids.append(response_id)
                successful += 1
                provider_statuses[provider_name] = "success"
                logger.info(
                    f"Provider {provider_name} query succeeded",
                    extra={
                        "provider": provider_name,
                        "response_id": str(response_id),
                        "citations": len(result.citations)
                    }
                )
            else:
                # Save failed/timeout result
                response_id = self._save_response(prompt.id, result)
                response_ids.append(response_id)
                failed += 1
                provider_statuses[provider_name] = result.status
                logger.warning(
                    f"Provider {provider_name} query {result.status}: {result.error_message}",
                    extra={
                        "provider": provider_name,
                        "status": result.status,
                        "error": result.error_message
                    }
                )

        return {
            "total": len(self.provider_adapters),
            "successful": successful,
            "failed": failed,
            "responses": response_ids,
            "provider_statuses": provider_statuses
        }

    async def _query_single_provider(
        self,
        adapter: ProviderAdapter,
        prompt: str,
        brand_name: str,
        competitors: List[str],
        timeout_seconds: int
    ) -> ProviderQueryResult:
        """
        Query a single provider with timeout handling

        Args:
            adapter: Provider adapter instance
            prompt: Query prompt
            brand_name: Brand being analyzed
            competitors: List of competitor names
            timeout_seconds: Timeout in seconds

        Returns:
            ProviderQueryResult
        """
        try:
            result = await adapter.query_with_timeout(
                prompt=prompt,
                brand_name=brand_name,
                competitors=competitors,
                timeout_seconds=timeout_seconds
            )
            return result

        except Exception as e:
            logger.error(
                f"Unexpected error querying {adapter.provider_name}: {e}",
                exc_info=True,
                extra={"provider": adapter.provider_name}
            )
            return ProviderQueryResult(
                provider=adapter.provider_name,
                model_name=adapter.get_model_name(),
                answer_text={"text": "", "error": str(e)},
                citations=[],
                metadata={"error": str(e)},
                citation_coverage="none",
                status="failed",
                error_message=str(e)
            )

    def _save_response(
        self,
        prompt_id: str,
        result: ProviderQueryResult
    ) -> str:
        """
        Save provider query result to database

        Args:
            prompt_id: ID of the prompt
            result: Provider query result

        Returns:
            ID of created AIResponse
        """
        # Create AIResponse
        ai_response = AIResponse(
            prompt_id=prompt_id,
            provider=result.provider,
            model_name=result.model_name,
            answer_text=result.answer_text,
            response_metadata=result.metadata,
            citation_coverage=CitationCoverage(result.citation_coverage),
            status=ResponseStatus(result.status),
            completed_at=datetime.utcnow() if result.status in ["success", "failed", "timeout"] else None
        )

        self.db.add(ai_response)
        self.db.flush()  # Get the ID without committing

        # Create citations
        for citation_data in result.citations:
            citation = Citation(
                ai_response_id=ai_response.id,
                url=citation_data.url,
                title=citation_data.title,
                snippet=citation_data.snippet,
                source_type=citation_data.source_type,
                position=citation_data.position
            )
            self.db.add(citation)

        self.db.commit()
        self.db.refresh(ai_response)

        return str(ai_response.id)

    def get_provider_info(self) -> List[ProviderInfo]:
        """
        Get information about all providers (enabled and disabled)

        Returns:
            List of ProviderInfo objects
        """
        all_providers = ["openai", "gemini", "claude", "perplexity", "google_ai", "huggingface"]
        provider_info = []

        for provider_name in all_providers:
            enabled = provider_name in self.enabled_providers
            adapter = self.provider_adapters.get(provider_name)

            if adapter:
                info = ProviderInfo(
                    name=provider_name,
                    enabled=enabled,
                    supports_citations=adapter.supports_citations(),
                    supports_streaming=False,  # SSE is handled at orchestrator level
                    model_name=adapter.get_model_name()
                )
            else:
                info = ProviderInfo(
                    name=provider_name,
                    enabled=False,
                    supports_citations=False,
                    supports_streaming=False,
                    model_name="unknown"
                )

            provider_info.append(info)

        return provider_info

    def get_progress(self, analysis_id: str) -> Dict[str, Any]:
        """
        Calculate progress for an analysis

        Args:
            analysis_id: Analysis ID

        Returns:
            Progress information dict
        """
        # Get all prompts for the analysis
        prompts = self.db.query(Prompt).filter(
            Prompt.analysis_id == analysis_id
        ).all()

        total_expected = len(prompts) * len(self.provider_adapters)
        total_completed = 0
        total_successful = 0
        total_failed = 0

        for prompt in prompts:
            responses = self.db.query(AIResponse).filter(
                AIResponse.prompt_id == prompt.id
            ).all()

            for response in responses:
                if response.status in [ResponseStatus.SUCCESS, ResponseStatus.FAILED, ResponseStatus.TIMEOUT]:
                    total_completed += 1
                    if response.status == ResponseStatus.SUCCESS:
                        total_successful += 1
                    else:
                        total_failed += 1

        percentage = (total_completed / total_expected * 100) if total_expected > 0 else 0

        return {
            "completed": total_completed,
            "total": total_expected,
            "successful": total_successful,
            "failed": total_failed,
            "percentage": round(percentage, 2),
            "enabled_providers": self.enabled_providers,
            "enabled_count": len(self.provider_adapters)
        }
