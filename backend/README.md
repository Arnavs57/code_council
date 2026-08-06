# Code Council AI — Backend

FastAPI foundation for the AI Engineering Governance Platform (Phase 1).
This phase ships **infrastructure only**: a runnable application shell with
configuration, logging, middleware placeholders and health/version endpoints.
No business logic, agents, models or auth yet.

> **Python version:** 3.12 recommended. The code is verified on 3.10+.

---

## Quick start

```bash
cd backend

# 1. Create a virtual environment (Windows)
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. (Optional) create local config
copy .env.example .env

# 4. Run the server
uvicorn app.main:app --reload
```

The API is now live:

| Endpoint | Description |
|----------|-------------|
| `GET /` | Application information |
| `GET /health` | Liveness check |
| `GET /version` | Application version |
| `GET /api/v1/*` | Same endpoints, versioned prefix |
| `GET /docs` | Interactive API docs (disabled in production) |

## Verify it works

```bash
# Tests (startup, middleware, endpoints, errors, config)
python -m pytest

# Lint
ruff check app tests

# Live smoke test
curl http://127.0.0.1:8000/health
# → {"app_name":"Code Council AI","version":"0.1.0","status":"ok",
#    "timestamp":"...","environment":"development"}
```

## Folder map

| Folder | Responsibility |
|--------|----------------|
| `app/main.py` | Application factory, lifespan, middleware/routers/handlers wiring |
| `app/api/` | Presentation: routes (v1) + global exception handlers |
| `app/core/` | Domain kernel: constants, exceptions, responses, helpers |
| `app/config/` | Pydantic settings, environment detection, loader |
| `app/logs/` | Logging configuration (JSON console + rotating file) |
| `app/middleware/` | Middleware stack (request-id, access log, placeholders) |
| `app/database/` | *Phase 2:* engine, sessions, Alembic migrations |
| `app/models/` | *Phase 2:* SQLAlchemy ORM entities |
| `app/schemas/` | *Phase 2:* Pydantic contracts |
| `app/repositories/` | *Phase 2:* data-access layer |
| `app/services/` | *Phase 2:* application services |
| `app/agents/` | *Phase 3:* AI agents (vertical slices) |
| `app/governance/` | *Phase 3:* governance controller |
| `app/orchestrator/` | *Phase 3:* LangGraph orchestrator |
| `app/events/` | *Phase 3:* event bus + projections |
| `app/websocket/` | *Phase 3:* live dashboard transport |
| `app/storage/` | *Phase 3:* object-storage abstraction |
| `tests/` | Unit/API tests (mirrors `app/`) |

## Configuration

Settings use the `CCAI_` prefix (see `.env.example`). Resolution order:
constructor args → environment variables → `.env.<environment>` / `.env` →
defaults. Environments: `development`, `testing`, `production`
(`CCAI_ENVIRONMENT`). Production disables the interactive docs.

### Ollama and GitHub-native reviews

The council is Ollama-first: set `CCAI_LLM_PROVIDER=ollama`,
`CCAI_OLLAMA_HOST`, and `CCAI_OLLAMA_MODEL`. Each agent streams its local
reasoning from Ollama, records real token telemetry (or clearly flagged
estimates), and reports a `$0.00` local cost. `GET /health/llm` confirms that
the configured provider and model are reachable. If `CCAI_OPENAI_API_KEY` is set,
OpenAI is the graceful fallback for an unavailable Ollama service.

The workflow at `.github/workflows/code-council.yml` runs the council directly
on the GitHub Actions runner and publishes one updatable governance PR comment
plus a GitHub Check Run with the action's ephemeral GitHub token—no external
dashboard or API endpoint is required. For local Ollama, set the
`CODE_COUNCIL_RUNNER` repository variable to a self-hosted runner that has
Ollama installed and running. The complete agent collaboration, tool execution
log, timeline, token analytics, and final decision are visible from the PR.

## Logging

Structured JSON on stdout and `logs/app.log` (rotating, 10 MiB × 5).
Every request carries a `request_id` (echoed in the `X-Request-ID` response
header). Startup, shutdown, request access lines and errors are logged.

## Development workflow

```bash
python -m pytest          # run tests
ruff check app tests      # lint
ruff format --check app   # formatting check
uvicorn app.main:app --reload   # dev server with hot reload
```

Add a new endpoint: create `app/api/v1/<name>.py` with an `APIRouter` and
include it in `app/api/v1/router.py` — nothing else changes.
