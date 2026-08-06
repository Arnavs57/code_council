# Code Council AI — Configuration & Platform Foundation

**Phase:** 1.5 · **Tasks 1–2:** Configuration Architecture + Configuration Folder Design (design only)
**Status:** Proposed (v1.0) · **Companion to:** `ARCHITECTURE.md`, `REPOSITORY_STRUCTURE.md`

---

## 0. Executive Summary

This document designs the **centralized configuration system** that becomes the
single source of truth for every future module. Two hard rules:

1. **No module calls `os.getenv()`** — all configuration is read through the
   platform's configuration layer.
2. **No module hardcodes configuration values** — everything configurable lives
   in typed settings, validated at boot, resolved from environment-aware
   sources.

The design builds on the Phase 1.3 foundation (`app/config/settings.py`,
`environment.py`, `config.py`), which already provides typed Pydantic settings
with a `CCAI_` prefix, environment detection and fail-fast validation. Phase 1.5
**extends** that foundation with: modular settings namespaces (per future
module), frozen/immutable settings, a secret resolver seam, redacted startup
audit, and a lint rule that enforces the "no raw env access" rule.

---

## 1. Configuration Lifecycle

```
┌──────────────────────────────────────────────────────────────────────┐
│ 1. STATIC BASELINE     core/constants.py — compile-time defaults      │
│        (app name, version, limits, paths — never read from env)      │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
│ 2. BOOTSTRAP            environment.py — detect environment           │
│        (CCAI_ENVIRONMENT, validate ∈ {development, testing,           │
│         production}, resolve env file: .env.<env> → .env)             │
                                ▼
│ 3. LOAD                 settings.py — merge layers by precedence      │
│        (constructor args > process env incl. secrets > env file       │
│         > field defaults)                                             │
                                ▼
│ 4. VALIDATE             Pydantic parse + field/cross-field validators │
│        (any error → ConfigurationError → process exits, never boots)  │
                                ▼
│ 5. FREEZE               settings frozen (immutable) post-load         │
                                ▼
│ 6. AUDIT                redacted startup log: which sources won,      │
│        which values are set (secrets masked)                          │
                                ▼
│ 7. CONSUME              modules import `settings` from the platform   │
│        (or receive it injected); they never read env/files directly   │
                                ▼
│ 8. ROTATE / UPDATE      secrets rotate on process restart (K8s/Docker)│
│        Future: dynamic feature-flag layer via a ConfigProvider seam   │
└──────────────────────────────────────────────────────────────────────┘
```

**Design points:**

- **Boot is the only place config is read.** After step 5 the process has one
  immutable view; there is no "read config on demand" anywhere else.
- **Config never changes mid-run in this phase.** Rotating secrets take effect
  on restart. A `ConfigProvider` interface (Section 9) is the seam where a
  live/feature-flag layer plugs in later — consumers are unaffected either way.
- **Audit before serving.** The startup log records the effective environment
  and which layers contributed values (with secrets masked), so operators can
  answer "what config is this pod actually running with?" from logs alone.

---

## 2. Loading Strategy

### 2.1 Precedence (highest wins)

| # | Layer | Source | Used in |
|---|-------|--------|---------|
| 1 | **Explicit overrides** | Constructor args (`Settings(_env_file=None, ...)`) | Tests, CLI/diagnostic tools |
| 2 | **Process environment** | `CCAI_*` vars — including values injected from Docker/K8s/Vault secrets | Every environment |
| 3 | **Environment file** | `.env.<environment>` → fallback `.env` (development/testing only) | Local dev, CI |
| 4 | **Defaults** | Field defaults + `core/constants.py` | Fallback, documented contract |

### 2.2 Sources per environment

| Concern | Development | Testing | Docker | Kubernetes / Cloud |
|---------|-------------|---------|--------|--------------------|
| Env file | `.env.development` (committed only as `.env.example`) | none — tests set env vars / constructor args | none | none |
| Non-secret values | `.env` file | env vars / args | `environment:` in compose | **ConfigMap** |
| Secrets | `.env` (gitignored) | test fixtures (non-real) | `env_file:` / `secrets:` in compose | **Secret** (mounted as env or files) |
| Interactive docs | on | on | off | off |
| Debug | true (derived) | false | false | false |

