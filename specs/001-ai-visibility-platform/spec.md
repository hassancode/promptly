# Feature Specification: AI Search Visibility & Competitive Insight Platform

**Feature Branch**: `001-ai-visibility-platform`
**Created**: 2026-01-06
**Status**: Draft
**Input**: User description: "Promptly — AI Search Visibility & Competitive Insight Platform"

## Clarifications

### Session 2026-01-06

- Q: How is visibility/prominence calculated and scored? → A: Composite score combining presence (mentioned/not), frequency (mentions vs competitors), and position/emphasis (early mentions weighted higher), calculated per prompt/provider then aggregated and normalized
- Q: How is sentiment evaluated for brand mentions? → A: LLM-based classification with strict rubric (Positive/Neutral/Negative), assigned per mention, ambiguous defaults to Neutral, aggregated by majority across prompts/providers, must reference underlying AI response
- Q: When and how are insights generated? → A: Two-phase synchronous model—AI querying shows incremental results, then user explicitly triggers "Get Insights" which runs synchronously, users can retry insights without re-querying providers
- Q: How is user location determined and used? → A: Server-side IP geolocation at analysis start, country-level granularity, fixed for entire analysis, defaults to global if cannot determine, displayed to user for transparency
- Q: What are citation coverage expectations and confidence levels? → A: Analysis valid if ≥1 provider returns citations; confidence levels: High (multiple citations), Medium (≥1 citation), Low (no citations); missing/broken citations marked and displayed
- Q: How are provider capability differences handled? → A: All providers contribute equally to visibility/sentiment/themes; citation capability affects confidence only (not inclusion); differences surfaced via metadata/UI indicators; no implicit ranking
- Q: What constitutes a successful analysis with partial failures? → A: Success if ≥1 provider returns usable response; failures visible and non-blocking; users can retry failed providers only; insights proceed with available data; confidence reflects partial coverage
- Q: How are ambiguous brand names resolved? → A: Infer context from competitors and prompts first; prompt user disambiguation only if ambiguity remains high after provider responses show conflicting interpretations; applied context shown to user and used consistently
- Q: What prompt quality guardrails are enforced? → A: Block empty, nonsensical, unsafe, or malicious prompts; allow low-quality with guidance; prompts sent unchanged to all providers; brand context and location applied outside user prompt
- Q: How are insights made explainable and traceable? → A: Every insight includes summary, explanation, and evidence (AI responses/citations); insights without citations marked lower confidence; no insight shown without explanation
- Q: What is the data retention and report lifecycle policy? → A: Reports retained indefinitely until user deletion; soft delete for MVP; deleted reports hidden from UI and analysis; no automatic expiration or archival

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration and Dashboard Access (Priority: P1)

A brand manager visits Promptly to understand their AI visibility. They need to create an account and access the platform to begin their first analysis.

**Why this priority**: Without user registration and authentication, no other features are accessible. This is the foundation for all user interactions and enables personalized, secure access to analysis data.

**Independent Test**: Can be fully tested by completing sign-up flow, receiving verification, logging in, and landing on an empty dashboard. Delivers immediate value by providing authenticated access to the platform.

**Acceptance Scenarios**:

1. **Given** a new visitor on the landing page, **When** they click Sign Up and complete registration with valid email and password, **Then** they receive a verification email and can verify their account
2. **Given** a verified user, **When** they log in with correct credentials, **Then** they are redirected to the Dashboard
3. **Given** an unverified user, **When** they attempt to log in, **Then** they see a message to verify their email first
4. **Given** a user enters invalid credentials, **When** they attempt to log in, **Then** they see an error message with actionable guidance

---

### User Story 2 - Brand and Competitor Setup (Priority: P2)

A user on the dashboard wants to analyze their brand against competitors. They need to specify their brand name and select relevant competitors to compare against.

**Why this priority**: This is the first step in the analysis flow and sets the context for all AI queries. Without brand and competitor selection, no meaningful analysis can occur.

**Independent Test**: Can be fully tested by entering a brand name, reviewing AI-suggested competitors (up to 3), optionally adding custom competitors (up to 2 more), and confirming selections. Delivers value by establishing the competitive landscape for analysis.

