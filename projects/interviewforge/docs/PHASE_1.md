# Phase 1 Foundation and core data

**Status: planned.** Goal: a runnable Python foundation where an authenticated candidate can save a profile and Python target, and an authorized administrator can manage reviewed company/topic/problem records.

This phase combines source roadmap Phase 0 (setup) and Phase 1 (core backend). The source allocates approximately 4–5 weeks total; treat that as a reference, not a commitment. Re-estimate after the UI and authentication spikes using actual available hours.

## Entry criteria

- Repository structure and initial scope are understood.
- A development database and authentication approach can be configured.
- No production candidate data or real credentials are used as seed fixtures.

## Subtasks in dependency order

| ID | Subtask and deliverable | Depends on | Acceptance criteria |
| --- | --- | --- | --- |
| P1-01 | Resolve Python runtime and dependencies; add application configuration, dependency lock and development instructions | None | Fresh checkout installs reproducibly; missing required settings produce clear errors; secrets are excluded from Git |
| P1-02 | Build API startup, typed settings, health endpoints and structured logging | P1-01 | Health works without external AI; readiness reports database failures accurately; errors include trace IDs without secrets |
| P1-03 | Design and migrate identity, candidate profile and target models | P1-02 | Migrations apply to an empty database; required fields and owner relationships are enforced; language is constrained to Python for the initial release |
| P1-04 | Implement authentication, authorization and candidate profile APIs | P1-03 | Candidate can register/sign in through the selected auth mechanism, read/update own profile and save target; another user's records cannot be read or modified |
| P1-05 | Model company, role, curriculum, problem bank, source and knowledge versions | P1-03 | Records include source/license metadata and review state; hidden tests are absent from candidate responses; referential constraints reject orphaned records |
| P1-06 | Add reviewed content administration and synthetic seed fixtures | P1-04, P1-05 | Only admins can approve content; actor/time/reason is audited; draft or expired company facts cannot appear as verified current facts |
| P1-07 | Add practice-attempt, execution-job and AI-trace interfaces and persistence foundations | P1-05 | Job lifecycle and trace schemas are documented; idempotency strategy is explicit; no candidate code or real model call executes through a placeholder |
| P1-08 | Prototype Python UI for sign-in, onboarding, target selection and admin content review | P1-04, P1-06 | Profile survives refresh and a new session; keyboard form navigation and understandable errors work; document Python UI limitations for later strict OA |
| P1-09 | Add CI, authorization/schema tests and local startup verification | P1-02 through P1-08 | CI runs on a clean checkout; ownership-denial cases pass; database migration and rollback/recovery procedure is exercised locally |
| P1-10 | Review privacy, configuration, backup and developer handoff | P1-09 | Data categories/retention proposal documented; sample export/deletion design includes derived data; a clean environment can reproduce the phase demo |

## Implementation checklist

- [ ] P1-01 Runtime and dependency foundation
- [ ] P1-02 API and configuration
- [ ] P1-03 Identity/profile schema
- [ ] P1-04 Authentication and ownership enforcement
- [ ] P1-05 Content and knowledge schema
- [ ] P1-06 Admin review and seed data
- [ ] P1-07 Attempt/job/trace contracts
- [ ] P1-08 Python UI proof
- [ ] P1-09 CI and integration verification
- [ ] P1-10 Operational handoff

## Proposed API slice

`GET /health`, `GET /ready`, `GET /me`, `PATCH /me/profile`, `POST /me/targets`, `GET /companies`, `GET /roles`, `GET /topics`, `GET /problems/{id}`, plus protected admin content review endpoints. Choose auth routes to match the selected identity implementation. No unauthenticated admin mutation is allowed.

Profile fields include experience, target company/role/region, Python language, preparation deadline, daily availability and timezone. Knowledge publication requires source URL/reference, license or permission status, verified timestamp, next review date and reviewer.

## Exit demonstration

1. Start the documented development environment from a fresh checkout.
2. Sign in as candidate A, save a Python preparation target and verify persistence.
3. Sign in as candidate B and demonstrate denied access to A's data.
4. As admin, create a sourced content fixture, approve it and inspect the audit record.
5. As candidate, see only allowed fields and approved applicable content; hidden tests remain private.
6. Restart the service, confirm persisted state and run the phase checks in CI.

Record evidence against each step before marking Phase 1 complete. If the Python UI cannot satisfy basic session isolation and navigation, resolve that architecture decision before Phase 2.

## Excluded from this phase

Real tutoring, embeddings, adaptive recommendations, submitted-code execution, timed OA, proctoring, interview conversations, billing and deployment to paying users. The foundation prepares their interfaces without claiming their functionality.