**Key rule:** environment files are a *developer convenience*, never a
production mechanism. Production config arrives exclusively through real
environment variables (or mounted secret files), which is exactly what
12-factor and Kubernetes expect.

### 2.3 Namespacing

Settings use **one root prefix with per-module sub-namespaces**, so a future
module can be configured without touching anyone else's keys:

```
CCAI_               root (app name, version, environment, debug, api prefix)
CCAI_LOG_           logging (level, console, file, rotation)
CCAI_DB_            database  (Phase 2: URL, pool size, echo)
CCAI_BUS_           event bus (Phase 3: Redis URL, stream TTL)
CCAI_LLM_           LLM gateway (Phase 3: providers, model tiers, budgets)
CCAI_GOV_           governance (Phase 3: budget ceilings, limits)
CCAI_TOOLS_         tool registry (Phase 3: allowlists)
CCAI_PLUGIN_*_      plugins (any future contributor)
```

Each namespace maps to a **nested Pydantic model** (Section 7), so `settings.llm`
is a typed object, not a pile of loose strings.

---

## 3. Validation Strategy

Validation happens **once, at load**, and is enforced by Pydantic v2:

| Category | Mechanism | Example |
|----------|-----------|---------|
| Type safety | Annotated fields | `port: int`, `cors_origins: list[str]` |
| Enumerated values | `Literal` / enum + validator | `environment ∈ {development, testing, production}` |
| Format checks | Shared validators in `config/validators.py` | URL, port range (1–65535), non-empty, boolean parsing |
| Cross-field rules | `model_validator(mode="after")` | `debug` derived from environment when unset |
| Security classification | `SecretStr` / `SecretBytes` | API keys, DB passwords — never serialize as plaintext |
| Required secrets | Sentinel + validator | A prod-only required key missing → `ConfigurationError` |
| Unknown keys | `extra="ignore"` | Forward-compatible: old env vars don't crash new versions |

**Validation is uniform across environments.** Only the *sources* differ per
environment, never the schema — so "works on my machine" failures are exactly
the failures production will report, just earlier and with better ergonomics.

---

## 4. Fail-Fast Strategy

1. **Boot-time, import-time failure.** Any validation error raises during
   application import (the `settings` singleton is built before the FastAPI app
   is created). The process never starts serving with invalid config — a crash
   with a clear message beats a half-configured deployment every time.
2. **Environment mismatch is fatal.** An unknown `CCAI_ENVIRONMENT` raises
   (`ValueError` from `environment.py`, validated again in the settings schema).
   There is no "guess" mode and no implicit production fallback.
3. **Production guards.** Production disables interactive docs and forces
   `debug=false`; a future guard will refuse to boot in production with debug
   enabled or with a default secret value.
4. **Deterministic errors.** All configuration errors surface as typed
   `ConfigurationError` exceptions (from `app/core/exceptions.py`) so failure
   paths are testable and the error envelope is consistent.
5. **Redacted failure output.** Error messages never include secret values —
   only key names and the rule that failed.

---

## 5. Dependency Flow

```
                 ┌───────────────────────────────┐
                 │        core/constants.py      │  static, dependency-free
                 └───────────────┬───────────────┘
                                 │ (imports)
                 ┌───────────────▼───────────────┐
                 │        app/config/            │  the ONLY reader of
                 │  environment → settings →     │  env vars, env files,
                 │  secrets → audit              │  and secrets
                 └───────────────┬───────────────┘
                                 │ exposes: `settings` (frozen singleton)
     ┌──────────┬───────────┬────┴────┬───────────┬───────────┬──────────┐
     ▼          ▼           ▼         ▼           ▼           ▼          ▼
   api/      services/   agents/   governance/ orchestrator/  events/  websocket/
   database/ tools/      llm/      middleware/  logs/        (every future module)
```

**Rules (enforced by linting):**

- **Only `app/config/` may touch `os.environ`, env files, or secret sources.**
  A lint rule (Section 8) treats `os.getenv`, `os.environ[...]`, and
  `load_dotenv` anywhere else as a build failure.
