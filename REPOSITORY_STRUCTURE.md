# Code Council AI — Repository Structure

**Status:** Proposed (v1.0) · **Phase:** Pre-development · **Companion to:** `ARCHITECTURE.md` (system design)
**Stack:** React + TypeScript + Vite + Tailwind + shadcn/ui · FastAPI (Python) · Supabase PostgreSQL + SQLAlchemy · LangGraph · REST + WebSockets

---

## 0. Design Principles for This Structure

1. **Clean Architecture layering.** Dependencies point inward: `api/` → `services/` → `repositories/` → `database/`. Domain (`core/`, `models/`, `schemas/`) depends on nothing.
2. **Vertical slices for AI roles.** Each agent is a self-contained package so roles evolve, retry, and deploy independently.
3. **Everything asynchronous is event-shaped.** The event system is a peer module, not an afterthought.
4. **Tools are plugins.** Adding a scanner never modifies existing code (open/closed).
5. **Prompts are artifacts.** Versioned at the repo root, diffable in review, consumed by backend code.
6. **Frontend mirrors the domain.** Feature folders map 1:1 to backend concerns so engineers find things by intuition.

---

## 1. Complete Root Repository Structure

```
code-council-ai/
├── .github/                    # CI/CD workflows, PR templates, issue templates
├── backend/                    # FastAPI service: API, agents, governance, orchestrator, events
├── frontend/                   # React + Vite + TS + Tailwind + shadcn/ui SPA
├── architecture/               # System design (ARCHITECTURE.md) + Architecture Decision Records (ADRs)
├── diagrams/                   # Diagram sources (Mermaid, draw.io) embedded by docs/architecture
├── docs/                       # Human-facing documentation (API, dev, deploy, prompts guide, agent specs)
├── prompts/                    # Versioned prompt library — the source of truth for prompts
├── scripts/                    # Developer/ops scripts (setup, seed, docker helpers, lint)
├── tests/                      # Cross-app tests: end-to-end (Playwright) + shared fixtures
├── infrastructure/             # docker-compose, container builds, Kubernetes/terraform (later)
├── assets/                     # Static brand assets (logo, screenshots used by docs)
├── .env.example                # Environment variable template (all services)
├── .editorconfig               # Cross-editor formatting defaults
├── .gitignore
├── Makefile                    # Task runner: make dev, make test, make lint, make docker-up
└── README.md                   # Project overview, quick start, links to docs/
```

| Root folder | Purpose |
|-------------|---------|
| `.github/` | CI/CD pipelines (lint → test → build → deploy), PR/issue templates. Keeps automation out of app code. |
| `backend/` | The entire Python service. Self-contained (`pyproject.toml`, `Dockerfile`) so it can be built and deployed independently of the frontend. |
| `frontend/` | The entire TypeScript SPA. Self-contained (`package.json`) for independent build/deploy. |
| `architecture/` | Canonical system design + ADRs. Separate from `docs/` because decision records have a different lifecycle (versioned, reviewed, rarely edited) than user docs (maintained continuously). |
| `diagrams/` | Source files for diagrams rendered into `docs/architecture`. Single source of truth so diagrams aren't screenshots scattered in prose. |
| `docs/` | Human-facing documentation (Section 12). |
| `prompts/` | Versioned prompt artifacts (Section 3 note). Non-engineers (prompt engineers, reviewers) can review prompts without touching code. |
| `scripts/` | One-off and recurring developer scripts (DB reset, seed demo data, lint-all). Anything runnable but not part of the deployed app. |
| `tests/` | End-to-end tests that span both apps + shared fixtures (sample repos, canned events). Unit tests live inside `backend/tests/` and colocated in `frontend/`. |
| `infrastructure/` | Deployment topology: docker-compose for local dev, later Kubernetes/Terraform for prod. Keeps infra config out of both apps. |
| `assets/` | Brand/design assets referenced by docs and marketing surfaces. |

**Monorepo rationale:** one repo, one PR can touch backend + frontend + prompts + docs for a single feature; atomic cross-cutting changes; shared CI; simple local dev. The two apps remain deployable independently (separate containers), which is what "monorepo" must preserve — it is *not* a single deployable.

---

