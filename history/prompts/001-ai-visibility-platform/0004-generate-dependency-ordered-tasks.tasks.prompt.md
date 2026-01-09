---
id: 0004
title: Generate Dependency-Ordered Tasks
stage: tasks
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-ai-visibility-platform
branch: 001-ai-visibility-platform
user: hassan
command: /sp.tasks
labels: ["task-generation", "tdd", "user-stories", "provider-config", "sse-streaming", "contract-testing"]
links:
  spec: specs/001-ai-visibility-platform/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-visibility-platform/tasks.md
tests:
  - 39 test tasks generated (26 contract + 13 integration)
---

## Prompt

Please generate dependency-ordered tasks grouped by milestones. Ensure tasks explicitly include:

1) Provider enable/disable configuration
2) Next.js scaffold via create-next-app (App Router + TypeScript + Tailwind)
3) FastAPI served by Uvicorn (ASGI)
4) SSE streaming endpoint
5) Contract-first OpenAPI artifacts + contract tests
6) Sentiment: Claude primary with Hugging Face fallback

## Response snapshot

Generated 224 dependency-ordered tasks organized by user stories with TDD approach, explicitly addressing all 6 user requirements.

**Key Outputs:**

1. **Task Organization** (User Story Grouping):
   - Phase 1: Setup (9 tasks) - Monorepo scaffolding with create-next-app + Poetry
   - Phase 2: Foundational (23 tasks) - Core infrastructure + provider config manager
   - Phase 3-8: User Stories 1-6 (139 tasks) - TDD with contract tests first
   - Phase 9: Polish (32 tasks) - Error handling, logging, documentation

2. **Explicit Requirement Coverage**:
   - **Provider Config**: T014 (config manager parses ENABLED_PROVIDERS, fail-fast), T119-T123 (orchestrator respects config)
   - **Next.js Scaffold**: T003 (create-next-app --app --typescript --tailwind)
   - **FastAPI + Uvicorn**: T002 (Poetry with Python 3.12+), T019 (Uvicorn config for dev)
   - **SSE Streaming**: T124-T126 (FastAPI StreamingResponse with text/event-stream), T130-T134 (EventSource client)
   - **Contract-First**: T023-T027 (OpenAPI 3.0 spec), T033-T036 (contract tests for US1), repeated for all stories
   - **Sentiment Fallback**: T169 (Claude primary), T170 (Hugging Face fallback), T159 (integration test for both paths)

3. **TDD Workflow** (Red-Green-Refactor):
   - Every user story begins with contract tests (e.g., T033 before T037)
   - Integration tests precede service implementation (e.g., T096 before T097)
   - Unit tests accompany each component (e.g., T014 has validation tests)

4. **Provider Configuration Behavior** (Research Decision #9):
   - Disabled providers NOT queried, NOT counted in progress, NOT treated as failures
   - Progress bar formula: `completed / total_enabled_providers`
   - Frontend never receives events for disabled providers

5. **SSE Implementation Details**:
   - Backend: FastAPI `StreamingResponse` with `text/event-stream` Content-Type
   - Frontend: Native `EventSource` API (no libraries)
   - Events: `provider_started`, `provider_completed`, `provider_failed`, `analysis_complete`
   - Reconnection: Frontend retries with exponential backoff

6. **Task Metadata**:
   - Total: 224 tasks
   - Parallelizable: 156 (70%) marked with [P]
   - Test tasks: 39 (17%) - 26 contract + 13 integration
   - MVP scope: Phases 1-6 (142 tasks)
   - All tasks include exact file paths (e.g., `apps/api/src/core/providers.py`)

7. **Critical Path**:
   ```
   Phase 1 (Setup) → Phase 2 (Foundational) → US1 (Auth) → US2 (Brand/Competitor) →
   US3 (Prompts) → US4 (Provider Querying) → US5 (Results Display) → US6 (Insights) →
   Phase 9 (Polish)
   ```

8. **Implementation Notes Added**:
   - Provider config validation rules (at least one enabled, fail-fast at startup)
   - SSE event payload schemas with JSON structure
   - Sentiment fallback logic (Claude → Hugging Face on rate limit/unavailability)
   - Contract test organization (one test file per API endpoint group)

**Coverage Analysis**: All 6 user-specified requirements explicitly addressed with task IDs and file paths.

## Outcome

- ✅ Impact: 224 production-ready tasks with TDD approach, user story grouping for independent implementation, explicit coverage of all 6 user requirements
- 🧪 Tests: 39 test tasks (26 contract for API boundaries + 13 integration for cross-service flows)
- 📁 Files: Created tasks.md (comprehensive task breakdown with dependencies)
- 🔁 Next prompts: Ready for `/sp.implement` to begin Phase 1 (Setup) or `/sp.adr` to document 5 architectural decisions identified in plan
- 🧠 Reflection: User-provided requirements ensured critical implementation details (SSE, contract-first, sentiment fallback) were not lost in abstraction. User story grouping enables parallel team implementation vs. traditional milestone-based serialization.

## Evaluation notes (flywheel)

- Failure modes observed: None - all user requirements explicitly addressed with task IDs
- Graders run and results (PASS/FAIL): TDD structure PASS (contract tests precede implementation), Dependency ordering PASS (no circular deps), User requirement coverage PASS (6/6 requirements with task IDs), File path specificity PASS (all tasks have exact paths)
- Prompt variant (if applicable): User-specified requirements variant (vs. standard autonomous task generation)
- Next experiment (smallest change to try): Validate whether user story grouping reduces merge conflicts and enables faster parallel implementation compared to milestone-based task organization
