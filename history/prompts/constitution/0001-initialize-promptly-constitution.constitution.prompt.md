---
id: 0001
title: Initialize Promptly Constitution
stage: constitution
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: hassan
command: /sp.constitution
labels: ["constitution", "monorepo", "initialization", "repository-structure"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution creation)
---

## Prompt

Repository Structure Rules

This is a monorepo with a single product.

All runnable applications live under /apps.

/apps/api contains the FastAPI backend and owns all business logic.

/apps/web contains the Next.js frontend and owns all UI concerns.

No application code may live at the repo root.

Cross-cutting utilities may live in /packages if introduced later.

## Response snapshot

Created comprehensive constitution v1.0.0 with 7 core principles:

1. **Monorepo Structure (NON-NEGOTIABLE)**: Enforces `/apps/api` (FastAPI backend) and `/apps/web` (Next.js frontend) structure with no root-level application code.

2. **Backend Authority**: All business logic resides in `/apps/api`; frontend delegates to API and handles only UI concerns.

3. **Test-First Development (NON-NEGOTIABLE)**: Mandatory Red-Green-Refactor TDD cycle for all features.

4. **Contract Testing for API Integration**: All API endpoints require contract tests to validate schemas and enable independent frontend/backend development.

5. **Minimal Viable Implementation**: YAGNI principle, no speculative features, complexity must be justified.

6. **Observability and Debuggability**: Structured logging, consistent error schemas, trace-level logging for critical paths.

7. **Versioning and Breaking Changes**: Semantic versioning for API with migration plans and ADR documentation for breaking changes.

Additional sections:
- Repository Structure Constraints: Enforced directory layout with path constraints
- Development Workflow: 5-phase feature development flow (Specify → Plan → Tasks → Implement → Document)
- Governance: Amendment process, constitution supremacy, compliance review requirements

Constitution aligns with existing templates (plan-template.md, spec-template.md, tasks-template.md) and establishes quality gates for all development phases.

## Outcome

- ✅ Impact: Established foundational governance for Promptly monorepo with clear separation between FastAPI backend and Next.js frontend
- 🧪 Tests: N/A (constitutional document)
- 📁 Files: Created `.specify/memory/constitution.md` (v1.0.0, 206 lines)
- 🔁 Next prompts: Ready for feature specification (`/sp.specify`) or planning (`/sp.plan`) commands
- 🧠 Reflection: Constitution provides clear monorepo structure rules and development workflow aligned with Spec-Driven Development methodology

## Evaluation notes (flywheel)

- Failure modes observed: None - initial constitution creation successful
- Graders run and results (PASS/FAIL): Template validation PASS, placeholder resolution PASS, template consistency PASS
- Prompt variant (if applicable): N/A (initial creation)
- Next experiment (smallest change to try): Validate constitution enforcement during first feature planning phase