- **Everything imports `settings` from `app.config.config`** (or receives it
  injected). No module re-implements precedence, parsing or validation.
- **`config/` depends only on `core/`** (constants, exceptions) and the
  standard library — it sits at the bottom of the graph, so nothing cycles.
- **One public surface.** `app/config/__init__.py` re-exports `settings` and
  `get_settings()`; internal modules (`validators`, `secrets`, `audit`) are
  importable but not part of the contract.

---

## 6. Target Module Layout (Phase 1.5 implementation shape)

```
app/config/
├── __init__.py          # public surface: settings, get_settings
├── bootstrap.py         # build_settings(): load → validate → freeze → audit
├── environment.py       # environment detection + env-file resolution (exists)
├── settings.py          # root Settings: composition of namespaces (extends)
├── namespaces/          # one nested model per future module
│   ├── core.py          # app identity, debug, api prefix, docs
│   ├── logging.py       # level, console/file handlers, rotation
│   ├── database.py      # Phase 2: URL, pool, echo
│   ├── bus.py           # Phase 3: redis URL, stream TTL, group names
│   ├── llm.py           # Phase 3: providers, model tiers, budgets
│   └── governance.py    # Phase 3: limits, defaults
├── secrets.py           # SecretResolver interface (env-backed now; Vault later)
├── audit.py             # redacted startup config report
└── validators.py        # shared field validators (url, port, non-empty, csv)
```

**Why namespaces, not one big model:** every future module (database, event
bus, LLM gateway, governance, tools, plugins) adds its own config surface. A
single flat `Settings` would grow unbounded and force unrelated merge conflicts.
Nested models give each module one owned file, one prefix, and full type
safety — while the root object stays the single import point.

---

## 7. Secret Management Strategy

| Concern | Decision | Rationale |
|---------|----------|-----------|
| Storage | Never in code, never in committed files | `.env` is gitignored; only `.env.example` is committed (with `CHANGE_ME` placeholders) |
| Classification | `SecretStr`/`SecretBytes` fields | Redaction is structural, not accidental: serialization masks values |
| Delivery (dev) | `.env` file, gitignored | Local convenience |
| Delivery (Docker) | `env_file:` / `secrets:` in compose | Compose-native secret injection |
| Delivery (K8s/cloud) | **Secret** mounted as env vars (or files), **ConfigMap** for non-secret | Standard cloud-native separation; values visible to the process only |
| Rotation | On process restart | Simple, deterministic; no mid-run secret re-read needed in this phase |
| Future | `SecretResolver` interface → Vault/KMS adapter | The seam exists now; swapping the backend touches one file |

**Non-negotiable:** secret *names* may appear in logs; secret *values* never do
(masked as `***` in the audit report and error messages).

---

## 8. Enterprise Best Practices

1. **12-factor config** — config lives in the environment, not the codebase.
2. **Single source of truth** — one `settings` object; no ad-hoc env reads.
3. **Typed & validated at boot** — configuration errors are programming errors
   to the platform: deterministic, testable, fail-fast.
4. **No raw env access** — enforced by a lint rule (ruff custom rule or
   `flake8-banned-api`) banning `os.getenv` / `os.environ` / `load_dotenv`
   outside `app/config/`. This is a *mechanical* guarantee, not a code-review
   hope.
5. **Secrets externalized and classified** — SecretStr everywhere, values never
   logged, delivery via platform secret stores.
6. **Immutable after load** — `frozen=True` on the settings model; nobody can
   accidentally mutate global config at runtime.
7. **Config audit at startup** — redacted report logged on every boot.
8. **Tests override through the API** — tests use constructor args and
   `get_settings.cache_clear()` + env vars, never by editing code.
9. **Config-as-code defaults** — defaults live in `core/constants.py` and are
   reviewed like code; the `.env.example` is the documented contract.
10. **Schema versioning** — `settings.schema_version` lets future migrations
    detect and reject stale config generations.
11. **Documentation from schema** — Pydantic field descriptions generate the
    configuration reference; docs can never drift from the code.

---

## 9. Future Extensibility

