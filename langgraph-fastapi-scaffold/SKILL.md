---
name: langgraph-fastapi-scaffold
description: >-
  Use when bootstrapping a new AI agent backend or web app with LangGraph and
  FastAPI. Use when the user wants to create a LangGraph agent service, build
  an AI chat app, scaffold a FastAPI gateway for LangGraph, set up a Next.js
  frontend that streams from a LangGraph backend, or start a project with
  hot-reloadable Pydantic config and LangGraph checkpoint persistence.
  Do NOT use for extending existing projects, adding tools to an existing agent,
  or deer-flow-specific operations.
---

# LangGraph + FastAPI Scaffold

## Overview

Full-stack scaffold for building AI agent applications with LangGraph, FastAPI,
and Next.js. Extracted from [bytedance/deer-flow](https://github.com/bytedance/deer-flow)'s
battle-tested architecture and stripped down to reusable, generic patterns.

**Core principle:** Every LangGraph + FastAPI project needs the same
infrastructure shell — config hot-reload, async persistence, SSE streaming,
JWT auth, and a streaming chat UI. This scaffold provides that shell so you
start with the agent logic, not the plumbing.

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Agent framework | LangGraph + LangChain | ≥1.1.9 / ≥1.2.15 |
| Backend web | FastAPI + Uvicorn | ≥0.115.0 / ≥0.34.0 |
| Persistence | SQLAlchemy async + Alembic | ≥2.0 / ≥1.13 |
| Config | Pydantic v2 + YAML | ≥2.12.5 / ≥6.0 |
| Auth | PyJWT + bcrypt | ≥2.13.0 / ≥4.0.0 |
| Package mgmt | uv (workspace) | latest |
| Frontend | Next.js + React 19 | ≥16.2 / ≥19.0 |
| Styling | Tailwind CSS 4 + shadcn/ui | ≥4.0 / new-york |
| State | @tanstack/react-query | ≥5.90 |
| Streaming | @langchain/langgraph-sdk | ≥1.5.3 |
| Package mgmt | pnpm | ≥10 |

## When to Use

```
New project with LangGraph + FastAPI?
├─ Yes → Does it need a web UI?
│   ├─ Yes → Full-stack scaffold (backend + frontend)
│   └─ No  → Backend-only scaffold
└─ No  → Not this skill; use langchain-dev-guide for existing projects
```

**Triggers:**
- "Create a new LangGraph agent backend"
- "Bootstrap a FastAPI + LangGraph project"
- "Set up a chat app with LangGraph streaming"
- "Scaffold an AI agent with hot-reload config and SQL persistence"
- "Build a Next.js frontend that streams from LangGraph"

**Do NOT trigger for:**
- Adding features to existing projects → langchain-dev-guide
- DeerFlow-specific deployment/config → read the deer-flow docs directly
- Generic Python scaffolding (no LangGraph)

## Bootstrap Workflow

### 1. Gather requirements

Ask the user (use defaults if they don't specify):

| Question | Options | Default |
|----------|---------|---------|
| Project name | any valid Python package name | `my-agent` |
| Database backend | `sqlite` / `postgres` | `sqlite` |
| Auth | `enabled` / `disabled` | `disabled` (dev mode) |
| Model provider | `openai` / `anthropic` / `deepseek` / custom | `openai` |
| Docker | yes / no | no |

### 2. Clone the scaffold

```bash
# If scaffold repo is available:
git clone https://github.com/your-org/langgraph-fastapi-scaffold.git <project-name>
cd <project-name>

# Or generate from embedded templates (see templates/ directory)
```

### 3. Configure

```bash
# Backend config
cp config.example.yaml config.yaml
# Edit config.yaml: set models, database backend, auth

# Environment
cp .env.example .env
# Edit .env: set API keys, secrets
```

### 4. Install dependencies

```bash
# Backend
cd backend
uv sync

# Frontend
cd ../frontend
pnpm install
```

### 5. Initialize database

```bash
cd backend
uv run alembic upgrade head
```

### 6. Verify

```bash
# Terminal 1: Start backend
cd backend && uv run uvicorn app.gateway.app:app --reload --port 8001

# Terminal 2: Start frontend
cd frontend && pnpm dev --port 3000

# Smoke test
curl http://localhost:8001/health
# → {"status": "healthy", "service": "langgraph-fastapi-gateway"}
```

### 7. Open and test

Visit `http://localhost:3000`, create a chat, send a message. The example
`chat_agent.py` echoes back with the model you configured.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Next.js Frontend (port 3000)                            │
│  ┌─────────┐  ┌──────────┐  ┌──────────────────┐       │
│  │ chat UI │  │ TanStack  │  │ LangGraph SDK    │       │
│  │ (RSC)   │  │ Query     │  │ (SSE streaming)  │       │
│  └─────────┘  └──────────┘  └────────┬─────────┘       │
└──────────────────────────────────────┼──────────────────┘
                                       │ HTTP/SSE
┌──────────────────────────────────────┼──────────────────┐
│  FastAPI Gateway (port 8001)         │                  │
│  ┌──────────┐  ┌──────────┐  ┌──────┴────────┐        │
│  │ Auth     │  │ CSRF     │  │ Thread/Run    │        │
│  │ MW       │  │ MW       │  │ Routers       │        │
│  └──────────┘  └──────────┘  └──────┬────────┘        │
│  ┌──────────────────────────────────┴────────────────┐  │
│  │  deps.py: AsyncExitStack singletons               │  │
│  │  StreamBridge │ Checkpointer │ Store │ RunManager │  │
│  └──────────────────────────────────┬────────────────┘  │
│  ┌──────────────────────────────────┴────────────────┐  │
│  │  LangGraph Agent (chat_agent.py)                   │  │
│  │  StateGraph → chat_node → compiled graph           │  │
│  └──────────────────────────────────┬────────────────┘  │
└─────────────────────────────────────┼───────────────────┘
                                      │
┌─────────────────────────────────────┼───────────────────┐
│  Persistence                        │                   │
│  SQLite (dev) / PostgreSQL (prod)   │                   │
│  LangGraph Checkpointer + Store     │                   │
└─────────────────────────────────────────────────────────┘
```

**Key architectural decisions (inherited from deer-flow):**

1. **AppConfig hot-reload**: `config.yaml` edits take effect on next request
   without restart. Startup-only fields (database, checkpointer) are documented
   in `reload_boundary.py`.
2. **AsyncExitStack lifespan**: All runtime singletons created/shutdown in one
   `AsyncExitStack` in `deps.py`, stored on `app.state`.
3. **StreamBridge**: Decouples agent worker (graph execution) from SSE endpoint
   (HTTP response). Default: in-memory `asyncio.Queue`.
4. **Abstract stores**: `RunStore`, `RunEventStore`, `ThreadMetaStore` each have
   memory (dev/test) and SQL (prod) implementations.
5. **Double-submit cookie CSRF**: Gateway sets `csrf_token` cookie at login;
   frontend echoes it as `X-CSRF-Token` header on mutating requests.

## Key Files (in the scaffold project)

### Backend

| File | Purpose |
|------|---------|
| `backend/app/gateway/app.py` | FastAPI app factory + lifespan |
| `backend/app/gateway/deps.py` | Runtime singleton bootstrap + DI getters |
| `backend/app/config/app_config.py` | Hot-reload Pydantic config |
| `backend/app/agents/chat_agent.py` | Example agent graph (replace this!) |
| `backend/app/runtime/runs/manager.py` | In-flight run registry |
| `backend/app/runtime/stream_bridge/` | SSE producer/consumer decoupling |
| `backend/app/persistence/engine.py` | Async SQLAlchemy engine factory |
| `backend/app/gateway/routers/thread_runs.py` | Run lifecycle: create/stream/cancel |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/src/core/api/api-client.ts` | LangGraph SDK client wrapper |
| `frontend/src/core/api/fetcher.ts` | fetch + CSRF + 401 redirect |
| `frontend/src/core/threads/hooks.ts` | useThreadStream, optimistic UI |
| `frontend/src/components/ai-elements/prompt-input.tsx` | Chat composer |
| `frontend/src/components/ai-elements/conversation.tsx` | Scroll-to-bottom chat shell |

## How to Extend

### Replace the example agent

Edit `backend/app/agents/chat_agent.py`:
```python
from langgraph.graph import StateGraph, MessagesState, START
from langchain_openai import ChatOpenAI

def build_graph():
    model = ChatOpenAI(model="gpt-4o")
    def chat_node(state: MessagesState):
        return {"messages": [model.invoke(state["messages"])]}
    return StateGraph(MessagesState) \
        .add_node("chat", chat_node) \
        .add_edge(START, "chat") \
        .compile()
```

Then update `langgraph.json` to point at your new factory function.

### Add a tool

```python
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """Search the web."""
    return f"Results for: {query}"

# Bind to model
model = ChatOpenAI(model="gpt-4o").bind_tools([search])
```

### Add a router

1. Create `backend/app/gateway/routers/my_feature.py`
2. Add `app.include_router(my_feature.router)` in `app.py`

### Add a frontend page

1. Create `frontend/src/app/my-page/page.tsx`
2. Use the shared `getAPIClient()` and `useThreadStream` hooks

## Embedded Templates

Key templates are in `templates/` for offline reference. The canonical
source is the scaffold repository (see `assets/scaffold-repo-link.md`).

| Template | What it shows |
|----------|--------------|
| `templates/backend/app.gateway.app.py` | FastAPI factory + lifespan pattern |
| `templates/backend/app.gateway.deps.py` | DI singleton bootstrap + getters |
| `templates/backend/app.agents.chat_agent.py` | Minimal StateGraph example |
| `templates/frontend/core.api.api-client.ts` | LangGraphClient wrapper |
| `templates/frontend/core.threads.hooks.ts` | useThreadStream + optimistic UI |

## Reference Docs

- `references/architecture.md` — full architecture deep-dive
- `references/backend-contracts.md` — API endpoints, request/response schemas
- `references/frontend-contracts.md` — TS types, hooks, component contracts
- `references/auth-flow.md` — JWT cookie flow, CSRF, setup endpoint
- `references/config-hot-reload.md` — how hot reload works, which fields need restart
- `references/deployment.md` — Docker Compose, Postgres, multi-worker

## What This Scaffold Does NOT Include

These deer-flow features are intentionally omitted as domain-specific:

- Skills system (catalog, installer, slash commands)
- Subagent orchestration
- IM Channel integrations (Slack, Feishu, Telegram, etc.)
- MCP server management
- Sandbox execution
- Scheduled tasks / cron
- Memory injection / RAG
- GitHub webhooks
- TUI
- Guardrails

For projects that need these, study the original [deer-flow](https://github.com/bytedance/deer-flow) source or use its agent harness directly.
