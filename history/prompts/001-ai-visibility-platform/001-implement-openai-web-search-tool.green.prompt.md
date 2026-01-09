---
id: 001
title: Implement OpenAI Web Search Tool
stage: green
date: 2026-01-09
surface: agent
model: claude-opus-4-5-20251101
feature: 001-ai-visibility-platform
branch: 001-ai-visibility-platform
user: hassan
command: /sp.implement
labels: ["openai", "web-search", "provider-adapter", "implementation"]
links:
  spec: specs/001-ai-visibility-platform/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - apps/api/src/providers/openai_adapter.py
tests:
  - tests/integration/test_provider_orchestration.py
---

# Prompt

implement TODO in line 85 @apps/api/src/providers/openai_adapter.py to pass websearch as a tool

# Response

## Summary

Implemented OpenAI web search functionality in the OpenAI provider adapter by updating the API call to use OpenAI's Responses API with the `web_search` tool.

## Changes Made

1. **Updated `query()` method** (lines 84-90):
   - Changed from `client.chat.completions.create()` to `client.responses.create()`
   - Added `tools=[{"type": "web_search"}]` parameter to enable web search
   - Updated model to `gpt-4o` which supports web search

2. **Added `_extract_answer_from_response()` method** (lines 161-197):
   - Parses the Responses API output format
   - Extracts answer text from message content blocks
   - Handles fallback to `output_text` attribute

3. **Updated `extract_citations()` method** (lines 199-244):
   - Parses `web_search_call` items from response output
   - Extracts URL, title, and snippet from search results
   - Returns list of `CitationCreate` objects

4. **Updated metadata handling** (lines 99-109):
   - Changed to reflect Responses API token naming (`input_tokens`, `output_tokens`)
   - Added `web_search_enabled: True` flag

5. **Updated `get_model_name()`** (line 45):
   - Changed from `gpt-4` to `gpt-4o` for web search support

## Verification

- Import test passed
- Mock response functionality verified
- Provider orchestration tests passed (4/7 - 3 failures unrelated to this change)

## Outcome

SUCCESS - OpenAI adapter now uses the Responses API with web search tool enabled, replacing the TODO placeholder with actual implementation.