## 2. Backend Folder Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app factory + lifespan (db, bus, ws startup/shutdown)
│   ├── api/                     # PRESENTATION — HTTP routes only
│   │   ├── v1/
│   │   │   ├── routes/          # runs.py, findings.py, discussions.py, decisions.py,
│   │   │   │                    # policies.py, agents.py, audit.py, uploads.py
│   │   │   ├── dependencies.py  # DI providers: db session, current user, current run, tenant
│   │   │   └── errors.py        # Domain exceptions → RFC 7807 problem responses
│   ├── core/                    # DOMAIN KERNEL — base exceptions, enums, constants, result types
│   ├── config/                  # pydantic-settings Settings, env parsing, feature flags
│   ├── database/                # engine, async session, Alembic migrations, seeders
│   ├── models/                  # SQLAlchemy ORM entities, grouped by domain module
│   ├── schemas/                 # Pydantic v2 schemas: API contracts, event payloads, internal DTOs
│   ├── repositories/            # Data-access layer (SQL + cache) behind interfaces
│   ├── services/                # APPLICATION — non-AI business logic (runs, findings, policies)
│   ├── agents/                  # AI agents — isolated per role (Section 3)
│   ├── governance/              # Governance controller internals (Section 4)
│   ├── orchestrator/            # LangGraph graph + workflow + dispatch (Section 5)
│   ├── context/                 # Shared-context store + synchronization (Section 9)
│   ├── events/                  # Event system: bus, models, publishers, subscribers (Section 7)
│   ├── websocket/               # Connection/session/broadcast/channels (Section 8)
│   ├── tools/                   # External tool integrations + sandbox + registry (Section 6)
│   ├── llm/                     # LLM gateway: provider abstraction, structured output, budget hooks
│   ├── middleware/              # ASGI middleware: request-id, auth, logging, error normalization
│   ├── security/                # Authentication, authorization/RBAC, secret handling
│   ├── storage/                 # Object-storage abstraction (repo artifacts, evidence blobs)
│   ├── reports/                 # Report builders: final decision summary, evidence packs
│   ├── logs/                    # Logging *configuration* (JSON formatters, handlers) — not runtime files
│   ├── workers/                 # Long-running processes: queue consumers, event subscribers, watchdog
│   └── utils/                   # Small shared helpers (ids, time, hashing, pagination)
├── tests/                       # Backend tests, mirroring app/ (Section 13)
├── alembic.ini                  # Alembic config for database migrations
├── pyproject.toml               # Dependencies + tooling (ruff, mypy, pytest)
├── Dockerfile
├── .env.example
└── README.md
```

### 2.1 Why every folder exists

| Folder | Layer | Responsibility | Boundary rule |
|--------|-------|----------------|---------------|
| `api/` | Presentation | HTTP route handlers, request validation, response shaping | **Never** touches DB or agents directly — calls services |
| `core/` | Domain | Base exceptions, enums (`RunStatus`, `Verdict`), constants, `Result`/`Error` types | Zero dependencies; everything depends on it |
| `config/` | Infra | `Settings` via pydantic-settings; env precedence; feature flags | Imported by anything needing config; no logic |
| `database/` | Infra | Engine/session lifecycle, migrations, seed data | Owned by nobody; used by repositories |
| `models/` | Domain | ORM entities (persistence shape) | No Pydantic, no business logic |
| `schemas/` | Domain | Pydantic contracts (API + events + internal DTOs) | No ORM imports (decouples API from DB shape) |
| `repositories/` | Infra | Encapsulates queries/transactions per aggregate | Only layer that imports `models/` + `database/` |
| `services/` | Application | Orchestrates repositories; use cases (start run, close discussion) | No HTTP, no FastAPI imports — testable in isolation |
| `agents/` | Application (AI) | Agent definitions, loops, prompts, role logic | See Section 3 |
| `governance/` | Application (AI) | Policy, planning, budgets, supervision | Consumes `agents/` metadata + `context/` + `events/` |
| `orchestrator/` | Application (AI) | LangGraph graph execution | See Section 5 |
| `context/` | Application (AI) | Shared blackboard + sync rules | See Section 9 |
| `events/` | Application (AI) | Event bus + projections | See Section 7 |
| `websocket/` | Presentation | WS transport to frontend | See Section 8 |
| `tools/` | Application (AI) | Tool plugins + sandbox | See Section 6 |
| `llm/` | Infra | Provider clients, structured output, token accounting | Single choke point for all model calls |
| `middleware/` | Presentation | Cross-cutting HTTP concerns | Registered in `main.py` only |
| `security/` | Infra | Authn/authz, RBAC, secret access | Consumed by `api/dependencies.py` |
| `storage/` | Infra | Object-storage adapter (S3/MinIO/local) | Replaces the concrete client everywhere |
| `reports/` | Application | Render decision summaries/evidence packs | Pure functions; called by services |
| `logs/` | Infra | Logging configuration (JSON, correlation IDs) | Configured once in `main.py` |
| `workers/` | App entry | Processes for queue consumers, event subscribers, watchdog | Deployable separately from the API |
| `utils/` | Infra | Small shared helpers | No business logic; no domain imports |

### 2.2 Dependency rules (enforced by linting)

```
api/  websocket/  workers/
   │        │
   ▼        ▼
services/  governance/  orchestrator/  agents/  events/
   │        │        │        │         │
   ▼        ▼        ▼        ▼         ▼
repositories/  context/  tools/  llm/
   │
   ▼
database/  storage/
   │
   ▼