| Future need | How the design absorbs it |
|-------------|---------------------------|
| **AI providers (LLM gateway)** | `namespaces/llm.py` + `CCAI_LLM_*`: per-provider keys (classified), model tiers, budget ceilings, fallback chains — no consumer changes |
| **Plugin system** | Each plugin registers its own namespace model + prefix (`CCAI_PLUGIN_<name>_*`) at the root composition; the loader discovers them |
| **Docker** | Env injection via compose `environment:`/`env_file:`; secrets via `secrets:` |
| **Kubernetes / cloud** | ConfigMap for non-secret, Secret (env/file) for secrets; ConfigMap updates → restart; no code change |
| **Feature flags / dynamic config** | `ConfigProvider` interface behind the same `settings` surface; a future flags backend (e.g. LaunchDarkly, a `flags` table) implements it without touching consumers |
| **Multi-tenant** | Tenant-level overrides become a *runtime* layer on top of the immutable base (same provider seam) |
| **Vault / KMS** | `SecretResolver` adapter swap — one file |

---

## 10. Challenged Decisions & Alternatives

A formal review of this design (and the options it rejected):

**C1. Monolithic Settings vs modular namespaces.**
*Challenge:* One flat settings class is simpler and satisfies today's needs.
*Resolution:* Rejected for growth: database/bus/LLM/governance/tools/plugins
each add config surface; a flat model becomes a merge-conflict magnet. Nested
namespaces cost little now and save a refactor later. **Chosen: namespaces.**

**C2. Single `CCAI_` prefix vs per-module prefixes.**
*Challenge:* One prefix is simpler to document.
*Resolution:* Both are needed: `CCAI_` root + `CCAI_<MODULE>_` children.
Per-module prefixes prevent key collisions as modules (and plugins) multiply
and make "which module owns this key" obvious. **Chosen: hierarchical.**

**C3. Hot reload now vs at boot only.**
*Challenge:* "Enterprise platforms support live config" is a common demand.
*Resolution:* Deliberately deferred. Mid-run mutation of settings creates
non-deterministic behavior, a class of bugs this platform cannot afford in a
governance product. Restart-based rotation is simple and correct; the
`ConfigProvider` seam keeps the option open. **Chosen: boot-time + seam.**

**C4. Singleton vs dependency injection.**
*Challenge:* Singletons are hard to test; DI is "purer".
*Resolution:* Both, by role: a frozen cached singleton for read-mostly global
config (the 99% case), and constructor injection for the rare service that
needs per-test overrides. Dogma on either side would add friction for no gain.
**Chosen: hybrid.**

**C5. Warn vs fail on invalid config.**
*Challenge:* "Warn and continue" keeps dev moving.
*Resolution:* Rejected — fail-fast uniformly. Boot-time failure is cheap,
deterministic and unambiguous; a half-configured deployment in production is
none of those things. **Chosen: fail-fast.**

**C6. Environment files in production.**
*Challenge:* Some stacks ship `.env` everywhere.
*Resolution:* Rejected. Env files are a local-dev convenience; production runs
on real env vars / secrets, which is what Docker and Kubernetes expect.
**Chosen: env files dev/test only.**

**C7. Loose env access with "review will catch it".**
*Challenge:* "We'll just be careful."
*Resolution:* Rejected — a lint rule makes the `os.getenv` ban mechanical.
Review-based rules decay; build-time rules don't. **Chosen: enforced.**

**C8. Secret values in the audit log.**
*Challenge:* "We need to debug why the DB failed."
*Resolution:* Rejected. The audit logs key names, sources and redacted
presence, never values; debugging uses the secrets store's own audit trail.
**Chosen: redacted audit.**

---

## 11. What Exists vs What Phase 1.5 Adds

| Concern | Phase 1.3 (done) | Phase 1.5 (this phase) |
|---------|------------------|------------------------|
| Typed settings | `Settings` class, `CCAI_` prefix | Nested namespaces per module |
| Environment detection | `environment.py` (env var + env file) | unchanged (stable contract) |
| Validation | Field validators (env, log level, cors) | Shared validator library + cross-field rules + required-secret sentinels |
| Fail-fast | At import | Explicit `bootstrap.py` + typed `ConfigurationError` everywhere |
| Immutability | — | `frozen=True` |
| Secrets | none yet | `SecretStr` fields + `SecretResolver` seam + redaction |
| Audit | startup log lines | Redacted configuration report on boot |
| Env-access ban | none | Lint rule (ruff/flake8-banned-api) |
| Consumption rule | modules import `settings` | same, now documented + lint-enforced |