**Acceptance Scenarios**:

1. **Given** a logged-in user on the dashboard, **When** they click Start Analysis and enter a brand name, **Then** the system suggests up to 3 competitor brands using AI
2. **Given** the system has suggested competitors, **When** the user reviews suggestions, **Then** they can accept, reject, or add up to 2 additional custom competitors
3. **Given** the user has selected a brand and at least one competitor, **When** they confirm selections, **Then** they proceed to prompt selection
4. **Given** the user enters an invalid or empty brand name, **When** they attempt to proceed, **Then** they see validation guidance
5. **Given** a brand name is ambiguous, **When** AI providers return conflicting interpretations, **Then** the user is prompted to disambiguate and the applied context is shown and used consistently

---

### User Story 3 - Analysis Prompt Configuration (Priority: P3)

A user with brand and competitors selected needs to define the questions (prompts) that will be sent to AI systems to understand how their brand is represented.

**Why this priority**: Prompts determine what insights are gathered. Good prompts reveal visibility, sentiment, and competitive positioning in AI responses.

**Independent Test**: Can be fully tested by reviewing AI-suggested prompts (up to 5), optionally adding custom prompts (up to 2 more), confirming selections, and initiating analysis. Delivers value by allowing users to customize the analysis scope to their specific concerns.

**Acceptance Scenarios**:

1. **Given** a user has confirmed brand and competitors, **When** they reach prompt selection, **Then** the system suggests up to 5 natural-language prompts relevant to the brand
2. **Given** the system has suggested prompts, **When** the user reviews them, **Then** they can accept, edit, or add up to 2 additional custom prompts
3. **Given** the user has selected at least one prompt, **When** they confirm and start analysis, **Then** the system begins querying AI systems with location-aware context
4. **Given** the user adds a custom prompt, **When** the prompt is empty, nonsensical, unsafe, or malicious, **Then** the system blocks it with clear guidance
5. **Given** the user adds a low-quality prompt, **When** validation runs, **Then** the system allows it with guidance for improvement
6. **Given** prompts are sent to AI providers, **When** queries are executed, **Then** brand context and location are applied outside the user prompt and prompts are sent unchanged

---

### User Story 4 - Multi-Provider AI Querying and Citation Collection (Priority: P4)

The system needs to query multiple AI providers (OpenAI, Google Gemini, Anthropic Claude, Perplexity, Google AI Search) with the selected prompts, collect answers and citations, and handle partial failures gracefully.

**Why this priority**: This is the core data collection capability that distinguishes Promptly from traditional SEO tools. It gathers the raw material for competitive insights.

**Independent Test**: Can be fully tested by triggering analysis with configured brand, competitors, and prompts, then verifying that responses and citations are collected from available providers. Delivers value by providing location-aware AI responses with citation evidence.

**Acceptance Scenarios**:

1. **Given** a user has started analysis, **When** the system queries AI providers, **Then** it collects answer text, citations (URLs, titles, snippets), and provider metadata from each available provider
2. **Given** an AI provider supports web-search or citation tools, **When** the system queries that provider, **Then** it enables those tools to maximize citation availability
3. **Given** one or more AI providers fail or timeout, **When** the system completes querying, **Then** partial results are still returned, failures are clearly marked visible and non-blocking, and analysis succeeds if at least one provider returns usable response
4. **Given** an AI provider returns answers without citations, **When** results are collected, **Then** citation coverage is explicitly marked as incomplete for that provider and contributes equally to analysis with lower confidence
5. **Given** the system queries AI providers, **When** the user's location is determined at analysis start via server-side IP geolocation (country-level), **Then** all queries include location context fixed for entire analysis and effective location is displayed to user
6. **Given** location cannot be determined, **When** analysis starts, **Then** global context is used as fallback

---

### User Story 5 - AI Response Exploration and Citation Review (Priority: P5)

A user whose analysis has completed needs to review the raw AI responses and citations before requesting insights, to understand what data was collected.

**Why this priority**: Transparency in data collection builds trust and allows users to verify that responses are relevant and complete before investing time in insights.

