"""Provider configuration management"""
from enum import Enum
from typing import List
from .config import settings


class AIProvider(str, Enum):
    """Supported AI providers"""

    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    PERPLEXITY = "perplexity"
    GOOGLE_AI = "google_ai"
    HUGGINGFACE = "huggingface"


class ProviderConfig:
    """Provider configuration manager"""

    def __init__(self):
        self._enabled_providers = self._parse_enabled_providers()
        self._validate_providers()

    def _parse_enabled_providers(self) -> List[AIProvider]:
        """Parse ENABLED_PROVIDERS from environment variable"""
        provider_strings = [
            p.strip().lower() for p in settings.ENABLED_PROVIDERS.split(",")
        ]

        enabled = []
        for provider_str in provider_strings:
            try:
                provider = AIProvider(provider_str)
                enabled.append(provider)
            except ValueError:
                raise ValueError(
                    f"Invalid provider '{provider_str}'. "
                    f"Valid providers: {', '.join([p.value for p in AIProvider])}"
                )

        return enabled

    def _validate_providers(self):
        """Validate provider configuration"""
        if not self._enabled_providers:
            raise ValueError(
                "At least one provider must be enabled. "
                "Set ENABLED_PROVIDERS environment variable."
            )

    @property
    def enabled_providers(self) -> List[AIProvider]:
        """Get list of enabled providers"""
        return self._enabled_providers

    def is_enabled(self, provider: AIProvider) -> bool:
        """Check if a provider is enabled"""
        return provider in self._enabled_providers

    def get_enabled_count(self) -> int:
        """Get count of enabled providers"""
        return len(self._enabled_providers)


# Global provider config instance
provider_config = ProviderConfig()
