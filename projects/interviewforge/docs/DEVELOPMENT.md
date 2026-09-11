# Local development

## Requirements

Use Python 3.13 and uv 0.12.13 (the dependency manager used to generate this lock). Install uv from its official distribution if needed: `python -m pip install uv==0.12.13`. Dependencies are recorded in `uv.lock`; normal setup must not re-resolve them.

From the repository root:

```powershell
cd projects/interviewforge
uv sync --locked
uv run --locked interviewforge
```

Open `http://127.0.0.1:8000/docs` to try the API. The command binds only to the local machine. Run it from the project directory so `.env` is loaded from the expected location. Stop the server with Ctrl+C.

To install the agent runtime when developing LLM workflows:

```powershell
uv sync --extra agents --locked
```

This installs the locked Deep Agents, LangGraph, LangChain, MCP SDK, and OpenAI model adapter packages. It does not make a model call or require an API key until an agent is invoked.

If using the repository-local tool environment created during development, replace `uv` with `../../.tools/Scripts/uv.exe`. The tool environment is ignored and is not required in another checkout.

## Configuration

| Variable | Meaning |
| --- | --- |
| `INTERVIEWFORGE_DATABASE_URL` | Required PostgreSQL URL using `postgresql+psycopg`, with host and database |
| `INTERVIEWFORGE_ENVIRONMENT` | `development` (default), `test` or `production`; production disables OpenAPI/docs routes |
| `INTERVIEWFORGE_DB_CONNECT_TIMEOUT` | Database connection and pool checkout timeout, integer 1–10 seconds; default 3 |
| `INTERVIEWFORGE_LLM_PROVIDER` | `anthropic` for the configured Claude integration; `disabled` turns model use off |
| `INTERVIEWFORGE_LLM_MODEL` | Provider-qualified tool-calling model identifier used by Deep Agents |
| `ANTHROPIC_API_KEY` | Claude API secret; keep only in the ignored local `.env` |
| `INTERVIEWFORGE_AMAZON_MCP_SERVER_URL` | MCP server containing reviewed Amazon company knowledge |
| `INTERVIEWFORGE_AMAZON_MCP_TOOL` | Amazon search tool name exposed by the MCP server |

The basic application starts without a database or key. A local ignored `.env` is prepared with `ANTHROPIC_API_KEY=`; paste the Claude key after that equals sign. The example selects `anthropic:claude-sonnet-5`, which can be changed when model availability or cost requires it. Later, add the reviewed Amazon MCP endpoint. Never paste a real key into chat, source code, `.env.example`, commits, screenshots, or logs. This foundation does not provision PostgreSQL or create schema tables. Invalid configuration prevents startup with a field-level error that omits credential values.

## Endpoint behavior

- `GET /`: visible candidate dashboard and application navigation.
- `GET /onboarding`: target setup preview; submitted values are explicitly not persisted yet.
- `GET /practice`: first Python problem experience; code execution is explicitly disabled until the secure runner is implemented.
- `GET /coach`: Amazon-only coach. Named requests about other companies are refused before any LLM or MCP call.
- `GET /coach/status`: reports provider, model, configuration readiness and MCP readiness without returning the API key.
- `GET /health`: 200 while the application is alive, without requiring a database or model.
- `GET /ready`: performs `SELECT 1`; returns 200 when the database is reachable or 503 when unavailable. This checks connectivity, not migration/schema readiness yet.
- `/docs` and `/openapi.json`: available outside production for development.
- Every request receives a server-generated `X-Trace-ID`. Internal errors return a generic response with that ID. Request logs include status, duration and method, excluding request URLs, bodies, database errors and credentials.

No registration, profile, UI or AI endpoints exist yet. Disabling API documentation is not authentication; do not expose this development server as the finished product.

When `configured` is `true` at `/coach/status`, submitting an allowed Amazon question sends the prompt to Anthropic through the Deep Agents supervisor. The UI labels a successful result `LIVE CLAUDE RESPONSE`. Local policy refusals and provider failures are never labeled as successful model output. Until MCP is configured, the runtime prompt limits Claude to general coaching and prevents claims about current Amazon process facts.

## Verification

```powershell
uv run --locked pytest
uv run --locked ruff check .
uv run --locked ruff format --check .
python ../../scripts/check_repository.py
```

Tests do not need a real database or paid model: they use a deliberately unreachable database for the outage case and a controlled engine double for the success/lifecycle case. A live successful PostgreSQL connection and migrations must be verified when database provisioning is added in P1-03.

Dependency changes require editing `pyproject.toml`, running `uv lock`, reviewing the lock diff and repeating verification. Fresh environments use `uv sync --locked` to reject a stale lock. This follows the [uv locking workflow](https://docs.astral.sh/uv/concepts/projects/sync/). Startup resources use [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/) and settings follow [FastAPI configuration guidance](https://fastapi.tiangolo.com/advanced/settings/).


## Amazon public knowledge MCP

Start this Python bridge from the InterviewForge project directory in a terminal with outbound network access:

```powershell
.\.venv\Scripts\python.exe -m interviewforge.ai.amazon_server
```

It listens on http://127.0.0.1:3001/mcp. Set INTERVIEWFORGE_AMAZON_MCP_SERVER_URL to that URL and restart the application. The bridge is maintained by InterviewForge; Amazon supplies the public source pages, not the MCP server. It requires no candidate login.

The tool search_amazon_company_knowledge reads only the fixed official source registry. The tool amazon_reported_coding_questions serves reviewed community evidence, with source URLs and known report dates. Add evidence to amazon_content.py only after checking the first-person report. Difficulty-only LeetCode search is not part of the application sync path.

Start the existing LeetCode MCP service separately if live problem availability checks are needed. It receives only exact attributed slugs through get_problem. A failed sync never falls back to generic problems.

Old generic plans are retained on disk but do not load as version 2 plans. Creating a new plan replaces the active state; progress is local and self-reported.