**Independent Test**: Can be fully tested by viewing collected AI responses in a clear, comparable format with citations displayed alongside answers. Delivers value by providing visibility into the raw data that will inform insights.

**Acceptance Scenarios**:

1. **Given** analysis has completed, **When** the user views results, **Then** they see AI responses organized by provider and prompt with citations clearly linked
2. **Given** multiple providers returned responses, **When** the user explores results, **Then** they can compare responses across providers for the same prompt
3. **Given** a provider failed or returned incomplete citations, **When** the user views results, **Then** they see clear indicators of data quality, coverage, and provider capability differences via metadata/UI indicators with no implicit provider ranking
4. **Given** citations are available, **When** the user clicks a citation, **Then** they can view the source URL, title, and snippet (if available)
5. **Given** citations are missing or broken, **When** displayed, **Then** they are marked as such with confidence level (High: multiple citations, Medium: ≥1 citation, Low: no citations)
6. **Given** failed providers exist, **When** user views results, **Then** user can retry only the failed providers without re-running successful ones

---

### User Story 6 - Competitive Insights and Recommendations (Priority: P6)

A user who has reviewed AI responses wants to understand how their brand compares to competitors across all collected data and receive actionable recommendations for improvement.

**Why this priority**: This is the ultimate value delivery—transforming raw AI responses into strategic insights and actions that improve brand visibility in AI systems.

**Independent Test**: Can be fully tested by clicking Get Insights after analysis completion, then reviewing brand vs competitor comparison with mentions, visibility, sentiment, themes, gaps, and at least 5 actionable recommendations. Delivers value by providing strategic guidance based on evidence.

**Acceptance Scenarios**:

1. **Given** a user clicks Get Insights, **When** insight generation runs synchronously, **Then** they see a summary comparing their brand against competitors across all AI responses
2. **Given** insights are generated, **When** the user reviews them, **Then** they see mention frequency, visibility/prominence scores (composite of presence + frequency + position with early mentions weighted higher, calculated per prompt/provider then aggregated and normalized), and sentiment indicators (Positive/Neutral/Negative via LLM classification with strict rubric)
3. **Given** sentiment is assigned, **When** mentions are ambiguous or mixed, **Then** sentiment defaults to Neutral and is aggregated by majority across prompts/providers
4. **Given** insights include findings, **When** the user explores them, **Then** each insight includes summary, explanation, and evidence (AI responses/citations) with no insight shown without explanation
5. **Given** insights are complete, **When** the user views recommendations, **Then** they see at least 5 actionable recommendations with clear rationale, expected impact, and evidence references
6. **Given** insights reference key themes or gaps, **When** the user reviews them, **Then** they understand what topics their brand is associated with and where they're absent
7. **Given** insights have varying citation support, **When** displayed, **Then** confidence levels are shown (High/Medium/Low) and insights without citations are marked lower confidence
8. **Given** insight generation completes, **When** user wants to retry, **Then** they can re-run insight generation without re-querying AI providers

---

### Edge Cases

- What happens when all AI providers fail to return responses? (Analysis fails; user notified to retry)
- How does the system handle a brand name that is ambiguous or has multiple meanings? (Infer from competitors/prompts; prompt disambiguation if high ambiguity remains)
- What happens when a user selects 5 competitors but only 3 return meaningful results? (Analysis proceeds with available data; confidence reflects partial coverage)
- How does the system behave when a prompt is too generic or too specific to yield useful results? (Allow with guidance for low-quality; insights reflect actual provider responses)
- What happens when citation URLs are broken or inaccessible? (Marked as broken; displayed with lower confidence indicator)
- How does the system handle rate limits or quota exhaustion from AI providers? (Treated as provider failure; visible and non-blocking; can retry)
- What happens when a user's location cannot be determined? (Defaults to global context; displayed to user)
- How does the system handle very long AI responses that may impact UI rendering? (Truncate with "show more" or pagination; full text available on demand)
- What happens when two competitors have identical names? (Context inference and disambiguation prompt if needed)
- How does the system handle prompt injection attempts or malicious input? (Blocked by prompt validation; brand context/location applied outside user prompt)

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication & User Management

