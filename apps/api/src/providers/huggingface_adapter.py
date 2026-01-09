"""
Hugging Face Provider Adapter

Adapter for querying Hugging Face models (classification/sentiment analysis).
Note: HF models typically don't provide citations, focused on classification tasks.
"""
import os
from typing import List, Dict, Any, Optional
from providers.base_adapter import ProviderAdapter
from schemas.provider import ProviderQueryResult, CitationCreate
from core.logging import get_logger

logger = get_logger(__name__)


class HuggingFaceAdapter(ProviderAdapter):
    """
    Hugging Face provider adapter

    Uses Hugging Face Inference API for text classification/analysis.
    Note: This provider doesn't support citations as it's focused on
    classification rather than generative search.
    """

    def __init__(self):
        """Initialize Hugging Face adapter"""
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        super().__init__(api_key)

        if self.api_key:
            try:
                from huggingface_hub import InferenceClient
                self.client = InferenceClient(token=self.api_key)
                logger.info("Hugging Face adapter initialized successfully")
            except ImportError:
                logger.warning("huggingface_hub package not installed - using mock mode")
                self.client = None
        else:
            logger.warning("HUGGINGFACE_API_KEY not set - using mock mode")
            self.client = None

    def get_provider_name(self) -> str:
        return "huggingface"

    def get_model_name(self) -> str:
        return "mistralai/Mistral-7B-Instruct-v0.2"

    def supports_citations(self) -> bool:
        return False  # HuggingFace focused on classification, not citations

    async def query(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> ProviderQueryResult:
        """
        Query Hugging Face model

        Args:
            prompt: User's query prompt
            brand_name: Brand being analyzed
            competitors: List of competitor names
            context: Optional context

        Returns:
            ProviderQueryResult with classification/analysis (no citations)
        """
        try:
            if not self.client:
                return self._mock_response(prompt, brand_name, competitors)

            # Build analysis prompt
            analysis_prompt = self._build_analysis_prompt(
                prompt, brand_name, competitors, context
            )

            logger.info(
                f"Querying Hugging Face: {analysis_prompt[:100]}...",
                extra={"provider": "huggingface", "brand": brand_name}
            )

            # Call Hugging Face Inference API
            response = self.client.text_generation(
                analysis_prompt,
                model=self.get_model_name(),
                max_new_tokens=1000,
                temperature=0.7,
                return_full_text=False
            )

            # Extract answer
            answer_text = response if isinstance(response, str) else response.get('generated_text', '')

            # No citations for HuggingFace
            citations = []

            # Normalize response
            normalized_answer = self.normalize_response(answer_text, citations)

            return ProviderQueryResult(
                provider=self.get_provider_name(),
                model_name=self.get_model_name(),
                answer_text=normalized_answer,
                citations=citations,
                metadata={
                    "model": self.get_model_name(),
                    "type": "text_generation",
                    "citations_supported": False
                },
                citation_coverage="none",  # HF doesn't provide citations
                status="success"
            )

        except Exception as e:
            logger.error(
                f"Hugging Face query failed: {e}",
                exc_info=True,
                extra={"provider": "huggingface"}
            )
            raise

    def _build_analysis_prompt(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build analysis prompt for HuggingFace"""
        system_prompt = f"""<s>[INST] You are an expert brand analyst. Analyze the following brands and provide insights.

Brand: {brand_name}
Competitors: {', '.join(competitors) if competitors else 'None specified'}

Question: {prompt}

Provide a detailed analysis focusing on:
1. Brand positioning
2. Competitive advantages
3. Market perception
4. Key differentiators

Do not make up citations or sources. Focus on analytical insights. [/INST]</s>"""

        return system_prompt

    def extract_citations(self, raw_response: Any) -> List[CitationCreate]:
        """
        HuggingFace doesn't provide citations

        Args:
            raw_response: HF response

        Returns:
            Empty list (no citations)
        """
        return []

    def _mock_response(
        self,
        prompt: str,
        brand_name: str,
        competitors: List[str]
    ) -> ProviderQueryResult:
        """Generate mock HuggingFace analysis"""
        competitors_str = ", ".join(competitors) if competitors else "competitors"

        mock_answer = f"""**Brand Analysis: {brand_name}**

**Executive Summary:**
{brand_name} operates in a competitive market environment alongside {competitors_str}. This analysis examines key positioning factors and competitive dynamics.

**Brand Positioning:**
{brand_name} has established itself through distinct value propositions and market approach. The brand demonstrates recognition within its target segments.

**Competitive Analysis:**
Compared to {competitors_str}, {brand_name} exhibits both similarities and differentiators:
• Market approach and strategy
• Product/service offerings
• Customer engagement patterns
• Brand perception metrics

**Key Insights:**
1. **Differentiation:** {brand_name} distinguishes itself through specific attributes
2. **Market Position:** Competitive standing relative to {competitors_str}
3. **Perception:** How the brand is viewed in the marketplace
4. **Trajectory:** Growth indicators and market momentum

**Analytical Conclusion:**
{brand_name} demonstrates viable competitive positioning. Continued monitoring of market dynamics and competitor activities remains important for strategic planning.

*Note: Analysis based on general market understanding. This is a mock response - configure HUGGINGFACE_API_KEY for model-generated analysis.*"""

        # HuggingFace doesn't provide citations
        citations = []

        normalized_answer = self.normalize_response(mock_answer, citations)

        return ProviderQueryResult(
            provider=self.get_provider_name(),
            model_name=self.get_model_name(),
            answer_text=normalized_answer,
            citations=citations,
            metadata={
                "mode": "mock",
                "reason": "No API key configured",
                "citations_supported": False
            },
            citation_coverage="none",
            status="success"
        )