core/  models/  schemas/  config/  (shared foundation)
```

A circular-import lint rule (e.g., a custom Ruff rule or CI check) treats layer violations as build failures. This is the single most important guardrail for a codebase of this size.

---

## 3. AI Agent Organization

### 3.1 Recommended structure — shared foundation + vertical slices

```
app/agents/
├── base/                          # SHARED FOUNDATION (framework, not business)
│   ├── agent.py                   # Abstract AgentExecutor: lifecycle (start → work → finish)
│   ├── executor.py                # The agent run loop: context → prompt → LLM → tools → outputs
│   ├── config.py                  # BaseAgentConfig: model tier, temperature, token budget, timebox
│   ├── memory.py                  # Memory interface: per-agent history adapter
│   ├── tools.py                   # Tool binding: allowlist → sandboxed tool instances
│   ├── schemas.py                 # Base Finding / Vote / Question / Answer contracts
│   ├── registration.py            # @register_agent decorator → governance registry
│   └── errors.py                  # AgentError taxonomy (llm, tool, budget, context)
├── registry.py                    # Runtime view: role → class, capabilities, model tier
├── security_officer/              # VERTICAL SLICE
│   ├── agent.py                   # Agent class: role identity, model config, lifecycle overrides
│   ├── prompt.py                  # System prompt (owned by this agent only)
│   ├── service.py                 # Role-specific logic beyond the base loop
│   ├── tools.py                   # Tool allowlist + any role-specific tool wrappers
│   ├── schemas.py                 # Role-specific outputs (Severity, CWE taxonomy)
│   ├── config.py                  # Role defaults (model tier: strongest)
│   └── memory.py                  # Optional memory-policy override
├── software_architect/            # (same shape)
├── qa_lead/                       # (same shape)
├── devops_lead/                   # (same shape)
├── red_team/                      # (same shape; strongest tier, adversarial role)
└── release_manager/               # (same shape; read-only, decision authority)
```

### 3.2 Advantages / disadvantages

| Design | Advantages | Disadvantages |
|--------|-----------|---------------|
| **A: Fully shared, role config only** (one `agents/` with prompts in a dict) | Tiny; zero duplication | Roles cannot own distinct tools/schemas cleanly; prompts tangle with logic; a Red Team's adversarial needs leak into Security's file; adding a role touches shared files → merge friction |
| **B: Vertical slices (recommended)** | Role knowledge colocated; independent iteration (prompt changes never touch other roles); per-role model/tool/budget config; testable in isolation; trivial to add/remove roles; clear git ownership | Some boilerplate (mitigated by `base/`); risk of divergent patterns (mitigated by code review + shared base contracts) |
| **C: Each agent a separate package** (`plugins/security_officer/`) | Maximum isolation; independently versionable/releasable | Overkill in a monorepo; adds packaging/dependency-management friction; hinders cross-agent shared-code reuse |

**Recommendation: B**, with a strict rule: `base/` may not import any vertical slice, and a vertical slice may import only `base/`, `core/`, `context/`, `events/`, `tools/`, `llm/`. Prompts live in `prompt.py` files (imported as data), while the **versioned review artifact** lives in root `prompts/` and CI asserts they match — so prompt changes are reviewable outside code reviews.

---

## 4. Governance Layer Structure

```
app/governance/
├── controller.py              # Facade: lifecycle (validate → plan → allocate → assign → monitor → remediate → close)
├── planning/
│   ├── plan_builder.py        # Repo metadata + policy → execution plan (DAG of nodes + edges + timeouts)
│   └── plan_validator.py      # DAG sanity: no cycles, dependencies satisfiable, budget-feasible
├── policies/
│   ├── policy.py              # Policy model: conditions, actions (e.g., "P0 without waiver → block")
│   ├── engine.py              # Policy evaluation engine (pure, testable)
│   └── builtin/               # Versioned built-in policies (severity gates, veto rules, safe-default NO-GO)
├── permissions/
│   ├── rbac.py                # User/role → action checks (viewer, approver, admin)
│   └── grants.py              # Agent grants: tool allowlists, context read/write scopes, LLM tier
├── budgets/
│   ├── allocator.py           # Per-run/per-agent token + time budget allocation
│   ├── ledger.py              # Consumption accounting (from events + LLM gateway hooks)
│   └── limits.py              # Defaults + hard caps
├── registry/
│   ├── agent_registry.py      # Registered roles: capabilities, model tier, grant profile
│   └── tool_registry.py       # Registered tools: input schema, sandbox profile, default allowlist
├── supervision/
│   └── watchdog.py            # Heartbeat/stall/budget-overrun detection → remediation commands
└── context_policies/          # Sharing rules: who may write/read which context namespaces
```

| Component | Responsibility |
|-----------|----------------|
| `controller.py` | The only public entry point for governance; the orchestrator and API call this, never internals |
| `planning/` | Turns "repo uploaded" + policy into the DAG the orchestrator executes (the fix for "every agent starts at once") |
| `policies/` | Declarative rules evaluated by `engine.py`; adding a policy = adding a data file, not changing engine code |
| `permissions/` | Two faces: human RBAC and *agent* grants (what each role may invoke and see) |
| `budgets/` | Prevents cost explosion; ledger is fed by events so it is auditable |
| `registry/` | Runtime metadata for planning; fed by `agents/base/registration.py` and `tools/registry.py` |
| `supervision/` | The watchdog; runs as a separate consumer process (`app/workers/`) |
| `context_policies/` | Governs the shared blackboard (Section 9); kept in governance, not context, because sharing is a *permission* question |

**Key separation:** governance decides *what may happen*; the orchestrator decides *how it executes*. Governance never runs the graph; the orchestrator never sets policy.

---

## 5. LangGraph Structure

```
app/orchestrator/
├── runner.py                   # Async execution: .astream(), resume from checkpoint, interrupts
├── graph/
│   ├── builder.py              # Assembles StateGraph from nodes/edges (per workflow)
│   ├── nodes/                  # NODE IMPLEMENTATIONS (pure, testable)
│   │   ├── ingest.py           # Accept artifact, register repo context
│   │   ├── scan.py             # Trigger scanner, await RepoIndexed
│   │   ├── agent_node.py       # Generic: enqueue agent task, await AgentFinished event
│   │   ├── discuss.py          # Run discussion phases, enforce thread budget
│   │   └── decide.py           # Release Manager handoff
│   ├── edges/                  # CONDITIONAL ROUTING
│   │   ├── routers.py          # DAG transitions: scan done → which agents, in what order
│   │   └── guards.py           # Preconditions: budget remaining, no blocker, human approval needed
│   └── state/
│       ├── run_state.py        # Graph state schema (TypedDict) — the contract nodes share
│       └── reducers.py         # Merge/reducer functions for list fields (findings, votes)
├── workflow/
│   ├── standard_review.py      # Full DAG: scan → 5 reviewers → discussions → decide
│   └── quick_review.py         # Optional: subset DAG for small diffs (policy-driven)
├── memory/
│   └── checkpointer.py         # Postgres checkpointer factory (thread_id = run_id)
├── dispatcher/
│   ├── queue.py                # Role-scoped task queues (interface)
│   ├── dispatch.py             # Enqueue + await completion events (async node pattern)
│   └── consumer.py             # Worker entry points (spawned by app/workers/)
└── retry/
    ├── policy.py               # Per-node retry/backoff policies (transient vs. permanent errors)
    └── circuit_breaker.py      # Per-role breaker: repeated LLM/tool failure → degraded/fail-fast
