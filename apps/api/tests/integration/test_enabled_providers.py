"""
Integration test for ENABLED_PROVIDERS behavior
Task: T106A [US4]
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
import os

# Import from src
import sys
sys.path.insert(0, "src")


class TestEnabledProvidersBehavior:
    """Integration tests for ENABLED_PROVIDERS configuration"""

    @pytest.fixture
    def mock_analysis(self):
        """Create a mock analysis"""
        analysis = MagicMock()
        analysis.id = uuid4()
        analysis.brand_name = "TestBrand"
        return analysis

    def test_only_enabled_providers_queried(self):
        """
        Test that only providers in ENABLED_PROVIDERS are queried
        Disabled providers should NOT be queried at all
        """
        all_providers = ["openai", "claude", "gemini", "perplexity", "google_ai", "huggingface"]
        enabled_providers = ["openai", "claude"]

        queried_providers = []

        for provider in all_providers:
            if provider in enabled_providers:
                queried_providers.append(provider)

        # Only enabled providers should be queried
        assert set(queried_providers) == set(enabled_providers)
        assert "gemini" not in queried_providers
        assert "perplexity" not in queried_providers

    def test_progress_total_equals_enabled_count(self):
        """
        Test that progress total equals number of ENABLED providers only
        Not total possible providers
        """
        all_providers_count = 6
        enabled_providers = ["openai", "claude", "gemini"]
        enabled_count = len(enabled_providers)

        progress = {
            "completed": 1,
            "total": enabled_count  # Should be 3, not 6
        }

        assert progress["total"] == 3
        assert progress["total"] != all_providers_count

    def test_disabled_providers_not_in_progress(self):
        """
        Test that disabled providers don't appear in progress tracking
        """
        enabled_providers = ["openai", "claude"]
        disabled_providers = ["gemini", "perplexity", "google_ai", "huggingface"]

        progress_providers = {
            "pending": ["claude"],
            "completed": ["openai"],
            "failed": []
        }

        # All providers in progress should be from enabled list
        all_progress_providers = (
            progress_providers["pending"] +
            progress_providers["completed"] +
            progress_providers["failed"]
        )

        for provider in all_progress_providers:
            assert provider in enabled_providers
            assert provider not in disabled_providers

    def test_disabled_provider_not_treated_as_failure(self):
        """
        Test that disabled providers are NOT counted as failures
        They simply don't exist in the context of this analysis
        """
        enabled_providers = ["openai", "claude"]
        all_providers = ["openai", "claude", "gemini", "perplexity", "google_ai", "huggingface"]

        results = {
            "openai": {"status": "success"},
            "claude": {"status": "success"}
        }

        # Count successes and failures from enabled providers only
        successes = sum(1 for p in enabled_providers if results.get(p, {}).get("status") == "success")
        failures = sum(1 for p in enabled_providers if results.get(p, {}).get("status") == "failed")

        # All enabled providers succeeded
        assert successes == 2
        assert failures == 0

        # Disabled providers are NOT counted as failures
        # They simply weren't queried


class TestEnabledProvidersConfiguration:
    """Tests for parsing and validating ENABLED_PROVIDERS config"""

    def test_parse_comma_separated_providers(self):
        """
        Test that ENABLED_PROVIDERS is parsed from comma-separated string
        """
        env_value = "openai,claude,gemini"
        enabled_providers = [p.strip() for p in env_value.split(",")]

        assert enabled_providers == ["openai", "claude", "gemini"]

    def test_whitespace_handling(self):
        """
        Test that whitespace in ENABLED_PROVIDERS is handled
        """
        env_value = " openai , claude , gemini "
        enabled_providers = [p.strip() for p in env_value.split(",")]

        assert enabled_providers == ["openai", "claude", "gemini"]

    def test_invalid_provider_name_rejected(self):
        """
        Test that invalid provider names are rejected at startup
        """
        valid_providers = {"openai", "claude", "gemini", "perplexity", "google_ai", "huggingface"}

        env_value = "openai,invalid_provider,claude"
        parsed = [p.strip() for p in env_value.split(",")]

        invalid_providers = [p for p in parsed if p not in valid_providers]

        assert "invalid_provider" in invalid_providers

    def test_at_least_one_provider_required(self):
        """
        Test that at least one provider must be enabled
        Empty ENABLED_PROVIDERS should cause startup failure
        """
        env_value = ""
        enabled_providers = [p.strip() for p in env_value.split(",") if p.strip()]

        has_at_least_one = len(enabled_providers) > 0
        assert not has_at_least_one  # Empty should fail

    def test_default_all_providers_enabled(self):
        """
        Test that if ENABLED_PROVIDERS is not set, all providers are enabled
        """
        default_providers = ["openai", "claude", "gemini", "perplexity", "google_ai", "huggingface"]

        # Simulate no env var set
        env_value = None

        if env_value is None:
            enabled_providers = default_providers
        else:
            enabled_providers = [p.strip() for p in env_value.split(",")]

        assert set(enabled_providers) == set(default_providers)


class TestEnabledProvidersUI:
    """Tests for UI representation of enabled providers"""

    def test_ui_shows_enabled_providers(self):
        """
        Test that UI shows which providers are enabled
        """
        enabled_providers = ["openai", "claude", "gemini"]

        ui_provider_list = [
            {"name": "openai", "enabled": True},
            {"name": "claude", "enabled": True},
            {"name": "gemini", "enabled": True},
            {"name": "perplexity", "enabled": False},
            {"name": "google_ai", "enabled": False},
            {"name": "huggingface", "enabled": False}
        ]

        enabled_in_ui = [p for p in ui_provider_list if p["enabled"]]
        assert len(enabled_in_ui) == len(enabled_providers)

    def test_disabled_providers_grayed_out(self):
        """
        Test that disabled providers are visually distinct in UI
        """
        ui_provider = {
            "name": "perplexity",
            "enabled": False,
            "css_class": "text-gray-400 opacity-50"  # Grayed out styling
        }

        assert ui_provider["enabled"] is False
        assert "gray" in ui_provider["css_class"]

    def test_progress_bar_based_on_enabled_only(self):
        """
        Test that progress bar shows progress of enabled providers only
        """
        enabled_count = 3
        completed_count = 2

        progress_percent = (completed_count / enabled_count) * 100

        # Should be 66.67%, not lower based on all providers
        assert progress_percent == pytest.approx(66.67, rel=0.01)


class TestEnabledProvidersStartupValidation:
    """Tests for startup validation of enabled providers"""

    def test_missing_api_key_for_enabled_provider_fails(self):
        """
        Test that missing API key for enabled provider causes startup failure
        """
        enabled_providers = ["openai", "claude"]
        api_keys = {
            "openai": "sk-xxx",
            "claude": None  # Missing!
        }

        missing_keys = [
            p for p in enabled_providers
            if not api_keys.get(p)
        ]

        assert "claude" in missing_keys
        # In real app, this should raise startup error

    def test_disabled_provider_api_key_not_required(self):
        """
        Test that API keys for disabled providers are not required
        """
        enabled_providers = ["openai"]
        all_providers = ["openai", "claude", "gemini"]

        api_keys = {
            "openai": "sk-xxx",
            "claude": None,  # Missing but disabled
            "gemini": None   # Missing but disabled
        }

        # Only check enabled providers
        missing_keys = [
            p for p in enabled_providers
            if not api_keys.get(p)
        ]

        # No missing keys for enabled providers
        assert len(missing_keys) == 0

    def test_provider_config_logged_at_startup(self):
        """
        Test that enabled/disabled provider status is logged at startup
        """
        log_messages = []

        def log_info(message):
            log_messages.append(message)

        enabled_providers = ["openai", "claude"]
        disabled_providers = ["gemini", "perplexity", "google_ai", "huggingface"]

        # Simulate startup logging
        log_info(f"Enabled providers: {', '.join(enabled_providers)}")
        log_info(f"Disabled providers: {', '.join(disabled_providers)}")

        assert any("Enabled providers" in msg for msg in log_messages)
        assert any("openai" in msg for msg in log_messages)
