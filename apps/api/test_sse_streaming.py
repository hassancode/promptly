#!/usr/bin/env python3
"""
Test script for Phase 6 SSE Streaming

Tests the provider orchestrator and SSE streaming without requiring
a running server. Useful for validating the implementation logic.
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from datetime import datetime
from typing import List, Dict, Any

# Mock database session for testing
class MockDB:
    def __init__(self):
        self.objects = []
        self.committed = False

    def add(self, obj):
        self.objects.append(obj)

    def flush(self):
        # Assign IDs to objects
        for i, obj in enumerate(self.objects):
            if not hasattr(obj, 'id') or obj.id is None:
                obj.id = f"test-id-{i}"

    def commit(self):
        self.committed = True
        self.flush()

    def refresh(self, obj):
        pass

    def query(self, model):
        return MockQuery(self.objects, model)


class MockQuery:
    def __init__(self, objects, model):
        self.objects = objects
        self.model = model
        self.filters = []

    def filter(self, *args):
        # Simple mock - just return self
        return self

    def first(self):
        return None if not self.objects else self.objects[0]

    def all(self):
        return self.objects


# Mock models
class MockAnalysis:
    def __init__(self, id, user_id, brand_name):
        self.id = id
        self.user_id = user_id
        self.brand_name = brand_name
        self.competitors = []


class MockCompetitor:
    def __init__(self, name):
        self.name = name


class MockPrompt:
    def __init__(self, id, analysis_id, text):
        self.id = id
        self.analysis_id = analysis_id
        self.text = text


async def test_provider_orchestrator():
    """Test the provider orchestrator with mock providers"""
    print("=" * 80)
    print("TEST 1: Provider Orchestrator - Concurrent Queries")
    print("=" * 80)

    try:
        from services.provider_orchestrator import ProviderOrchestrator
        from models.analysis import Analysis
        from models.prompt import Prompt
        from models.competitor import Competitor

        # Create mock database
        db = MockDB()

        # Create test data
        analysis = MockAnalysis(
            id="test-analysis-1",
            user_id="test-user-1",
            brand_name="Tesla"
        )
        analysis.competitors = [
            MockCompetitor("Rivian"),
            MockCompetitor("Lucid Motors")
        ]

        prompt = MockPrompt(
            id="test-prompt-1",
            analysis_id="test-analysis-1",
            text="What are the best electric vehicles for long-distance travel?"
        )

        # Initialize orchestrator
        print("\n📊 Initializing Provider Orchestrator...")
        orchestrator = ProviderOrchestrator(db)

        print(f"   Enabled providers: {orchestrator.enabled_providers}")
        print(f"   Total adapters initialized: {len(orchestrator.provider_adapters)}")

        for provider_name in orchestrator.enabled_providers:
            if provider_name in orchestrator.provider_adapters:
                adapter = orchestrator.provider_adapters[provider_name]
                print(f"   ✓ {provider_name}: {adapter.get_model_name()} (citations: {adapter.supports_citations()})")
            else:
                print(f"   ✗ {provider_name}: Not initialized (missing SDK?)")

        # Test concurrent queries
        print("\n🚀 Starting concurrent provider queries...")
        print(f"   Brand: {analysis.brand_name}")
        print(f"   Competitors: {[c.name for c in analysis.competitors]}")
        print(f"   Prompt: {prompt.text}")
        print(f"   Timeout: 30s per provider")

        start_time = datetime.now()

        result = await orchestrator.query_all_providers(
            analysis=analysis,
            prompt=prompt,
            timeout_seconds=30
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n✅ Queries completed in {duration:.2f}s")
        print(f"   Total providers queried: {result['total']}")
        print(f"   Successful: {result['successful']}")
        print(f"   Failed: {result['failed']}")
        print(f"   Responses saved: {len(result['responses'])}")

        print("\n📋 Provider Status:")
        for provider, status in result['provider_statuses'].items():
            emoji = "✅" if status == "success" else "❌"
            print(f"   {emoji} {provider}: {status}")

        # Test progress calculation
        print("\n📈 Testing progress calculation...")
        progress = orchestrator.get_progress("test-analysis-1")
        print(f"   Enabled providers: {progress['enabled_count']}")
        print(f"   Progress: {progress['completed']}/{progress['total']} ({progress['percentage']}%)")

        # Test provider info
        print("\n📊 Provider Information:")
        provider_info = orchestrator.get_provider_info()
        for info in provider_info:
            status = "🟢 Enabled" if info.enabled else "🔴 Disabled"
            citations = "📎" if info.supports_citations else "❌"
            print(f"   {status} {info.name}: {info.model_name} {citations}")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_sse_event_generation():
    """Test SSE event generation logic"""
    print("\n" + "=" * 80)
    print("TEST 2: SSE Event Generation")
    print("=" * 80)

    try:
        from schemas.provider import (
            StreamEvent,
            ProviderStartedEvent,
            ProviderCompletedEvent,
            ProgressUpdateEvent
        )

        print("\n📡 Testing SSE event schemas...")

        # Test provider_started event
        started_event = ProviderStartedEvent(
            provider="openai",
            prompt_id="test-prompt-1",
            timestamp=datetime.now()
        )
        print(f"   ✓ provider_started: {started_event.provider}")

        # Test provider_completed event
        completed_event = ProviderCompletedEvent(
            provider="openai",
            prompt_id="test-prompt-1",
            response_id="test-response-1",
            has_citations=True,
            citation_count=2,
            timestamp=datetime.now()
        )
        print(f"   ✓ provider_completed: {completed_event.provider} ({completed_event.citation_count} citations)")

        # Test progress_update event
        progress_event = ProgressUpdateEvent(
            completed=3,
            total=6,
            percentage=50.0,
            current_provider="claude"
        )
        print(f"   ✓ progress_update: {progress_event.percentage}% ({progress_event.completed}/{progress_event.total})")

        # Test StreamEvent wrapper
        stream_event = StreamEvent(
            event="provider_completed",
            data=completed_event.model_dump()
        )
        print(f"   ✓ StreamEvent: {stream_event.event}")

        print("\n✅ All SSE event schemas validated")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_provider_adapters():
    """Test individual provider adapters"""
    print("\n" + "=" * 80)
    print("TEST 3: Provider Adapters")
    print("=" * 80)

    try:
        from providers.openai_adapter import OpenAIAdapter
        from providers.claude_query_adapter import ClaudeQueryAdapter

        print("\n🔌 Testing OpenAI Adapter...")
        openai = OpenAIAdapter()
        print(f"   Provider: {openai.get_provider_name()}")
        print(f"   Model: {openai.get_model_name()}")
        print(f"   Supports Citations: {openai.supports_citations()}")
        print(f"   API Key Configured: {'Yes' if openai.api_key else 'No (using mock mode)'}")

        # Test query (will use mock mode if no API key)
        print("\n   🚀 Testing query...")
        result = await openai.query(
            prompt="What are the best electric vehicles?",
            brand_name="Tesla",
            competitors=["Rivian", "Lucid Motors"]
        )
        print(f"   ✓ Query result: {result.status}")
        print(f"   ✓ Answer length: {len(result.answer_text.get('text', ''))}")
        print(f"   ✓ Citations: {len(result.citations)}")
        print(f"   ✓ Citation coverage: {result.citation_coverage}")

        print("\n🔌 Testing Claude Adapter...")
        claude = ClaudeQueryAdapter()
        print(f"   Provider: {claude.get_provider_name()}")
        print(f"   Model: {claude.get_model_name()}")
        print(f"   Supports Citations: {claude.supports_citations()}")
        print(f"   API Key Configured: {'Yes' if claude.api_key else 'No (using mock mode)'}")

        # Test query
        print("\n   🚀 Testing query...")
        result = await claude.query(
            prompt="Compare Tesla to Rivian",
            brand_name="Tesla",
            competitors=["Rivian"]
        )
        print(f"   ✓ Query result: {result.status}")
        print(f"   ✓ Answer length: {len(result.answer_text.get('text', ''))}")
        print(f"   ✓ Citations: {len(result.citations)}")

        print("\n✅ All provider adapters working")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("🧪 PHASE 6 SSE STREAMING TEST SUITE")
    print("=" * 80)
    print("\nThis test suite validates the Phase 6 implementation:")
    print("  • Provider Orchestrator (concurrent queries)")
    print("  • Provider Adapters (OpenAI, Claude)")
    print("  • SSE Event Generation")
    print("  • Progress Tracking")
    print("=" * 80)

    results = []

    # Run tests
    results.append(("Provider Adapters", await test_provider_adapters()))
    results.append(("SSE Event Generation", await test_sse_event_generation()))
    results.append(("Provider Orchestrator", await test_provider_orchestrator()))

    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Phase 6 core infrastructure is working.")
        print("\n📝 Next steps:")
        print("  1. Apply database migration: poetry run alembic upgrade head")
        print("  2. Start API server: poetry run uvicorn src.main:app --reload")
        print("  3. Test SSE endpoint: curl -N http://localhost:8000/api/v1/analyses/{id}/stream")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")

    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