```

| Component | Responsibility |
|-----------|----------------|
| `runner.py` | Owns graph invocation, streaming (values/updates/custom), checkpoint resume, `interrupt()` handling |
| `graph/nodes/` | Node implementations; each node is a *pure function of state* → events/queue actions (unit-testable without LangGraph) |
| `graph/edges/` | Conditional routing between nodes; the DAG logic lives here, not in nodes |
| `graph/state/` | The typed shared state contract; reducers define how concurrent agent outputs merge |
| `workflow/` | Reusable graph assemblies (review types); a new workflow = new builder function, no node changes |
| `memory/` | Durable checkpoints so a crash resumes the run (never restarts it) |
| `dispatcher/` | The async bridge: nodes enqueue tasks and *await events* instead of blocking on LLM calls |
| `retry/` | Retry policy separation — transient (LLM 429/5xx) retried; domain errors never retried |

---

## 6. Tool Integration Structure

```
app/tools/
├── base/
│   ├── tool.py                 # ToolProtocol: name, description, input/output schemas, sandbox profile
│   ├── result.py               # ToolResult: stdout, exit_code, duration, artifact refs
│   └── errors.py               # ToolError taxonomy (timeout, forbidden, tool-missing)
├── registry.py                 # name → factory (the plugin point)
├── factory.py                  # Instantiates allowlisted tools from config for a given agent/run
├── sandbox/
│   ├── executor.py             # Sandboxed execution abstraction (container/VM)
│   ├── profiles.py             # Profiles: no-egress, cpu/mem/time caps, tmpfs
│   └── guards.py               # Allowlist enforcement, path jail, artifact capture
├── integrations/               # ONE FOLDER PER TOOL (each a self-contained package)
│   ├── semgrep/                # __init__.py exposes `tool = SemgrepTool()` (plugin contract)
│   ├── bandit/
│   ├── trivy/
│   ├── secret_scanner/
│   ├── docker_analyzer/
│   ├── dependency_scanner/
│   └── github/                 # Clone, PR comments, status checks
└── llm_tools/                  # Non-sandboxed tools: repo-index queries, diff analyzers
```

**How a new tool is added without modifying existing code (open/closed):**

1. Create `app/tools/integrations/{name}/` implementing `base/tool.py` (name, schemas, sandbox profile).
2. Register the factory in `tools/registry.py` (or auto-discover via entry points).
3. Grant it to roles in *policy data* (`governance/permissions/grants.py` or policy records) — no code change.
4. Done. Agents, orchestrator, governance, and the sandbox are untouched.

The registry keeps an **explicit registration** (over magic auto-discovery) at hackathon scale: one obvious place to find every tool, no import-time surprises. The `github/` integration is special — it is the only tool with network egress, so its sandbox profile is "network allowed but scope-limited" and its grants are tightly controlled.

---

## 7. Event System Structure

```
app/events/
├── bus/
│   ├── broker.py               # EventBroker interface (publish, subscribe, replay)
│   ├── redis_broker.py         # Redis Streams implementation (consumer groups, TTL, cursor)
│   └── envelope.py             # Envelope type: event_id, run_id, type, seq, ts, actor, payload, schema_ver
├── models/
│   ├── event.py                # Base Event model (typed)
│   └── definitions.py          # All event type definitions (RunStarted, FindingPublished, …) — the contract
├── publishers/
│   ├── publisher.py            # Publisher interface
│   └── redis_publisher.py      # XADD implementation
├── subscribers/
│   ├── subscriber.py           # Consumer base + @subscribe decorator
│   ├── handlers/               # audit_sink.py, notifier.py, projection_feed.py, projection_timeline.py
│   └── groups.py               # Consumer-group naming/registration
├── streaming/                  # High-frequency projection builders
│   ├── progress.py             # Aggregates RepoScanProgress/AgentProgress → % bars
│   └── presence.py             # Agent heartbeat → roster state
├── notifications/              # Outbound: webhooks, Slack/email (decision.made)
├── feed/                       # Activity-feed projection service
└── timeline/                   # Timeline projection service
```

**How an event flows:**

```
Service/Agent → publishers/publisher.publish(event)          [write-then-publish: Postgres first, then bus]
     → bus/redis_broker (XADD to run:{id}:events)
     → consumer groups:
         • subscribers/handlers/audit_sink      → Postgres audit tables
         • subscribers/handlers/projection_*    → feed/timeline/progress projections
         • websocket/broadcast                  → live push to the frontend
         • governance/supervision/watchdog      → heartbeats, budget ledger