---

## 12. Task 2 — Configuration Folder Design

### 12.0 Target Layout

```
backend/app/config/
├── __init__.py          # PUBLIC SURFACE  — re-exports settings, get_settings, types
├── config.py            # LOADER          — lru_cached get_settings(); builds frozen singleton
├── environment.py       # ENV DETECTION   — CCAI_ENVIRONMENT, .env.<env> → .env resolution
├── settings.py          # ROOT SCHEMA     — composes all namespaces; cross-field rules
├── bootstrap.py         # LIFECYCLE       — load → validate → freeze → audit (fail-fast entry)
├── constants.py         # CONFIG VOCAB    — prefixes, key names, file names, sentinels
├── paths.py             # PATH RESOLVER   — anchored paths (backend root, logs, uploads, tmp)
├── validators.py        # SHARED CHECKS   — url, port, csv, non-empty, presence
├── features.py          # FEATURE FLAGS   — typed flag schema + ConfigProvider seam
├── secrets.py           # SECRET RESOLVER — SecretResolver protocol + env-backed impl
├── audit.py             # REDACTED REPORT — what is set, from which layer, values masked
├── providers.py         # PROVIDER CONTRACT  — provider definitions (types, tiers, budgets)
├── provider_registry.py # PROVIDER CATALOG   — id → definition; uniqueness/type validation
├── provider_factory.py  # PROVIDER BUILDER   — construct from registry (wiring lands Phase 3)
└── namespaces/          # NESTED SCHEMAS — one owned file per future module
    ├── __init__.py
    ├── core.py          # app identity, debug, docs, api prefix        [now]
    ├── logging.py       # level, handlers, rotation, console/file     [now]
    ├── database.py      # Phase 2 — URL, pool, echo                   [reserved]
    ├── bus.py           # Phase 3 — stream, groups, TTL               [reserved]
    ├── llm.py           # Phase 3 — provider selection, tiers, caps  [reserved]
    └── governance.py    # Phase 3 — ceilings, limits                  [reserved]
```

Files marked `[now]` are implemented in this phase; `[reserved]` are slots whose
schemas land in their own phases — the folder exists so nothing restructures later.

### 12.1 Responsibility of Every File