- **FR-001**: System MUST allow users to register with email and password
- **FR-002**: System MUST send verification emails to new users and require email verification before login
- **FR-003**: System MUST authenticate users via session-based authentication with secure password hashing
- **FR-004**: System MUST provide a login flow that redirects verified users to the Dashboard
- **FR-005**: System MUST prevent unverified users from accessing protected features
- **FR-006**: System MUST associate all analysis data with the owning user and prevent cross-user data access

#### Brand & Competitor Configuration

- **FR-007**: System MUST accept a brand name as the primary subject of analysis
- **FR-008**: System MUST use an LLM to suggest up to 3 relevant competitor brands based on the entered brand name
- **FR-009**: System MUST allow users to add up to 2 additional custom competitor brands beyond AI suggestions
- **FR-010**: System MUST validate that brand and competitor names are non-empty and meet reasonable length constraints
- **FR-011**: System MUST infer brand context from competitors and prompts when brand name is ambiguous
- **FR-012**: System MUST prompt user for disambiguation when AI providers return conflicting brand interpretations after context inference
- **FR-013**: System MUST display applied brand context to user and use it consistently throughout analysis

#### Prompt Selection & Customization

- **FR-014**: System MUST use an LLM to suggest up to 5 natural-language prompts relevant to the brand and industry
- **FR-015**: System MUST allow users to add up to 2 additional custom prompts beyond AI suggestions
- **FR-016**: System MUST validate prompts and block empty, nonsensical, unsafe, or malicious inputs with clear guidance
- **FR-017**: System MUST allow low-quality prompts with improvement guidance
- **FR-018**: System MUST send user prompts unchanged to all AI providers
- **FR-019**: System MUST apply brand context and location outside the user prompt when querying providers
- **FR-020**: System MUST allow users to edit or remove suggested prompts before analysis

#### Location-Aware AI Querying

- **FR-021**: System MUST determine user location at analysis start using server-side IP geolocation with country-level granularity
- **FR-022**: System MUST fix location for the entire analysis session once determined
- **FR-023**: System MUST use global context as fallback when location cannot be determined
- **FR-024**: System MUST display effective location to user for transparency
- **FR-025**: System MUST include location context in all AI queries to ensure responses reflect regional relevance
- **FR-026**: System MUST query multiple AI providers: OpenAI, Google Gemini, Anthropic Claude, Perplexity, and Google AI Search/AI Overview (where supported)
- **FR-027**: System MUST enable web-search or citation-generating tools for AI providers that support them
- **FR-028**: System MUST collect answer text, citations (URLs, titles, snippets when available), and provider metadata from each AI response
- **FR-029**: System MUST handle partial provider failures as visible and non-blocking events
- **FR-030**: System MUST consider analysis successful if at least one provider returns a usable response
- **FR-031**: System MUST allow users to retry only failed providers without re-running successful ones
- **FR-032**: System MUST normalize AI responses into a consistent format for frontend consumption

#### Citation & Evidence Management

- **FR-033**: System MUST preserve all citations returned by AI providers, including URLs, titles, and snippets
- **FR-034**: System MUST link citations to their corresponding AI responses and prompts
- **FR-035**: System MUST mark missing or broken citations explicitly
- **FR-036**: System MUST assign confidence levels based on citation coverage: High (multiple citations), Medium (≥1 citation), Low (no citations)
- **FR-037**: System MUST include providers without citations in analysis with equal contribution but lower confidence
- **FR-038**: System MUST display provider capability differences via metadata and UI indicators without implicit ranking

#### Insights Generation