```

Rules: events are **the only way** components observe each other; handlers are idempotent (dedupe on `event_id`); subscribers do **not** perform business logic — they build projections or dispatch to services. `events/models/definitions.py` is the single contract file; producers and consumers import it, so a rename breaks compilation instead of silently diverging.

---

## 8. WebSocket Structure

```
app/websocket/
├── manager.py                 # ConnectionManager: socket registry, per-connection send queues, close handling
├── sessions.py                # SessionManager: authenticated session state, run scoping
├── broadcast.py               # BroadcastManager: event → channels → connections (the fan-out)
├── channels.py                # Channel naming + registry: "run.{run_id}", "run.{run_id}.agent.{role}"
├── subscriptions.py           # Client subscriptions + cursor/resume tracking (last_event_id)
├── protocol.py                # Frame schemas: subscribe, subscribed, event, ping/pong, error, resubscribe
└── handlers.py                # WS endpoint wiring (FastAPI dependency for the /ws/v1/events route)
```

**How live updates reach the frontend:**

```
Event bus (run:{id}:events)
  → broadcast.py (subscriber)  resolves event → channel(s) from payload (run_id, agent, type)
  → manager.py                 finds connections subscribed to those channels
  → protocol.py                serializes envelope → WS frame
  → frontend ws client         idempotent reducer applies event to Zustand store
  → UI components re-render
```

Reconnect: client sends `last_event_id` → `subscriptions.py` maps to bus cursor → replay then live. All WS state is in Redis, so multiple gateway instances are stateless and swappable.

---

## 9. Shared Context Structure

```
app/context/
├── store.py                   # Namespaced get/set/append API with ownership enforcement
├── repo_context.py            # Repo index, metadata, scan results (written by scanner)
├── findings.py                # Findings namespace (agent-owned writes: {agent}.{finding_id})
├── evidence.py                # Evidence registry: artifact refs, raw model dumps
├── memory/                    # Shared working memory
│   ├── working_memory.py      # Short-term notes agents may read (with grants)
│   └── summarizer.py          # Rolling summaries to bound context size
├── threads/                   # Discussion threads (append-only)
│   ├── thread.py              # Thread state, budget counters (rounds, timebox)
│   └── messages.py            # Question/Answer/Agreement/Disagreement messages
├── conversation/              # Conversation history per thread (for LLM windowing)
└── sync/                      # Synchronization engine
    ├── ownership.py           # Enforces write ownership per namespace
    ├── versioning.py          # rev/etag on writes; conflict rules
    └── projections.py         # Derived aggregates (vote tallies, progress) computed on read
```

**Synchronization rules** (the reason it doesn't corrupt itself):

1. **Single-writer namespaces** — agent writes only its own `findings` prefix; the scanner owns `repo_context`; the Release Manager owns the decision.
2. **Append-only threads** — messages are immutable; edits are new messages.
3. **Versioned writes** — every mutation carries `rev`; stale writes are rejected, not silently merged.
4. **Derived-on-read** — counts/tallies are computed from the event stream at read time, never stored (no stale aggregates, no write races).
5. **Write-then-publish** — context mutations commit to Postgres first, then emit the corresponding event (the same event the dashboard projects).
6. **Grant enforcement** — read/write scopes come from `governance/context_policies/`, applied in `store.py`.

---

## 10. Frontend Structure

```
frontend/
├── public/                       # Static assets served as-is
├── src/
│   ├── main.tsx                  # React root
│   ├── App.tsx                   # Providers (router, auth, ws, theme) composition
│   ├── router.tsx                # Route table (upload, run/war-room, history, admin, auth)
│   ├── layouts/                  # Shell layouts: AppLayout, WarRoomLayout (grid of panels)
│   ├── pages/                    # Route-level pages (thin: compose layouts + feature components)
│   │   ├── upload/               # Repo upload + start-review flow
│   │   ├── run/                  # The War Room page (live review)
│   │   ├── history/              # Past runs list/detail (replay)
│   │   ├── admin/                # Policies, agents, budgets, tool grants
│   │   └── auth/                 # Login / session
│   ├── components/
│   │   ├── ui/                   # shadcn/ui generated primitives (button, card, dialog, …)
│   │   ├── shared/               # Domain-agnostic app components (StatusPill, SeverityBadge, Spinner, EmptyState)
│   │   └── features/             # FEATURE MODULES (each owns its components + hooks)
│   │       ├── agent-dashboard/  # Agent roster cards: status, token meter, tool calls
│   │       ├── timeline/         # Vertical phase timeline; jumps to evidence/findings
│   │       ├── activity-feed/    # Slack-like event feed; auto-scroll, pause on hover
│   │       ├── repo-explorer/    # File tree + language/risk chips from repo index
│   │       ├── findings/         # Findings board: severity/confidence badges, "contested" markers
│   │       ├── evidence/         # Evidence viewer: scan snippets, tool outputs, model dumps
│   │       ├── discussion/       # Q&A threads with agree/disagree + resolution state
│   │       ├── decision/         # Final verdict banner: score breakdown, dissent, evidence links
│   │       └── charts/           # Progress bars, cost/status charts (Recharts or lightweight)
│   ├── hooks/                    # Shared cross-feature hooks (useRunStream, useFindings, useReconnect)
│   ├── contexts/                 # React contexts: AuthContext, RunContext, WsContext
│   ├── services/
│   │   ├── api/                  # REST client + typed endpoint modules (runs, findings, …)
│   │   └── ws/                   # WebSocket client: connect, resume cursor, reconnect, heartbeats
│   ├── stores/                   # Zustand stores + the idempotent event reducer
│   ├── lib/                      # Utilities: formatting, time, cn(), query keys
│   ├── types/                    # Shared TS types (generated from backend OpenAPI/Pydantic)
│   └── config/                   # Env config: API/WS base URLs, feature flags
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.ts
├── components.json               # shadcn/ui configuration
└── package.json
```

| Module | Responsibility |
|--------|----------------|
| `pages/` | Route-level composition only — no business logic |
| `layouts/` | Shells; the War Room layout is the product centerpiece (grid: feed, roster, timeline, findings, threads, decision banner) |
| `components/ui/` | Generated shadcn primitives — never hand-edit beyond theming |
| `components/shared/` | Reusable, domain-agnostic visuals |
| `components/features/` | Feature slices; the mapping to backend concerns is 1:1 (`findings/` ↔ `findings.py` routes) |
| `hooks/` + `contexts/` | Cross-cutting React logic shared by features |
| `services/api/` | Typed REST client (TanStack Query-compatible); base URL from `config/` |
| `services/ws/` | The critical live layer: resume-cursor logic, reconnect with backoff, event dedupe |
| `stores/` | Zustand stores + the event reducer — the UI's projection engine |
| `types/` | **Generated** from backend schemas (openapi-typescript), never hand-written — prevents drift |
| `lib/` | Pure utilities only |

---

## 11. Database Layer Structure

```
app/database/
├── base.py                    # DeclarativeBase (single metadata for Alembic autogenerate)
├── session.py                 # Async engine + session factory (from config)
├── migrations/                # Alembic
│   ├── env.py
│   └── versions/              # One file per migration (timestamped, reviewed)
└── seeders/                   # Dev seed data (demo runs, sample policies)

