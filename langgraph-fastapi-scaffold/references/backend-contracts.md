# Backend API Contracts

## Base URL

All API endpoints are under the gateway base URL (default `http://localhost:8001`).

## Authentication

Most endpoints require a valid JWT stored in an HttpOnly `access_token` cookie.
Public endpoints (no auth required):
- `GET /health`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/setup` (only when no admin exists)
- `GET /api/v1/auth/me` (returns null when not authenticated)

## Common Patterns

### Error Responses

```json
{
  "detail": "Human-readable error message"
}
```

HTTP status codes: 400 (bad request), 401 (unauthenticated), 403 (forbidden),
404 (not found), 409 (conflict), 422 (validation), 500 (internal), 503 (service unavailable).

### Cursor Pagination

Used for messages and events. Parameters:
- `limit` (default 100, max 200 for messages, 2000 for events)
- `before_seq` (integer, exclusive upper bound)
- `after_seq` (integer, exclusive lower bound)

Response: `{"data": [...], "has_more": true}`

### CSRF Protection

State-changing methods (POST/PUT/DELETE/PATCH) require `X-CSRF-Token` header.
Value is read from `csrf_token` cookie (set at login). Gateway compares header
to cookie — must match. Non-mutating methods (GET/HEAD/OPTIONS) are exempt.

## Endpoints

### Health

```
GET /health
→ 200 {"status": "healthy", "service": "langgraph-fastapi-gateway"}
```

### Auth

```
POST /api/v1/auth/setup
  Body: {"email": "admin@example.com", "password": "secure-password"}
  → 201 {"id": "uuid", "email": "admin@example.com", "system_role": "admin"}
  Errors: 409 (admin already exists), 422 (validation)

POST /api/v1/auth/login
  Body: {"email": "admin@example.com", "password": "secure-password"}
  → 200 {"id": "uuid", "email": "admin@example.com"}
  Sets: access_token (HttpOnly), csrf_token cookies
  Errors: 401 (bad credentials)

POST /api/v1/auth/logout
  → 204
  Clears: access_token, csrf_token cookies

GET /api/v1/auth/me
  → 200 {"id": "uuid", "email": "admin@example.com", "system_role": "admin"}
  → 200 null (when not authenticated)
```

### Threads

```
POST /api/threads
  Body: {"metadata": {}, "if_exists": "raise"}
  → 201 {"thread_id": "uuid", "created_at": "iso8601", "metadata": {}}

GET /api/threads
  Query: ?limit=20&offset=0
  → 200 [{"thread_id": "...", "created_at": "...", "metadata": {}}]

GET /api/threads/{thread_id}
  → 200 {"thread_id": "...", "created_at": "...", "metadata": {}}

GET /api/threads/{thread_id}/state
  → 200 {"values": {...}, "next": [...], "config": {...}}

DELETE /api/threads/{thread_id}
  → 204
```

### Runs & Streaming

```
POST /api/threads/{thread_id}/runs/stream
  Body: {
    "assistant_id": "chat_agent",
    "input": {"messages": [{"role": "user", "content": "Hello"}]},
    "stream_mode": ["messages", "values"],
    "config": {"configurable": {"thread_id": "..."}},
    "multitask_strategy": "reject"
  }
  → 200 text/event-stream (SSE)
  Headers: Content-Location: /api/threads/{thread_id}/runs/{run_id}

POST /api/threads/{thread_id}/runs/wait
  Body: same as stream without stream_mode
  → 200 {"run_id": "...", "status": "success", "values": {...}}

GET /api/threads/{thread_id}/runs/{run_id}/join
  → 200 text/event-stream (reconnect to existing SSE stream)

POST /api/threads/{thread_id}/runs/{run_id}/cancel
  → 204

GET /api/threads/{thread_id}/runs
  → 200 [{"run_id": "...", "status": "...", "created_at": "..."}]

GET /api/threads/{thread_id}/runs/{run_id}/messages
  → 200 {"data": [...], "has_more": false}
```

## SSE Event Format

```
event: metadata
data: {"run_id": "uuid"}

event: values
data: {"messages": [...], ...}

event: messages
data: [{"type": "ai", "content": "...", ...}]

event: end
data: {"status": "success"}
```

## Data Models

### ThreadState

The LangGraph state stored in the checkpointer. Default shape:

```python
class ThreadState(TypedDict):
    messages: list  # LangChain messages
    # Extend with your own fields:
    # title: str
    # metadata: dict
```

### RunRecord

```python
class RunRecord:
    run_id: str
    thread_id: str
    assistant_id: str
    status: RunStatus  # pending|running|success|error|timeout|interrupted
    created_at: str    # ISO 8601
    updated_at: str
    task: asyncio.Task | None
    abort_event: asyncio.Event | None
```
