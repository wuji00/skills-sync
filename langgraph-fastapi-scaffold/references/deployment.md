# Deployment

## Local Development

### Prerequisites
- Python 3.12+
- uv (package manager)
- Node.js 20+
- pnpm 10+

### Quick Start
```bash
# Clone
git clone <scaffold-repo> my-agent && cd my-agent

# Configure
cp config.example.yaml config.yaml
cp .env.example .env
# Edit config.yaml + .env with your settings

# Backend
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.gateway.app:app --reload --port 8001

# Frontend (new terminal)
cd frontend
pnpm install
pnpm dev --port 3000
```

## Docker

### docker-compose.yml

```yaml
services:
  backend:
    build: ./backend
    ports: ["8001:8001"]
    volumes:
      - ./config.yaml:/app/config.yaml:ro
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/deerflow.db
      - JWT_SECRET=${JWT_SECRET}

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_BACKEND_BASE_URL=http://backend:8001
    depends_on: [backend]
```

### Start
```bash
docker-compose up -d
```

## PostgreSQL Setup

1. Update `config.yaml`:
```yaml
database:
  backend: postgres
  postgres:
    url: postgresql+asyncpg://user:pass@localhost:5432/myagent
```

2. Install extras:
```bash
cd backend && uv sync --extra postgres
```

3. Create database (auto on first boot) or manually:
```bash
uv run alembic upgrade head
```

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `OPENAI_API_KEY` | OpenAI model access | For OpenAI models |
| `ANTHROPIC_API_KEY` | Anthropic model access | For Claude models |
| `JWT_SECRET` | JWT signing key | Yes (with auth) |
| `GATEWAY_HOST` | Bind address | No (default: 0.0.0.0) |
| `GATEWAY_PORT` | Bind port | No (default: 8001) |
| `GATEWAY_ENABLE_DOCS` | Swagger/ReDoc | No (default: true) |
| `GATEWAY_WORKERS` | Uvicorn workers | No (default: 1) |
| `DEER_FLOW_HOME` | Data directory | No (default: .deer-flow) |
| `DEER_FLOW_AUTH_DISABLED` | Skip auth (dev only) | No (default: unset) |

## Multi-Worker

When `GATEWAY_WORKERS > 1`:
- SQLite is **not supported** — the gateway refuses to start
- Must use PostgreSQL (`database.backend: postgres`)
- Stream bridge should use Redis for cross-process SSE (`stream_bridge.backend: redis`)

## Data Directory

Default: `.deer-flow/` under project root. Override with `DEER_FLOW_HOME`.

Contents:
```
.deer-flow/
├── deerflow.db         # SQLite database
├── uploads/            # Staging area for file uploads
└── sandbox/            # Sandbox workspaces (if used)
```

## Health Check

```bash
curl http://localhost:8001/health
# → {"status": "healthy", "service": "langgraph-fastapi-gateway"}
```

## Production Checklist

- [ ] Set `JWT_SECRET` to a strong random value
- [ ] Set `auth.token_expiry_hours` appropriately
- [ ] Use PostgreSQL, not SQLite
- [ ] Set `GATEWAY_WORKERS` based on CPU cores
- [ ] Use Redis stream bridge for multi-worker
- [ ] Enable HTTPS with a reverse proxy (nginx, Caddy)
- [ ] Set secure cookie flags (Secure, SameSite=Strict)
- [ ] Disable `GATEWAY_ENABLE_DOCS` if exposing publicly
- [ ] Configure CORS origins explicitly
- [ ] Set up log aggregation
