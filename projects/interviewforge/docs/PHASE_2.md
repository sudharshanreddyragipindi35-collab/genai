# Phase 2 Grounded learning and Python practice

**Status: planned; blocked on Phase 1 exit criteria.** Goal: a candidate completes a diagnostic, receives a realistic roadmap, practices Python safely and gets grounded hints with persistent progress.

This corresponds to the source's Company Hub and Practice phase, estimated there at 4–5 weeks. Sandbox hardening, source review and AI quality evaluation may extend that estimate. Re-estimate after selecting the runner and completing the first vertical slice.

## Entry criteria

- Phase 1 demonstration and required checks pass.
- Content publishing, ownership isolation and Python UI sessions work.
- A reviewed starter problem set and company-source inventory are available.
- A separate hardened sandbox and a model provider can be configured for development. Offline adapters remain available for tests.

## Subtasks in dependency order

| ID | Subtask and deliverable | Depends on | Acceptance criteria |
| --- | --- | --- | --- |
| P2-01 | Curate initial topic/problem bank and company source inventory | Phase 1 | Each problem has validated reference solution, sample/hidden tests, progressive hints and provenance; company material has applicability and review metadata |
| P2-02 | Implement knowledge ingestion and retrieval with source lifecycle filters | P2-01 | Retrieval excludes unapproved, expired and wrong-region/role content; updates replace indexed versions; deletion removes associated chunks/embeddings |
| P2-03 | Add model gateway, Deep Agents/LangGraph orchestration, structured responses and grounded Company Hub answers | P2-02 | Direct calls handle simple work; the supervisor delegates complex work to bounded specialists; company claims carry supporting citations; missing/conflicting evidence triggers abstention; malformed outputs/timeouts are handled; traces include graph/prompt/model/source versions |
| P2-04 | Integrate external Python sandbox and asynchronous execution lifecycle | Phase 1 contracts, P2-01 | Run and Submit differ; limits, infinite loops, oversized output, forbidden network/filesystem access and job cleanup are verified; infrastructure failure is not graded as an incorrect answer |
| P2-05 | Implement diagnostic session and deterministic baseline | P2-01, P2-04 | Versioned question blueprint supports concept items and 2–3 coding tasks; retries cannot duplicate scoring; partial sessions show incomplete evidence; results persist |
| P2-06 | Generate roadmap and daily plan from baseline and constraints | P2-05 | Tasks fit availability and deadline or explicitly report infeasibility; recalculation preserves completed work; topic prerequisites and task reasons are visible |
| P2-07 | Implement adaptive practice and evidence-based mastery updates with an interpretable ML baseline | P2-04, P2-05 | Recommendation explains topic/difficulty choice; independent and hinted attempts differ; repeated submissions cannot inflate mastery; updates reference attempts; evaluation prevents user/time leakage and measures calibration before a learned model replaces the baseline |
| P2-08 | Add contextual hint-first tutor and post-submission code feedback | P2-03, P2-07 | Mode policy controls answer disclosure; feedback uses code and real runner results; complexity estimates are labeled separately from measurements; prompt injection cannot grant access to hidden tests or override policy |
| P2-09 | Implement spaced review and weakness detection | P2-06, P2-07 | Review intervals are deterministic; missed days and timezone boundaries behave correctly; weakness claims require minimum evidence and link to supporting attempts |
| P2-10 | Complete Company Hub, diagnostic, dashboard and practice Python UI | P2-03 through P2-09 | Candidate can complete the full learning loop; progress survives reconnects; queue/model errors are recoverable and readable; flows work with keyboard navigation |
| P2-11 | Add offline regressions, AI evaluation suite and operating controls | P2-10 | Tests cover abstention, citations, hint leakage, ownership and outages; generation/execution quotas work; prompt/model changes have recorded evaluation results |
| P2-12 | Review learning-loop demo and prepare Phase 3 handoff | P2-11 | Exit demonstration passes; remaining defects are triaged; strict assessment authorization/timer design is documented before OA implementation |

## Implementation checklist

- [ ] P2-01 Reviewed content baseline
- [ ] P2-02 Ingestion and retrieval
- [ ] P2-03 AI gateway and grounded answers
- [ ] P2-04 Hardened runner integration
- [ ] P2-05 Diagnostic baseline
- [ ] P2-06 Roadmap and daily planning
- [ ] P2-07 Adaptive practice and mastery
- [ ] P2-08 Tutor and code feedback
- [ ] P2-09 Revision and weakness detection
- [ ] P2-10 Complete learning UI
- [ ] P2-11 Evaluation and operating controls
- [ ] P2-12 Exit review

## Small delivery slices

First deliver one approved problem through submission, runner results and persisted attempt. Then add diagnostic and roadmap generation. Add retrieval and tutor once objective evidence is available. Finish with adaptive selection, revision scheduling, weakness insights and full UI integration. P2-02/P2-03 and P2-04 can be developed independently after content contracts are stable.

## Proposed API slice

`GET /companies/{id}/process`, `POST /knowledge/answer`, `POST /diagnostics`, diagnostic response/submit routes, `POST /roadmaps`, `POST /roadmaps/{id}/recalculate`, `GET /me/daily-plan`, `GET /practice/next`, `POST /practice/attempts`, `POST /code/run`, `POST /problems/{id}/submit`, `GET /code/jobs/{id}`, tutor session/message routes, `GET /revisions/due` and `GET /analytics/weaknesses`.

All candidate requests enforce ownership. Client-supplied pass counts, mastery scores and execution status are never authoritative. Hidden tests stay server-side and do not enter candidate-accessible tutor context.

## Quality gate

Create a versioned starter evaluation set with at least 30 cases covering supported/unsupported company claims, stale/conflicting sources, citation mismatches, prompt injection, hint escalation and code-feedback consistency. All critical access and leakage cases must pass; set and record baseline thresholds for noncritical teaching-quality cases before approving a release. Human review checks that cited text actually supports the answer; a resolvable URL alone is insufficient.

Run deterministic integration checks for interrupted jobs, duplicate callbacks, provider timeouts, wrong-user access, missed revision dates and insufficient diagnostic evidence. Do not use a live paid model as a requirement for ordinary local tests.

## Exit demonstration

1. Candidate selects the initial company/role/Python target and sees reviewed source context.
2. A sourced company question is answered with supporting citations; an unsupported one abstains.
3. Candidate completes the diagnostic and receives topic evidence and a time-feasible roadmap.
4. Candidate solves a recommended Python problem in the separate sandbox and sees persisted results.
5. Candidate asks for a hint and receives incremental help; post-submission feedback cites actual outcomes.
6. Mastery, daily tasks and next review update once, including after retries or reconnects.
7. Simulate runner/model failure; show recoverable errors without fabricated scores or answers.
8. Run the regression/evaluation gates and record the selected provider, prompt and content versions.

## Deferred

Strict OA timing and tutor lockout enforcement are Phase 3 work, although Phase 2 interfaces must allow server-enforced modes. Interview rounds are Phase 4. Final readiness scoring and reports are Phase 5. No camera, keystroke biometrics or official employer pass prediction is part of this phase.
