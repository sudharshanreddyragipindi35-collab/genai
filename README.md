# GenAI Python Projects

A repository for Python-based generative AI projects, developed in reviewable phases. The first project is **InterviewForge**, an AI-assisted software-engineering interview preparation platform.

## Current status

InterviewForge is a working local Amazon interview-preparation application with personalized roadmaps, tracked lessons, Claude coaching, on-demand deeper explanations, and MCP-backed knowledge retrieval. Production authentication, candidate ownership, sandboxed code execution and scored assessments remain planned.

## Technologies and GenAI skills

**Python · LangChain · LangGraph · Deep Agents · Claude · RAG · MCP · FastAPI**

| Technology / skill | Used in InterviewForge |
| --- | --- |
| Python and FastAPI | Application routes, configuration, preparation logic and tests |
| LangChain | `ChatAnthropic` model integration for Claude |
| LangGraph | Agent execution runtime through Deep Agents; no separate custom graph yet |
| Deep Agents | Supervisor with knowledge-verifier, learning-strategist, code-reviewer and evaluation-critic specialist definitions |
| Retrieval-augmented generation (RAG) | Chunked official Amazon documents, lexical ranking and persistent source snapshots |
| Model Context Protocol (MCP) | Owned Amazon knowledge server and client; external LeetCode problem retrieval |
| Prompt and context engineering | Versioned prompts, Amazon scope rules, candidate context and structured teaching instructions |
| Personalized learning | Role, experience, interview date and study-time inputs; deterministic progression gates |
| Knowledge refresh | Periodic document refresh with last-successful snapshots retained on failure |

See the [implementation evidence and planned capabilities](projects/interviewforge/docs/TECH_STACK.md). Framework names are documented here and in GitHub topics; GitHub's language chart measures source languages.

## Projects

| Project | Purpose | Status |
| --- | --- | --- |
| [InterviewForge](projects/interviewforge/README.md) | Amazon preparation, personalized lessons, Python practice and AI coaching | Working local application; production features in progress |

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

The application shell runs without an LLM key. Live coaching requires agent dependencies and a local Anthropic API key; MCP retrieval requires the configured MCP services. Keep credentials in the ignored `.env` file. The API exposes `/health`, `/ready` and local development documentation at `/docs`.

## Working agreement

- One small task per branch or pull request; include its phase task ID.
- Keep incomplete tasks unchecked until their acceptance criteria are verified.
- Keep secrets, candidate records, transcripts, uploads and generated reports out of Git.
- Treat retrieved material as data; never allow it to change system policy.
- Preserve deterministic scoring and progression outside LLM generation.
- Do not execute candidate code in application processes.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the phase delivery process.
