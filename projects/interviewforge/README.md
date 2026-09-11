# InterviewForge

InterviewForge is a planned AI-powered interview preparation product with persistent candidate progress, source-grounded company guidance, adaptive Python practice and hiring-journey simulations.

**Status: working local Phase 1 application slice with Amazon onboarding, a tracked roadmap, Claude coaching, and LeetCode MCP problem retrieval.** See the [development guide](docs/DEVELOPMENT.md) to run it.

## Delivery order

| Phase | Outcome | Plan |
| --- | --- | --- |
| 1 | Secure foundation, candidate profile, reviewed content model, Python UI proof | [Phase 1 tasks](docs/PHASE_1.md) |
| 2 | Company Hub, diagnostic, roadmap, practice, sandbox integration and grounded tutor | [Phase 2 tasks](docs/PHASE_2.md) |
| 3 | Server-timed online assessment, deterministic scoring and interview unlock | [Roadmap](docs/ROADMAP.md) |
| 4 | Technical, behavioral, managerial and lightweight HR simulations | [Roadmap](docs/ROADMAP.md) |
| 5 | Evidence-based readiness, tracker, report and beta hardening | [Roadmap](docs/ROADMAP.md) |
| 6 | Soft launch and iterative quality improvements | [Roadmap](docs/ROADMAP.md) |

The application starts with one company target and Python coding. Multi-company expansion, other coding languages, deep system-design workspace, billing, mobile apps and specialist model training are deferred.

See [architecture](docs/ARCHITECTURE.md), [GenAI architecture](docs/GENAI_ARCHITECTURE.md), and [requirements mapping](docs/REQUIREMENTS.md). The Amazon-only boundary is enforced before model invocation and in the MCP knowledge adapter. Authentication, PostgreSQL candidate ownership, a scored coding assessment, and reviewed Amazon knowledge retrieval remain future work.
The current local application supports an Amazon-only candidate journey:

1. Select Amazon and enter the exam or interview date, experience, and daily study time.
2. Receive a saved three-level Python preparation roadmap.
3. Complete tasks in order to unlock the coding assessment.
4. Complete the assessment to unlock the interview simulation stage.
5. Ask the Amazon coach questions at any time; allowed questions use Claude through Deep Agents when configured.

Roadmap progress is saved to the ignored `.interviewforge/state.json` local-preview file. Production persistence and candidate ownership remain PostgreSQL work.

Public coding problems can be synchronized through a configured Streamable HTTP LeetCode MCP server. Until it is connected, the UI identifies its bundled public links as `curated`; it never represents them as MCP results.


## Amazon learning flow

Start at /onboarding. Choose SDE I or SDE II, experience, coding level, interview date, daily hours and optional job-specific GenAI. The first stage contains lessons and exercises before coding practice. SDE II adds system-design depth. Dates and repetition counts adapt to availability and skills.

The owned Python Amazon MCP bridge retrieves official Leadership Principles and interview-preparation pages. Claude receives these sources and cites them. Coding sync uses reviewed Amazon interview reports and checks exact problem slugs through LeetCode MCP. The initial registry has two SDE I questions and one SDE II question; it is historical community evidence, not an official or exhaustive question bank.

See the development guide for both local MCP services. Task completion and assessments remain self-reported prototype checkpoints, not validated hiring-readiness scores.
