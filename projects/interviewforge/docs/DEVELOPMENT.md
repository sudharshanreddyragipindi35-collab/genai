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
| `INTERVIEWFORGE_LLM_PROVIDER` | `disabled` by default; change to `openai` when the key and model are ready |
| `INTERVIEWFORGE_LLM_MODEL` | Provider-qualified tool-calling model identifier used by Deep Agents |
| `OPENAI_API_KEY` | Secret used by the model adapter; keep only in the ignored local `.env` |
| `INTERVIEWFORGE_AMAZON_MCP_SERVER_URL` | MCP server containing reviewed Amazon company knowledge |
| `INTERVIEWFORGE_AMAZON_MCP_TOOL` | Amazon search tool name exposed by the MCP server |

The basic application starts without a database or key. Copy `.env.example` to `.env`, paste the key only in that local file, set the model and provider, and later add the reviewed Amazon MCP endpoint. Never paste a real key into chat, source code, `.env.example`, commits, screenshots, or logs. This foundation does not provision PostgreSQL or create schema tables. Invalid configuration prevents startup with a field-level error that omits credential values.

## Endpoint behavior

- `GET /`: visible candidate dashboard and application navigation.
- `GET /onboarding`: target setup preview; submitted values are explicitly not persisted yet.
- `GET /practice`: first Python problem experience; code execution is explicitly disabled until the secure runner is implemented.
- `GET /coach`: Amazon-only coach. Named requests about other companies are refused before any LLM or MCP call.
- `GET /health`: 200 while the application is alive, without requiring a database or model.
- `GET /ready`: performs `SELECT 1`; returns 200 when the database is reachable or 503 when unavailable. This checks connectivity, not migration/schema readiness yet.
- `/docs` and `/openapi.json`: available outside production for development.
- Every request receives a server-generated `X-Trace-ID`. Internal errors return a generic response with that ID. Request logs include status, duration and method, excluding request URLs, bodies, database errors and credentials.

No registration, profile, UI or AI endpoints exist yet. Disabling API documentation is not authentication; do not expose this development server as the finished product.

## Verification

```powershell
uv run --locked pytest
uv run --locked ruff check .
uv run --locked ruff format --check .
python ../../scripts/check_repository.py
```

Tests do not need a real database or paid model: they use a deliberately unreachable database for the outage case and a controlled engine double for the success/lifecycle case. A live successful PostgreSQL connection and migrations must be verified when database provisioning is added in P1-03.

Dependency changes require editing `pyproject.toml`, running `uv lock`, reviewing the lock diff and repeating verification. Fresh environments use `uv sync --locked` to reject a stale lock. This follows the [uv locking workflow](https://docs.astral.sh/uv/concepts/projects/sync/). Startup resources use [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/) and settings follow [FastAPI configuration guidance](https://fastapi.tiangolo.com/advanced/settings/).
