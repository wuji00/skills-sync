# Architecture Deep-Dive

## Layered Architecture

The scaffold follows a three-layer architecture inherited from deer-flow:

```
┌─────────────────────────────────────────┐
│  Presentation Layer (Next.js)           │
│  - React Server Components for layout   │
│  - Client components for interactivity  │
│  - TanStack Query for server state      │
│  - LangGraph SDK for SSE streaming      │
└──────────────┬──────────────────────────┘
               │ HTTP (REST + SSE)
┌──────────────┴──────────────────────────┐
│  Gateway Layer (FastAPI)                │
│  - Middleware: Auth, CSRF, CORS, Trace  │
│  - Routers: auth, threads, runs         │
│  - DI: deps.py getters + lifespan       │
│  - Services: start_run, sse_consumer    │
└──────────────┬──────────────────────────┘
               │ Python calls
┌──────────────┴──────────────────────────┐
│  Runtime Layer (LangGraph)              │
│  - StreamBridge: SSE pub/sub            │
│  - Checkpointer: state persistence      │
│  - Store: long-term memory              │
│  - RunManager: in-flight run registry   │
│  - Agent graph: compiled StateGraph     │
└──────────────┬──────────────────────────┘
               │ SQLAlchemy async
┌──────────────┴──────────────────────────┐
│  Persistence Layer                      │
│  - SQLite (WAL mode, dev default)       │
│  - PostgreSQL (production)              │
│  - Abstract store pattern (memory/SQL)  │
│  - Alembic migrations                   │
└─────────────────────────────────────────┘
```

## Startup Sequence

1. `uvicorn` loads `app.gateway.app:app`
2. `create_app()` builds FastAPI with middleware stack
3. `lifespan()` enters `AsyncExitStack` context:
   a. `get_app_config()` loads `config.yaml`
   b. `configure_logging(startup_config)`
   c. `langgraph_runtime(app, startup_config)`:
      - `make_stream_bridge(config)` → memory bridge (or Redis)
      - `init_engine_from_config(config.database)` → SQLAlchemy engine
      - `make_checkpointer(config)` → LangGraph checkpointer
      - `make_store(config)` → LangGraph store
      - Initialize repositories (Run, ThreadMeta, User)
      - `make_run_event_store(config)` → event persistence
      - `RunManager(store=...)` → in-flight registry
   d. `_ensure_admin_user(app)` — first-boot setup check
4. Gateway ready → serve requests

## Request Flow (Chat Message)

1. Frontend: user types message, hits submit
2. `useThreadStream` calls `client.runs.stream(threadId, assistantId, payload)`
3. FastAPI `POST /api/threads/{thread_id}/runs/stream`:
   a. Auth middleware validates JWT cookie
   b. Router creates run record via `RunManager`
   c. `start_run()` spawns background `asyncio.Task`:
      - Build `RunContext` (checkpointer, store, config, event_store)
      - Compile agent graph from `langgraph.json`
      - `graph.astream()` with config, stream_mode
      - Publish events to `StreamBridge`
   d. `sse_consumer()` reads from bridge, formats SSE
   e. Response is `StreamingResponse` with `text/event-stream`
4. Frontend: `useStream` processes SSE events, updates UI
5. When graph completes, `RunManager` marks run as terminal
6. Next page load: `useThreadHistory` fetches from `GET .../messages`

## Config Hot-Reload

**How it works:**
- `get_app_config()` caches `AppConfig` in a module-level singleton
- On each call, checks `config.yaml` mtime
- If changed, re-parses YAML, validates with Pydantic, replaces cache
- ContextVar override for tests (`push_current_app_config`)

**What hot-reloads (no restart):**
- Model configurations (provider, model name, max_tokens)
- Auth settings (token expiry, public paths — via middleware re-read)
- Feature flags

**What requires restart:**
- `database.*` (connection pool, engine)
- `checkpointer.*` (persistence backend)
- `stream_bridge.*` (Redis vs memory)
- `sandbox.*` (provider)
- `log_level` (logging handler)

The authoritative list is in `reload_boundary.py`.

## Run Lifecycle

```
create → pending → running → success/error/timeout/interrupted
                       ↓
                    cancel()
```

- `pending`: record created, worker not yet started
- `running`: background task executing graph
- `success`: graph completed normally
- `error`: exception during graph execution
- `timeout`: execution exceeded max duration
- `interrupted`: user cancelled via `POST .../cancel`

**Multitask strategies** (when a new run is created while one is running):
- `reject`: return 409 (default)
- `interrupt`: cancel existing, start new
- `rollback`: cancel existing, fork from last checkpoint, start new on fork
