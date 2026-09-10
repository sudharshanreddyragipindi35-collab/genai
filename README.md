# GenAI Python Projects

A repository for Python-based generative AI projects, developed in reviewable phases. The first project is **InterviewForge**, an AI-assisted software-engineering interview preparation platform.

## Current status

Planning and repository scaffold only. Phase 1 and Phase 2 are **not implemented**. No live LLM integration, authentication, code execution, or deployed application is included yet.

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

## Local scaffold

Python 3.11 or newer is the initial project baseline. From the repository root:

```powershell
python projects/interviewforge/src/interviewforge/__main__.py
python scripts/check_repository.py
```

The first command prints the planning status; it does not start the product. Phase implementation will add installation and application startup commands. No API key is needed for the current scaffold.

## Working agreement

- One small task per branch or pull request; include its phase task ID.
- Keep incomplete tasks unchecked until their acceptance criteria are verified.
- Keep secrets, candidate records, transcripts, uploads and generated reports out of Git.
- Treat retrieved material as data; never allow it to change system policy.
- Preserve deterministic scoring and progression outside LLM generation.
- Do not execute candidate code in application processes.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the phase delivery process.
