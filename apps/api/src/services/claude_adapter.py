"""
Claude AI adapter for competitor suggestions

Uses Anthropic's Claude API to generate contextually relevant competitor suggestions.
"""
import os
from typing import List, Optional
import anthropic
from core.logging import get_logger

logger = get_logger(__name__)


class ClaudeAdapter:
    """
    Adapter for Claude AI competitor suggestions

    Uses Claude to generate up to 3 relevant competitors for a given brand.
    Handles API errors gracefully and provides fallback behavior.
    """

    def __init__(self):
        """Initialize Claude client"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not set - competitor suggestions will use fallback")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=api_key)

    async def suggest_competitors(
        self,
        brand_name: str,
        context: Optional[str] = None,
        max_suggestions: int = 3
    ) -> List[str]:
        """
        Generate competitor suggestions using Claude

        Args:
            brand_name: The brand to find competitors for
            context: Optional context to help with disambiguation
            max_suggestions: Maximum number of suggestions (default 3)

        Returns:
            List of competitor brand names

        Raises:
            Exception: If API call fails (caller should handle gracefully)
        """
        if not self.client:
            logger.warning(f"Claude client not initialized - using fallback for {brand_name}")
            return self._fallback_suggestions(brand_name)

        try:
            # Build prompt for Claude
            prompt = self._build_prompt(brand_name, context, max_suggestions)

            logger.info(f"Requesting competitor suggestions for brand: {brand_name}")

            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract competitor names from response
            response_text = message.content[0].text
            competitors = self._parse_competitors(response_text, max_suggestions)

            logger.info(
                f"Claude suggested {len(competitors)} competitors for {brand_name}: {competitors}"
            )

            return competitors

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}", exc_info=True)
            # Return fallback suggestions on API error
            return self._fallback_suggestions(brand_name)

        except Exception as e:
            logger.error(f"Unexpected error in Claude adapter: {e}", exc_info=True)
            return self._fallback_suggestions(brand_name)

    def _build_prompt(
        self,
        brand_name: str,
        context: Optional[str],
        max_suggestions: int
    ) -> str:
        """Build the prompt for Claude"""
        base_prompt = f"""You are a competitive intelligence expert. Given a brand name, suggest up to {max_suggestions} direct competitors.

Brand: {brand_name}"""

        if context:
            base_prompt += f"\nContext: {context}"

        base_prompt += f"""

Requirements:
- Suggest {max_suggestions} DIRECT competitors (companies in the same industry/market)
- Focus on well-known, legitimate companies
- Return ONLY the company names, one per line
- Do NOT include explanations, numbers, or bullet points
- Do NOT include the original brand in the list
- Each name should be the official brand name (e.g., "Tesla" not "Tesla Motors")

Example format:
Apple
Microsoft
Google