| File | Responsibility | Depends on | Phase |
|------|----------------|-----------|-------|
| `__init__.py` | The **only public import surface**. Re-exports `settings`, `get_settings()`, and the namespace types. Internal modules (`validators`, `secrets`, `audit`, `providers*`) stay importable but outside the contract. | — | now |
| `config.py` | **Loader**. `get_settings()` with `lru_cache` — the single entry that builds the frozen `settings` singleton after bootstrap. Already exists; gains freeze + audit calls. | environment, bootstrap | now |
| `environment.py` | **Environment detection**. Reads `CCAI_ENVIRONMENT`, validates against the enum, resolves `.env.<env>` → `.env`. Already exists; contract stable. | core/constants | now |
| `settings.py` | **Root schema**. One `Settings` class composing every namespace (core, logging, …); holds cross-field rules (`debug` derived from env). Already exists; refactored to delegate to namespaces. | namespaces, validators | now |
| `bootstrap.py` | **Lifecycle orchestrator**. `build_settings()`: resolve env → load → validate → freeze → audit. The fail-fast entry: any error raises `ConfigurationError` before the app object exists. | environment, settings, secrets, audit | now |
| `constants.py` | **Configuration vocabulary**: the `CCAI_` prefix and sub-prefixes, env var *names*, `.env` file names, sentinels (`CHANGE_ME`), schema version. **Boundary rule:** config/constants.py owns *key/file names*; core/constants.py owns *static default values* (app identity, log rotation limits). No double-sourcing of values. | — (standalone) | now |
| `paths.py` | **Path resolver**. Anchors everything to the backend root via `Path(__file__)` — logs, uploads (Ph3), tmp. Fixes a real Phase 1.3 flaw: `constants.LOG_FILE` is cwd-relative, so running uvicorn from another directory silently writes logs elsewhere. | — | now |
| `validators.py` | **Shared field validators** used by every namespace: URL, port range 1–65535, CSV lists, non-empty, `SecretStr` presence. One implementation; namespaces declare, never reimplement. | core/exceptions | now |
| `features.py` | **Feature flags, statically typed** (`enable_realtime_dashboard`, …). Defines the `ConfigProvider` protocol — today backed by settings, tomorrow by a dynamic flags backend. Consumers call the protocol, not the storage. | settings | now (seam) |
| `secrets.py` | **`SecretResolver` protocol** + `EnvSecretResolver` implementation (env var → `SecretStr`). The swap point for Vault/KMS later; also the `redact()` helper used by audit and errors. | validators | now (seam) |
| `audit.py` | **Redacted startup report**: which keys are set, from which precedence layer, `***` for secrets. Logged by bootstrap before serving. | settings, secrets | now |
| `providers.py` | **Provider contract** — the type shape of an AI provider definition: id, kind (openai/anthropic/local/plugin), base_url, model tiers, timeouts, budget caps, retry policy, secret refs. Pure schema, no I/O. | settings, validators | now (schema) |
| `provider_registry.py` | **Catalog**: `{provider_id → definition}` built from `CCAI_LLM_*` / `CCAI_PLUGIN_*_*`; validates uniqueness and known kinds; immutable after boot. Adding a provider = adding a definition, zero consumer edits (open/closed). | providers | now (schema) |
| `provider_factory.py` | **Builder**: given a registry entry, construct the typed provider config object (and in Phase 3, the actual client). Unknown id → `ConfigurationError`. Consumers depend on `providers.py`, never on concrete clients. | providers, provider_registry | now (schema) |
| `namespaces/core.py` | Nested schema for root app settings: identity, environment, debug, docs, api prefix, cors. | validators, core/constants | now |
| `namespaces/logging.py` | Nested schema for logging: level, console/file, rotation (moves the current `settings.py` log fields into an owned module). | validators, paths | now |
| `namespaces/database.py` | **Reserved.** Phase 2 DB URL, pool size, echo. | — | Phase 2 |
| `namespaces/bus.py`, `llm.py`, `governance.py` | **Reserved.** Phase 3 event bus, LLM gateway, governance ceilings. | — | Phase 3 |

### 12.2 Why This Shape (key decisions)

1. **One public surface, private machinery.** Everything a module needs is
   `from app.config import settings`. Internals can be refactored freely — the
   contract is the `__init__` re-exports.
2. **The providers trio is Dependency Inversion.** `providers.py` (contract) ←
   `provider_registry.py` (catalog) ← `provider_factory.py` (construction).
   Future AI providers and the plugin system both plug into the registry without
   touching consumers — the exact open/closed property Task 1 demanded.
3. **`paths.py` fixes a real bug before it bites.** Everything anchors to the
   backend root from `__file__`, killing the cwd-dependence in the current
   `constants.LOG_FILE`. Production containers and local shells get identical
   paths.
4. **`features.py` and `secrets.py` are protocol-first.** The storage today is
   plain env-backed settings; the seam means the dynamic flags backend and
   Vault/KMS arrive as new implementations of an existing protocol, not as
   rewrites.
5. **Namespaces keep ownership local.** Each future module owns its schema file
   and its `CCAI_<MODULE>_` prefix; merge conflicts and cross-module coupling
   stay bounded.

### 12.3 Challenged Choices in the Requested Example

The task listed `settings.py, environment.py, constants.py, paths.py,
features.py, providers.py, provider_registry.py, provider_factory.py,
validators.py`. The design above adopts all of them and makes three deliberate
disagreements:

- **`config.py` is kept** even though the example omits it — the loader is the
  piece that makes the singleton real (`get_settings()` + cache). Deleting it
  would push load logic back into `__init__.py`.
- **`constants.py` in `config/` is scoped to the configuration *vocabulary***,
  not a second copy of app defaults. A flat "put all constants here" reading
  would split the source of truth for values like `APP_VERSION` — the exact
  failure mode Task 1's single-source rule forbids.