- **FR-039**: System MUST trigger insight generation explicitly via user action ("Get Insights")
- **FR-040**: System MUST run insight generation synchronously for MVP
- **FR-041**: System MUST allow users to retry insight generation without re-querying AI providers
- **FR-042**: System MUST analyze brand vs competitors across all collected AI responses
- **FR-043**: System MUST calculate mention frequency for the brand and each competitor
- **FR-044**: System MUST derive visibility/prominence scores as composite of presence (mentioned/not), frequency (mentions vs competitors), and position/emphasis (early mentions weighted higher)
- **FR-045**: System MUST calculate visibility scores per prompt and per provider, then aggregate and normalize for comparison
- **FR-046**: System MUST evaluate sentiment using LLM-based classification with strict rubric (Positive/Neutral/Negative)
- **FR-047**: System MUST assign sentiment per brand mention and default ambiguous or mixed sentiment to Neutral
- **FR-048**: System MUST aggregate sentiment by majority across prompts, providers, and overall
- **FR-049**: System MUST reference underlying AI response (and citation if available) for every sentiment result
- **FR-050**: System MUST identify key themes and gaps in brand representation across AI responses
- **FR-051**: System MUST generate at least 5 actionable recommendations to improve brand presence in AI systems
- **FR-052**: System MUST ensure every insight includes summary, explanation, and evidence (AI responses/citations)
- **FR-053**: System MUST mark insights without citations as lower confidence
- **FR-054**: System MUST never show an insight without an explanation
- **FR-055**: System MUST present insights in a summary format with drill-down capabilities
- **FR-056**: System MUST reflect partial provider coverage in confidence levels

#### Data Privacy & Security

- **FR-057**: System MUST never expose AI provider API keys to the client
- **FR-058**: System MUST ensure analysis data is accessible only to the owning user
- **FR-059**: System MUST exclude sensitive user data and provider credentials from logs
- **FR-060**: System MUST use HTTPS for all client-server communication

#### Data Retention & Lifecycle

- **FR-061**: System MUST retain analysis reports indefinitely until user deletion
- **FR-062**: System MUST implement soft delete for MVP
- **FR-063**: System MUST hide deleted reports from UI and analysis views
- **FR-064**: System MUST NOT automatically expire or archive reports

#### Incremental Results & Progress

- **FR-065**: System MUST display AI provider querying progress incrementally as results become available
- **FR-066**: System MUST allow users to explore partial results while analysis is still in progress
- **FR-067**: System MUST clearly indicate when analysis is complete vs in-progress

### Key Entities

- **User**: Represents a registered user with email, password hash, verification status, and location context. Owns all analyses they create.

- **Analysis**: Represents a single competitive analysis session with a brand name, brand context (for disambiguation), selected competitors, selected prompts, location (country-level, fixed at start), and analysis status (in-progress, completed, failed).

- **Brand**: Represents the primary subject of analysis with a name and optional disambiguation context. Can also represent a competitor in the same analysis.

- **Prompt**: Represents a natural-language question to be sent to AI systems. Can be AI-suggested or user-provided. Linked to an analysis. Validated for safety but sent unchanged to providers.

- **AI Response**: Represents an answer from a single AI provider for a specific prompt. Contains answer text, provider metadata (name, model, capability flags), timestamp, citation coverage status, and failure indicators. Linked to a prompt and analysis.

- **Citation**: Represents a source referenced in an AI response. Contains URL, title, snippet (optional), source type, and validity status (broken/valid). Linked to an AI response.

- **Insight**: Represents a derived finding from analysis of AI responses. Contains mention counts, visibility scores (composite with per-prompt/provider breakdown), sentiment indicators (Positive/Neutral/Negative with aggregation), themes, gaps, confidence level (High/Medium/Low), summary, explanation, and evidence references. Linked to an analysis and references AI responses and citations as evidence.

- **Recommendation**: Represents an actionable suggestion for improving brand presence in AI systems. Contains recommendation text, rationale, expected impact, confidence level, and evidence references (AI responses/citations). Linked to an analysis.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the full flow from sign-up to insights in under 10 minutes for a standard analysis (1 brand, 3 competitors, 5 prompts)
- **SC-002**: System successfully returns responses from at least one AI provider for 95% of analyses
- **SC-003**: At least one AI provider returns citations for 80% of analyses
- **SC-004**: Insights screen includes brand vs competitor comparison with mentions, visibility, and sentiment indicators for 100% of completed analyses
- **SC-005**: System generates a minimum of 5 actionable recommendations for 100% of completed analyses
- **SC-006**: Location context materially influences AI responses in at least 70% of analyses (verified by comparing responses across different locations)
- **SC-007**: Partial provider failures do not block analysis completion in 100% of cases where at least one provider succeeds
- **SC-008**: Users can view incremental results as they become available for 100% of analyses
- **SC-009**: All insights and recommendations are linked to specific evidence (AI responses or citations) in 100% of cases
- **SC-010**: Analysis data is accessible only to the owning user with 100% enforcement
- **SC-011**: Every insight includes summary, explanation, and evidence with no insight shown without explanation in 100% of cases
- **SC-012**: Confidence levels (High/Medium/Low) are displayed based on citation coverage for 100% of insights
- **SC-013**: Ambiguous brand names are successfully disambiguated via context inference or user prompt in 90% of cases
- **SC-014**: Malicious or unsafe prompts are blocked in 100% of cases with clear guidance