app/models/                    # ORM entities, grouped by domain module (NOT by layer)
├── __init__.py                # Central import hub — Alembic and repositories import from here
├── identity/                  # users, teams, roles, api_tokens
├── runs/                      # runs, plan_nodes, plan_edges, run_assignments
├── repos/                     # the uploaded software repositories + uploads
├── findings/                  # findings, evidence, finding_links
├── discussions/               # threads, thread_messages, votes
├── decisions/                 # decisions, decision_reasons, decision_overrides
├── policies/                  # policies, budgets, tool_allowlists
└── audit/                     # audit_events (append-only)
```

**Organization rules (no tables designed yet — this is the layer contract):**

- **`database/` is infrastructure** (engine, sessions, migrations, seeds); **`models/` is domain** (entities). They are separate folders because they change for different reasons.
- Models are grouped **by domain module, not by layer** — this keeps a feature's entities discoverable together and mirrors `schemas/` and `services/` grouping.
- `schemas/` (Pydantic) never imports `models/` (ORM): the API shape is decoupled from the storage shape; repositories map between them.
- **Supabase note:** Supabase provides the hosted Postgres; the app connects via the async SQLAlchemy engine in `database/session.py`. Supabase's own Auth/Realtime are *not* used for app features (we run our own auth + WS) — only the database tier is consumed. Migrations are applied by the backend (Alembic), not Supabase UI.
- `migrations/versions/` are code-reviewed like any other diff; the schema evolves by migration, never by hand-editing the DB.

---

## 12. Documentation Structure

```
docs/
├── architecture/               # System design docs (embed ../diagrams sources), data-flow guides
├── api/                        # OpenAPI reference + endpoint usage guides (generated from backend)
├── development/                # Getting started, coding standards, how-tos (add a tool, add an agent)
├── deployment/                 # Docker, Supabase setup, environment variable reference
├── prompts/                    # Guide to the prompt library (structure, versioning policy, review flow)
└── agents/                     # Agent specifications: role, tools, outputs, budgets, model tiers
```

Plus root folders that complete the documentation surface:

| Folder | Documents | Audience |
|--------|-----------|----------|
| `architecture/` | `ARCHITECTURE.md`, `REPOSITORY_STRUCTURE.md`, ADRs | Engineers — long-lived, versioned, rarely edited |
| `diagrams/` | Mermaid/drawio sources | Engineers — edited when design changes |
| `prompts/` | The prompt artifacts themselves | Prompt engineers + reviewers — *code-reviewed* |
| `docs/architecture/` | Derived design explainers | Onboarding engineers |
| `docs/api/` | API reference | Frontend + external integrators |
| `docs/development/` | How-to guides | All developers |
| `docs/deployment/` | Ops runbook | SRE/DevOps |
| `docs/agents/` | Agent specs | Agent contributors (often non-generalists) |
| `docs/prompts/` | Prompt library guide | Prompt engineers |

**Why this split:** `architecture/` and `prompts/` are **source artifacts** with review lifecycles; `docs/` is **maintained reference**. Mixing them buries decision records under how-tos and lets prompts drift from code. Each audience gets one clear entry point.

---

## 13. Testing Structure

```
tests/                          # CROSS-APP
├── e2e/                        # Playwright: upload → war room → live updates → decision (full journeys)
└── fixtures/                   # Sample repos, canned event sequences, war-room snapshots

