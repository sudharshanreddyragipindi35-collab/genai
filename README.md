# GenAI Python Projects

A repository for Python-based generative AI projects, developed in reviewable phases. The first project is **InterviewForge**, an AI-assisted software-engineering interview preparation platform.

## Current status

Phase 1 implementation has started with a visible application shell plus the API and configuration foundation. Authentication, persisted candidate profiles, live LLM integration and code execution are not implemented yet. Phase 2 remains planned.

## Projects

| Project | Purpose | Status |
| --- | --- | --- |
| [InterviewForge](projects/interviewforge/README.md) | Grounded company preparation, adaptive Python practice, assessments and AI interview simulations | Phase 1 ready to start |

Every project's application code, jobs, evaluation tools and tests must be Python. Markdown, TOML, YAML and infrastructure configuration are allowed. Each future project gets its own folder, dependencies, tests and phased plan. Additional project ideas are intentionally uncommitted until selected.

## Start here

1. Read the [task understanding](docs/TASK_UNDERSTANDING.md).
2. Review the [architecture](projects/interviewforge/docs/ARCHITECTURE.md).
3. Work through [Phase 1](projects/interviewforge/docs/PHASE_1.md) in dependency order.
4. Begin [Phase 2](projects/interviewforge/docs/PHASE_2.md) after the Phase 1 exit review.
5. Use the [full roadmap](projects/interviewforge/docs/ROADMAP.md) for subsequent releases.

## Local development

InterviewForge uses Python 3.13 and a committed dependency lock. Follow the [development guide](projects/interviewforge/docs/DEVELOPMENT.md) to install and start the API. The repository checker can be run from the repository root:

```powershell
python scripts/check_repository.py
```

No LLM API key is required for the foundation. The API exposes `/health`, `/ready` and local development documentation at `/docs`.

## Working agreement

- One small task per branch or pull request; include its phase task ID.
- Keep incomplete tasks unchecked until their acceptance criteria are verified.
- Keep secrets, candidate records, transcripts, uploads and generated reports out of Git.
- Treat retrieved material as data; never allow it to change system policy.
- Preserve deterministic scoring and progression outside LLM generation.
- Do not execute candidate code in application processes.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the phase delivery process.