- **`bootstrap.py`, `secrets.py`, `audit.py`, `namespaces/` are added.** The
  example lists schema files but no lifecycle, no secret handling, and no
  namespacing; without them the folder would be a pile of schemas with no
  agreed boot path or secret policy.

### 12.4 Implementation Note — Flat Root + Typed Projections (Task 3)

Task 3 implemented settings management as a **flat frozen root**
(`app/config/settings.py`) with **typed namespace projections**
(`app/config/namespaces/core.py`, `namespaces/logging.py`) — NOT nested
`BaseSettings` models. This deliberately revises the namespaces-as-nested-
settings shape in §6/§12 above, based on empirical testing of
pydantic-settings 2.10.1:

| Claim | Nested `BaseSettings` behavior (tested) | Consequence |
|-------|----------------------------------------|-------------|
| Env vars reach namespaces | ✅ each nested model parses `os.environ` with its own prefix | — |
| Env files reach namespaces | ⚠️ only when each nested model declares its own `env_file` | duplication, drift |
| Precedence: env var > file | ❌ **files override real env vars inside nested models** | violates 12-factor — a developer's `.env` would beat a deployed Secret |
| `_env_file=None` isolation | ❌ **does not propagate to nested models** | tests can't opt out of env files; nondeterministic test runs |
| Single env contract | ❌ each namespace needs its own `env_file` + encoding + settings | merge-conflict magnet |

**Chosen design:** the root `Settings` stays flat (`env_prefix="CCAI_"`,
`frozen=True`) and is the *only* model that reads env vars/files. The
namespaces are immutable typed views (`BaseModel`, `frozen=True`) projected
from the flat fields via properties — `settings.core.app_name`,
`settings.logging.level`. Env precedence, `_env_file=None` isolation and the
layered env-file chain therefore work exactly as designed in §2, because
pydantic-settings' proven flat mechanism handles all of it.

**What changed in the folder design:** `namespaces/` still exists, but its
files hold projection models + the documented env contract instead of nested
settings sources. `paths.py` (root-anchored paths — fixes the Phase 1.3
cwd-relative `LOG_FILE` flaw), `validators.py` (shared url/port/csv/level
checks), `constants.py` (config vocabulary; static values stay in
`core/constants.py`), `bootstrap.py` (load → validate → freeze → fail-fast
`ConfigurationError`), `audit.py` (redacted boot report; name-based masking)
were all implemented as designed. The `os.getenv` lint rule and env
templates remain for their own tasks.

### 12.5 Phase Boundary (what is implemented now vs. reserved)

| Concern | Implemented this phase | Reserved / later phase |
|---------|------------------------|------------------------|
| Public surface + loader + bootstrap | `__init__`, `config.py`, `bootstrap.py` | — |
| Environment detection + inheritance | `environment.py` — layered `.env` → `.env.<env>`, no files in production | — |
| Root schema + namespaces | `settings.py` flat frozen root; `core`, `logging` projections | `database`, `bus`, `llm`, `governance` |
| Vocab + paths | `constants.py`, `paths.py` (root-anchored) | uploads/tmp wired to real storage (Ph3) |
| Validation | `validators.py` (url, port, csv, log level) | — |
| Audit | `audit.py` — redacted boot report (name-based masking) | value-pattern masking; Vault/KMS |
| Secrets | — (no secrets exist yet; `SecretStr` classification ready) | `secrets.py` resolver seam |
| Flags | — (deferred) | `features.py` protocol + static flags |
| Providers | — (deferred) | `providers.py` schema + registry + factory |
| Lint rule (ban `os.getenv`) | — (deferred) | ruff/flake8-banned-api rule |
| Env templates | `.env.example` updated (layered inheritance documented) | `.env.development` / `.env.testing` |

---

*Task 2 (folder design) complete. Next tasks in Phase 1.5 (per the plan):
implement the config folder — namespaces, bootstrap, paths, validators,
secrets + redaction, audit report, features/features seam, provider schema,
the lint rule banning raw `os.getenv`, environment templates (`.env.example`
per environment) — with tests.*