backend/tests/                  # MIRRORS app/ — find tests by walking the same path
├── conftest.py                 # Fixtures: db session, redis, ws client, fake LLM, sandbox stub
├── unit/                       # services/, governance/, orchestrator/, agents/, tools/, events/, context/
├── integration/                # Postgres + Redis + storage together (real containers)
├── api/                        # Endpoint tests via FastAPI TestClient/httpx
├── websocket/                  # WS protocol: subscribe, cursor resume, replay, reconnect
├── reports/                    # Report builder snapshots
└── factories/                  # Builders for models/events (test data generators)

frontend/                       # COLOCATED unit tests (Vitest + Testing Library)
├── src/components/features/findings/findings.test.tsx
├── src/stores/event-reducer.test.ts
└── src/services/ws/ws-client.test.ts
```

| Test type | Where | Covers |
|-----------|-------|--------|
| Backend unit | `backend/tests/unit/` | Pure logic per layer (nodes, policies, reducers, projections) |
| Agent tests | `backend/tests/unit/agents/` | Agent loop with **fake LLM + stubbed sandbox**: prompt adherence, tool allowlist, budget cutoff |
| API tests | `backend/tests/api/` | Routes, auth, validation, error mapping |
| Integration | `backend/tests/integration/` | DB + event bus + storage together; write-then-publish ordering |
| WebSocket | `backend/tests/websocket/` | Protocol correctness incl. resume/replay edges |
| Frontend unit | colocated in `frontend/` | Components, the event reducer (the critical logic), WS client |
| E2E | `tests/e2e/` | User journeys against the real stack (docker-compose) |

---

## 14. Naming Conventions

| Artifact | Convention | Example | Notes |
|----------|-----------|---------|-------|
| Root/script folders | `kebab-case` | `infrastructure/` | Lowercase, no underscores in root |
| Python packages/folders | `snake_case` | `security_officer/` | PEP 8 |
| Frontend folders | `kebab-case` | `activity-feed/` | Vite/shadcn convention |
| Python files | `snake_case.py` | `plan_builder.py` | |
| React component files | `PascalCase.tsx` | `FindingsPanel.tsx` | Matches the exported class/function name |
| Hook files | `useXxx.ts` | `useRunStream.ts` | |
| Plain TS modules | `kebab-case.ts` | `ws-client.ts` | |
| Python classes | `PascalCase` | `PlanBuilder` | |
| Python functions/vars | `snake_case` | `build_plan()` | |
| TS functions/vars | `camelCase` | `buildPlan()` | |
| Constants | `UPPER_SNAKE_CASE` (py) / `UPPER_CASE` (ts) | `MAX_ROUNDS` | |
| DB model classes | `PascalCase` | `Finding` | |
| DB tables | `snake_case`, plural | `findings` | Explicit `__tablename__` |
| API endpoints | lowercase `kebab-case`, plural nouns, `/api/v1` prefix | `POST /api/v1/runs/{id}/cancel` | Action suffix for verbs, never verbs in resource names |
| Pydantic schemas | `PascalCase` | `FindingCreate` / `FindingRead` | Action suffix for create/read/update |
| Event types | `PascalCase`, past tense + noun | `RunStarted`, `FindingPublished` | Enum: `EventType.RUN_STARTED` |
| WS channels | dot-delimited, run-scoped | `run.{run_id}`, `run.{run_id}.agent.{role}` | Replaces slashes/colons (readable in logs) |
| Repositories (data access) | `XRepository` | `FindingRepository` | Distinguished from `repos/` (uploaded software) — see §19 |

---

## 15. Coding Standards

| Concern | Standard | Enforcement |
|---------|----------|-------------|
| Formatting | Python: Ruff format. TS: Prettier (incl. Tailwind class sorting plugin) | pre-commit + CI |
| Linting | Python: Ruff (flake8 rules + isort group). TS: ESLint + typescript-eslint | pre-commit + CI |
| Type safety | Python: mypy (strict for `app/`). TS: `strict: true`; types generated from backend schemas | CI gate |
| Import organization | stdlib → third-party → first-party → local, no circular imports (layer rule from §2.2) | Ruff rule + CI check |
| Logging | Structured JSON; every record carries `run_id`, `event_id` (correlation); never log secrets | Logging config in `app/logs/`; review rule |
| Error handling | Typed domain exceptions in `core/`; FastAPI handlers map to RFC 7807; transient (LLM/network) retried, domain errors never; agent/tool errors use their own taxonomies | API tests assert error shapes |
| Config management | 12-factor: pydantic-settings, defaults → `.env` → environment; secrets via env/vault only, never in code or committed `.env` | `.env.example` is the only committed env file |
| Prompts | Artifacts in `prompts/`, versioned, CI-asserted identical to `agents/*/prompt.py` | CI diff check |

---

## 16. Architecture Rationale

**Why this exact shape:**

- **Monorepo with independent containers.** Atomic cross-cutting changes (a finding feature touches backend + frontend + docs in one PR) while both apps stay independently deployable — the property "monorepo" must preserve.
- **Clean Architecture layering, not package-by-layer.** Folders group by concern (`services/`, `repositories/`) *and* vertical feature awareness (agents, governance, events are peers, not afterthoughts). AI-specific code is isolated from generic platform code so the platform is testable without any LLM.
- **Agents as vertical slices.** The most volatile surface (prompts, model config, role logic) is quarantined per role; the shared base keeps the loop consistent.
- **Events as a first-class module.** The live dashboard *is* the product; the event system is a peer module with its own models/publishers/subscribers so projections (feed, timeline, progress) are explicit and swappable.
- **Tools behind a plugin registry.** External tools are the fastest-moving, most heterogeneous surface; the registry + sandbox profile abstraction keeps them addable without touching orchestration.
- **Governance separated from orchestration.** Policy (what may happen) vs. execution (how it runs) are different change frequencies; splitting them means policy changes never risk the graph, and graph changes never touch policy.
- **Contracts over convention.** Pydantic schemas ↔ generated TS types ↔ event definitions in one place — rename breaks the build, not the runtime.

---

## 17. Scalability Considerations

| Dimension | How the structure supports it |
|-----------|------------------------------|
| **Agent throughput** | Role-scoped worker queues (`orchestrator/dispatcher/`) let each role scale independently; `app/workers/` processes deploy separately from the API |
| **Event volume** | `events/bus/` is broker-agnostic (Redis Streams now, NATS/Kafka later) — the adapter swap is contained |
| **WS fan-out** | Stateless gateways (`websocket/`) with Redis-backed session state scale horizontally without sticky sessions |
| **Codebase growth** | Layer lint rule + vertical slices prevent the "god module"; a new agent = new slice, a new tool = new package |
| **Multi-tenancy** | Tenant scoping lives in `core/` (constants/context) + repositories + `events` (run-scoped streams) — add `tenant_id` discipline at the boundary, not per-feature |
| **Data growth** | Migrations-as-code; `repositories/` isolate query changes; projections make read models independently scalable |
| **Model cost** | `llm/` is the single choke point for budgets/fallbacks — cost controls are one module, not scattered |
| **New review types** | `orchestrator/workflow/` — a new DAG is a builder function, nodes are reused |

---

## 18. Best Practices

1. **Layers are load-bearing.** The §2.2 dependency rule is enforced in CI; drift is a bug, not a style choice.
2. **API shape ≠ DB shape.** `schemas/` and `models/` never import each other; repositories map between them.
3. **Write-then-publish.** Postgres commit before event publish keeps snapshot and stream convergent.
4. **Events are contracts.** `events/models/definitions.py` is reviewed like an API — it is one.
5. **Prompts are reviewed artifacts**, diffable in `prompts/`, identical to what the code loads (CI-asserted).
6. **Fake the LLM in tests.** Agent tests run against a fake gateway + stubbed sandbox; determinism beats fidelity.
7. **Frontend types are generated** from backend schemas; hand-written types drift.
8. **Everything configurable is config** (budgets, allowlists, model tiers) — policy data, not code.
9. **One entry point per subsystem** (`governance/controller.py`, `context/store.py`) — internals stay private.
10. **12-factor config** — no config in code, no secrets in the repo, `.env.example` is the contract.

---

## 19. Common Mistakes to Avoid

1. **Layers calling across** — `api/` hitting `models/` directly; dies via the CI lint rule.
2. **Circular imports between `schemas/` and `models/`** — keep them one-directional (schemas never import models).
3. **Business logic in event subscribers** — subscribers project or dispatch; they don't decide.
4. **Business logic in frontend components** — pages/features stay dumb; logic lives in stores/services/hooks.
5. **Name collision: `repos/` (uploaded software) vs `repositories/` (data access).** Rename the data-access layer to `repositories/` (as done) and *never* abbreviate "software repositories" to the same word inside `models/` (`models/repos/`) — this is already the most confusing pair in the tree; keep it documented in `docs/development/`.
6. **Prompts embedded in agent logic** — they must be artifacts; otherwise prompt changes skip review and drift.
7. **Hand-written frontend types** — they drift and burn debugging hours.
8. **Migrations by hand** — schema changes only via Alembic versions.
9. **Logging without correlation IDs** — every log must carry `run_id`/`event_id`; JSON logging configured once.
10. **Secrets in committed `.env`** — `.env` is gitignored; `.env.example` is the committed template.
11. **Splitting agents by layer instead of slice** — `prompts.py`, `tools.py`, `config.py` at the top level of `agents/` shared across roles recreates the tangled mess §3.2(A) warns about.
12. **Ignoring the WS resume path** — cursor/replay is the hardest WS bug class; it gets dedicated tests in `backend/tests/websocket/`.

---

## 20. Recommendations for Future Expansion

- **Extract agents to packages** when a role's lifecycle outgrows the monorepo (the vertical-slice shape makes this a move, not a rewrite).
- **Swap the bus** (Redis Streams → NATS/Kafka) behind `events/bus/broker.py` when volume demands it; add replay/audit compaction.
- **Add a models registry** (pinned versions, A/B arbitration) inside `llm/` as model diversity grows.
- **Observability stack** (OpenTelemetry + tracing) wired through `middleware/` and `workers/` before launch — retrofit is painful.
- **Multi-tenant SaaS packaging**: tenant context in `core/`, per-tenant budgets in `governance/budgets/`, tenant-scoped streams in `events/` — the boundaries already exist.
- **Diff-based re-review** (re-run only changed modules) as a new `orchestrator/workflow/` variant; the DAG builder makes this additive.
- **CLI + webhooks** as new consumers of the same events — the event contract is the integration surface.
- **Marketplace for tools** — the `tools/integrations/` plugin shape becomes the shipping unit.
- **Relocate `ARCHITECTURE.md`/`REPOSITORY_STRUCTURE.md` into `architecture/`** once the repo is scaffolded, keeping ADRs alongside them.