Now suggest competitors for {brand_name}:"""

        return base_prompt

    def _parse_competitors(self, response_text: str, max_suggestions: int) -> List[str]:
        """
        Parse competitor names from Claude's response

        Args:
            response_text: Raw response from Claude
            max_suggestions: Maximum number to return

        Returns:
            List of cleaned competitor names
        """
        # Split by lines and clean
        lines = response_text.strip().split('\n')
        competitors = []

        for line in lines:
            # Clean the line
            cleaned = line.strip()

            # Skip empty lines
            if not cleaned:
                continue

            # Remove common prefixes (numbers, bullets, etc.)
            cleaned = cleaned.lstrip('0123456789.-*• ')

            # Skip if still empty or looks like formatting
            if not cleaned or cleaned.startswith('#'):
                continue

            competitors.append(cleaned)

            # Stop if we have enough
            if len(competitors) >= max_suggestions:
                break

        return competitors[:max_suggestions]

    def _fallback_suggestions(self, brand_name: str) -> List[str]:
        """
        Provide fallback suggestions when Claude is unavailable

        Returns generic placeholder suggestions to allow testing
        without API key.
        """
        logger.info(f"Using fallback suggestions for {brand_name}")

        # Generic fallback - in production this might query a database
        # or use a simpler heuristic
        fallbacks = {
            "tesla": ["Rivian", "Lucid Motors", "Ford"],
            "apple": ["Samsung", "Google", "Microsoft"],
            "nike": ["Adidas", "Puma", "Under Armour"],
            "coca-cola": ["Pepsi", "Dr Pepper", "Sprite"],
        }

        brand_lower = brand_name.lower()

        # Check for exact match
        if brand_lower in fallbacks:
            return fallbacks[brand_lower]

        # Return generic suggestions
        return [
            f"Competitor A of {brand_name}",
            f"Competitor B of {brand_name}",
            f"Competitor C of {brand_name}",
        ]

    async def suggest_prompts(
        self,
        brand_name: str,
        competitors: List[str],
        max_suggestions: int = 5
    ) -> List[str]:
        """
        Generate prompt suggestions using Claude

        Args:
            brand_name: The brand to analyze
            competitors: List of competitor names
            max_suggestions: Maximum number of prompts (default 5)

        Returns:
            List of suggested prompt texts

        Raises:
            Exception: If API call fails (caller should handle gracefully)
        """
        if not self.client:
            logger.warning(f"Claude client not initialized - using fallback prompts")
            return self._fallback_prompts(brand_name, competitors)

        try:
            # Build prompt for Claude
            prompt = self._build_prompt_suggestion_prompt(
                brand_name, competitors, max_suggestions
            )

            logger.info(f"Requesting prompt suggestions for brand: {brand_name}")

            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract prompts from response
            response_text = message.content[0].text
            prompts = self._parse_prompts(response_text, max_suggestions)

            logger.info(
                f"Claude suggested {len(prompts)} prompts for {brand_name}"
            )

            return prompts

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}", exc_info=True)
            return self._fallback_prompts(brand_name, competitors)

        except Exception as e:
            logger.error(f"Unexpected error in Claude adapter: {e}", exc_info=True)
            return self._fallback_prompts(brand_name, competitors)

    def _build_prompt_suggestion_prompt(
        self,
        brand_name: str,
        competitors: List[str],
        max_suggestions: int
    ) -> str:
        """Build the prompt for generating query prompts"""
        competitors_str = ", ".join(competitors) if competitors else "various competitors"

        prompt = f"""You are an AI search visibility expert. Generate {max_suggestions} questions that a user might ask an AI assistant that would compare {brand_name} against its competitors ({competitors_str}).

Requirements:
- Generate {max_suggestions} questions that would naturally mention these brands
- Questions should be realistic searches users would ask AI assistants
- Focus on comparison, recommendations, or general inquiries about the industry
- Each question should be 10-20 words
- Return ONLY the questions, one per line
- Do NOT include numbers, bullets, or explanations

Example format:
What are the best electric vehicles for long-distance travel?
Which smartphone brands offer the best value for money?
What companies are leading innovation in athletic footwear?

Now generate {max_suggestions} questions for analyzing {brand_name} against {competitors_str}:"""

        return prompt

    def _parse_prompts(self, response_text: str, max_suggestions: int) -> List[str]:
        """
        Parse prompt suggestions from Claude's response

        Args:
            response_text: Raw response from Claude
            max_suggestions: Maximum number to return

        Returns:
            List of cleaned prompt texts
        """
        # Split by lines and clean
        lines = response_text.strip().split('\n')
        prompts = []

        for line in lines:
            # Clean the line
            cleaned = line.strip()

            # Skip empty lines
            if not cleaned:
                continue

            # Remove common prefixes (numbers, bullets, etc.)
            cleaned = cleaned.lstrip('0123456789.-*• ')

            # Skip if still empty or looks like formatting
            if not cleaned or cleaned.startswith('#'):
                continue

            # Ensure it ends with a question mark
            if not cleaned.endswith('?'):
                cleaned += '?'

            prompts.append(cleaned)

            # Stop if we have enough
            if len(prompts) >= max_suggestions:
                break

        return prompts[:max_suggestions]

    def _fallback_prompts(self, brand_name: str, competitors: List[str]) -> List[str]:
        """
        Provide fallback prompt suggestions when Claude is unavailable

        Returns generic prompts to allow testing without API key.
        """
        logger.info(f"Using fallback prompts for {brand_name}")

        competitors_str = ", ".join(competitors[:2]) if competitors else "its competitors"

        return [
            f"What are the best alternatives to {brand_name}?",
            f"How does {brand_name} compare to {competitors_str}?",
            f"What are the top brands in {brand_name}'s industry?",
            f"Which company is better, {brand_name} or {competitors[0] if competitors else 'others'}?",
            f"What are the pros and cons of {brand_name}?",
        ]
