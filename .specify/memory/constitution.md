<!--
Sync Impact Report:
Version change: [NEW] → 1.0.0
Rationale: Initial constitution creation with monorepo-specific principles
Added sections:
  - Core Principles (7 principles)
  - Repository Structure Constraints
  - Development Workflow
  - Governance
Templates updated:
  ✅ plan-template.md - Constitution Check section aligns with principles
  ✅ spec-template.md - Requirements alignment verified
  ✅ tasks-template.md - Task categorization aligns with principles
Follow-up TODOs: None - all placeholders filled
-->

# Promptly Constitution

## Core Principles

### I. Monorepo Structure (NON-NEGOTIABLE)

**Rules:**
- This is a monorepo with a single product
- All runnable applications MUST live under `/apps`
- `/apps/api` contains the FastAPI backend and owns ALL business logic
- `/apps/web` contains the Next.js frontend and owns ALL UI concerns
- NO application code may live at the repository root
- Cross-cutting utilities MAY live in `/packages` if introduced later

**Rationale:** Clear separation of concerns between frontend and backend prevents architectural drift and ensures each application has a well-defined boundary. Root-level application code creates ambiguity about ownership and complicates build tooling.

### II. Backend Authority

**Rules:**
- All business logic, data validation, and domain rules MUST reside in `/apps/api`
- The backend is the authoritative source for all data models and business workflows
- The frontend MUST NOT implement business logic; it orchestrates user interactions and delegates to the API
- API contracts define the interface between frontend and backend

**Rationale:** Business logic duplication between frontend and backend creates maintenance burden and inconsistency. Centralizing business logic in the backend ensures a single source of truth and enables other clients (mobile, CLI, webhooks) to leverage the same logic.

### III. Test-First Development (NON-NEGOTIABLE)

**Rules:**
- Tests MUST be written before implementation code
- Tests MUST fail before implementation begins
- Red-Green-Refactor cycle is mandatory:
  1. **Red**: Write failing test
  2. **Green**: Write minimal code to pass
  3. **Refactor**: Improve without breaking tests
- No feature is complete without corresponding tests

**Rationale:** Test-first development ensures requirements are clear, prevents over-engineering, and provides immediate feedback. Skipping this step leads to untestable code and regression risk.

### IV. Contract Testing for API Integration

**Rules:**
- All API endpoints MUST have contract tests
- Contract tests validate request/response schemas, status codes, and error formats
- Changes to API contracts require contract test updates BEFORE implementation
- Frontend and backend contract tests must remain in sync

**Rationale:** API contract tests serve as executable documentation and catch breaking changes early. They enable frontend and backend teams to work independently with confidence.

### V. Minimal Viable Implementation

**Rules:**
- Implement ONLY what is specified; no speculative features
- Start with the simplest solution that satisfies requirements
- YAGNI (You Aren't Gonna Need It) principle applies
- Premature abstraction is prohibited
- Complexity must be justified in the implementation plan

**Rationale:** Overengineering wastes time, increases maintenance burden, and introduces bugs. Simple solutions are easier to understand, test, and modify. Complexity should emerge from real needs, not anticipated ones.

### VI. Observability and Debuggability

**Rules:**
- All business operations MUST emit structured logs
- Errors MUST include context (request ID, user ID, operation, timestamp)
- API responses MUST use consistent error schemas with actionable messages
- Critical paths (auth, payments, data mutations) require trace-level logging

**Rationale:** Production debugging without observability is impossible. Structured logging and error handling reduce mean time to resolution (MTTR) and improve system reliability.

### VII. Versioning and Breaking Changes

**Rules:**
- API versioning follows semantic versioning: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes (incompatible API changes)
- MINOR: New features (backward-compatible)
- PATCH: Bug fixes (backward-compatible)
- Breaking changes require migration plan and deprecation notice
- API version changes must be documented in ADRs

**Rationale:** Clear versioning prevents accidental breakage and sets user expectations. Migration plans reduce deployment risk and enable graceful transitions.

## Repository Structure Constraints

### Enforced Directory Layout

```text
/apps/
  api/              # FastAPI backend (business logic authority)
  web/              # Next.js frontend (UI concerns only)

/packages/          # Shared utilities (optional, introduce only when needed)

/specs/             # Feature specifications (SDD artifacts)
  [###-feature]/
    spec.md
    plan.md
    tasks.md
    research.md
    data-model.md
    contracts/

/history/           # Prompt History Records & ADRs
  prompts/
    constitution/
    general/
    [feature-name]/
  adr/

/.specify/          # SDD templates and tooling
  memory/
    constitution.md # This file
  templates/
  scripts/
```

### Path Constraints

- Application code in `/apps/api` or `/apps/web` ONLY
- Shared code in `/packages` ONLY if cross-cutting (not app-specific)
- Root-level code prohibited (except configuration files)
- Each app manages its own dependencies and build tooling

## Development Workflow

### Feature Development Flow

1. **Specification Phase** (`/sp.specify`)
   - Define user stories with acceptance criteria
   - Identify functional requirements
   - Clarify edge cases and constraints

2. **Planning Phase** (`/sp.plan`)
   - Conduct technical research
   - Design data models and API contracts
   - Identify architectural decisions → suggest ADRs
   - Define implementation phases

3. **Task Generation** (`/sp.tasks`)
   - Break plan into testable, independent tasks
   - Organize by user story for incremental delivery
   - Mark parallelizable tasks
   - Define dependencies and execution order

4. **Implementation Phase** (`/sp.implement`)
   - Execute tasks in dependency order
   - Follow Red-Green-Refactor for each task
   - Commit after each task or logical group
   - Validate at checkpoints

5. **Documentation Phase**
   - Update relevant specs with actual implementation details
   - Create ADRs for significant decisions
   - Capture PHRs for all user interactions

### Quality Gates

- **Pre-Planning Gate**: Constitution compliance check
- **Pre-Implementation Gate**: Plan approval, ADRs for significant decisions
- **Per-Task Gate**: Tests written and failing before code
- **Pre-Commit Gate**: All tests passing, linting clean
- **Pre-Deploy Gate**: Integration tests passing, quickstart validated

## Governance

### Amendment Process

1. Proposed changes must be documented with rationale
2. Impact analysis on existing templates and workflows required
3. Sync Impact Report generated for all affected artifacts
4. Version bump according to semantic versioning
5. All dependent templates updated before ratification

### Constitution Supremacy

- This constitution supersedes all other development practices
- All code reviews, PRs, and planning must verify constitutional compliance
- Violations require explicit justification and complexity tracking
- CLAUDE.md (agent guidance) references this constitution for enforcement

### Version History

**Version**: 1.0.0 | **Ratified**: 2026-01-06 | **Last Amended**: 2026-01-06

### Compliance Review

- Constitution review at start of each planning phase (automatic via `/sp.plan`)
- Quarterly review of adherence and effectiveness
- Violations tracked in `plan.md` Complexity Tracking section with justifications
