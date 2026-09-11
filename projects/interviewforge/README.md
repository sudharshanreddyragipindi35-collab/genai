# InterviewForge

InterviewForge is a planned AI-powered interview preparation product with persistent candidate progress, source-grounded company guidance, adaptive Python practice and hiring-journey simulations.

**Status: basic Phase 1 application preview implemented; not a working MVP.** See the [development guide](docs/DEVELOPMENT.md) to run it.

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

See [architecture](docs/ARCHITECTURE.md) and [requirements mapping](docs/REQUIREMENTS.md). `src/interviewforge` now contains API startup, typed configuration, health/readiness checks and request logging. Authentication and user-facing preparation features are next-phase work.