## Assumptions *(optional)*

### Technical Assumptions

- Users have modern web browsers with JavaScript enabled
- AI providers have sufficient API quotas to handle expected query volumes
- IP geolocation services are available and provide reasonable country-level accuracy for regional context
- Email delivery services are reliable for verification emails

### Business Assumptions

- Users understand the concept of competitive analysis and brand visibility
- Users can articulate their brand name and recognize their primary competitors
- Free trial period is sufficient to demonstrate value (specific duration not specified)
- No billing or subscription infrastructure is required for MVP

### User Experience Assumptions

- Users are willing to wait for multi-provider AI queries to complete (estimated 10-30 seconds with incremental results)
- Users prefer transparency (seeing partial results and failures) over hiding complexity
- Users value evidence-backed insights over unsupported claims
- Dashboard is the primary entry point after login (no additional landing pages)
- Users will explicitly trigger insight generation after reviewing raw AI responses

### Location Determination

- Default location determination uses server-side IP geolocation at analysis start
- Country-level granularity is sufficient for MVP
- Users may want to override location in future iterations, but MVP uses automatic detection only
- Location is determined once and remains fixed for the entire analysis session
- Global context fallback is acceptable when location cannot be determined

### Visibility & Sentiment Calculation

- Visibility is a composite score combining presence (mentioned/not), frequency (mentions relative to competitors), and position/emphasis (early mentions weighted higher)
- Visibility is calculated per prompt and per provider, then aggregated and normalized
- Sentiment is evaluated using LLM-based classification with a strict rubric (Positive/Neutral/Negative)
- Sentiment is assigned per brand mention with ambiguous or mixed sentiment defaulting to Neutral
- Sentiment is aggregated by majority across prompts, providers, and overall analysis

### Insight Generation

- Insights are generated synchronously after user explicitly clicks "Get Insights"
- Insight generation runs synchronously for MVP (no background jobs)
- Users can retry insight generation without re-querying AI providers
- Every insight must include summary, explanation, and evidence (AI responses and/or citations)
- Insights without citations are allowed but marked with lower confidence

### Data Retention

- Analysis reports are retained indefinitely until user deletion
- Soft delete is used for MVP (reports hidden but not immediately purged)
- No automatic expiration or archival policies for MVP
- Users have full control over report deletion

### Authentication

- Session-based authentication is sufficient for MVP (no OAuth, SSO, or MFA required initially)
- Password reset functionality is deferred to post-MVP
- Account deletion and data export are deferred to post-MVP

### Provider Behavior

- All AI providers contribute equally to visibility, sentiment, and themes analysis
- Citation capability affects confidence levels only (not inclusion in analysis)
- Provider differences are surfaced via metadata and UI indicators
- No implicit provider ranking or favoritism
- Partial provider failures are visible and non-blocking
- Analysis succeeds if at least one provider returns a usable response

## Non-Goals *(optional)*

The following are explicitly out of scope for this feature:

- Traditional web crawling or SEO rank tracking
- Social media listening or social sentiment analysis
- Paid subscriptions, billing, or payment processing
- Long-term historical trend analysis or time-series data
- Mobile native applications (web-only for MVP)
- Multi-user organizations or team collaboration features
- White-label or reseller capabilities
- API access for third-party integrations
- Automated scheduled analyses or monitoring
- Custom AI model fine-tuning or training
- User-controlled location override (automatic only for MVP)
- Real-time or background insight generation (synchronous only for MVP)
- Hard delete of user data (soft delete only for MVP)
