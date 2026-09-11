# Daily updates

## 2026-09-12 Claude connection diagnosis

Completed:

- Verified the configured key and Claude Sonnet 5 using a direct provider request.
- Verified the Deep Agents wrapper and complete Amazon Coach service independently.
- Identified the displayed failure as transient rather than a key, model, account, or integration error.
- Added accurate live, scope, offline, and connection-error labels plus one additional bounded retry.
- Added safe diagnostic logging containing only the exception type, never the key or provider message.

## 2026-09-12 Live Claude invocation

Completed:

- Connected allowed Amazon Coach questions to Claude through the Deep Agents supervisor.
- Added a key-safe `/coach/status` endpoint and visible configured/offline state.
- Added explicit `LIVE CLAUDE RESPONSE` and `LOCAL POLICY RESPONSE` labels.
- Kept non-Amazon requests outside the model invocation path.
- Added bounded timeouts, limited retries and credential-safe provider errors.

The first real question submitted by the user will be the first Anthropic API call. Current Amazon process claims remain restricted until the reviewed Amazon MCP source is connected.

## 2026-09-12 Claude configuration

Completed:

- Added Anthropic as a supported model provider.
- Selected the provider-qualified Claude Sonnet 5 model identifier for the local integration.
- Added a safe Claude-key placeholder to the committed example and created an ignored local `.env` ready for the real key.
- Made the Anthropic LangChain adapter an explicit optional agent dependency.

The real key must remain only in `projects/interviewforge/.env` and must never be committed.

## 2026-09-12 Amazon coach boundary

Completed:

- Removed the implementation-architecture screen from candidate navigation.
- Added an Amazon Interview Coach as the user-facing AI experience.
- Added deterministic refusal for named non-Amazon companies before any LLM or MCP request.
- Added an MCP adapter that always requests Amazon data and rejects results labeled for another company.
- Added safe placeholders for the provider, model, local API key, MCP server and MCP tool.

Verification: all 15 tests passed. Amazon questions remain local until integrations are configured; Microsoft and other named-company questions receive the Amazon-only response without reaching an LLM. The MCP adapter hard-codes Amazon and rejects cross-company results.

## 2026-09-11 Agentic AI direction

Completed:

- Made Deep Agents on LangGraph the planned runtime for multi-step coaching and interview workflows.
- Defined the coach supervisor, knowledge verifier, learning strategist, code reviewer and evaluation critic roles in Python.
- Added an optional, provider-neutral Deep Agents factory that performs no model call until configured.
- Documented hybrid RAG, context engineering, structured generation, durable memory, model routing, evaluation, observability and calibrated learning-model concepts.
- Added a visible AI System page to the running application so the planned intelligence and its control boundaries are reviewable.

Next: implement database persistence and candidate ownership, then connect reviewed knowledge retrieval and the first grounded agent workflow in Phase 2.

## 2026-09-11 Application foundation

Completed:

- Replaced the planning-only entry point with a locally runnable FastAPI application.
- Added a responsive candidate dashboard, preparation journey, onboarding preview and first Python practice screen.
- Added typed environment configuration, optional PostgreSQL connectivity, liveness/readiness endpoints, request trace IDs and redacted internal errors.
- Locked runtime and development dependencies for Python 3.13 and documented local startup.
- Completed P1-01 and P1-02; started the visible portion of P1-08.

Verification: lint and formatting checks passed, all 8 tests passed, and the repository structure checker passed. The onboarding screen deliberately labels its profile preview as unsaved, and the practice screen keeps code execution disabled until the separate secure runner is available.

Next: persist candidate profiles and targets through Phase 1 database models and migrations, then add authentication and ownership isolation.

## 2026-09-11

Completed:

- Created the private `genai` GitHub repository with InterviewForge as the first Python project.
- Added product understanding, architecture, requirements mapping and the complete delivery roadmap.
- Prepared Phase 1 with 10 subtasks and Phase 2 with 12 subtasks, dependencies and acceptance criteria.
- Added the minimal Python scaffold and repository structure/link checker.
- Recorded the daily commit-and-push workflow requested by the user.

Verification: repository checks and the scaffold status command passed. The initial planning commit was verified on GitHub `main`.

Implementation status: not started. Phase 1 and Phase 2 product tasks remain planned.

Next: begin P1-01, resolving the Python runtime, dependencies, configuration and reproducible development setup. Continue updating this log and pushing reviewed progress during implementation sessions.
