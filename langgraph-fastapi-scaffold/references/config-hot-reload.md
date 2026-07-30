# Config Hot-Reload

## How It Works

The scaffold's configuration system is extracted from deer-flow's Pydantic-based
hot-reload pattern:

```python
# app/config/app_config.py
from pydantic import BaseModel
import yaml, os, hashlib

_app_config: AppConfig | None = None
_config_mtime: float | None = None
_config_hash: str | None = None

def get_app_config() -> AppConfig:
    """Return current AppConfig, reloading from disk if config.yaml changed."""
    global _app_config, _config_mtime, _config_hash
    config_path = _resolve_config_path()

    try:
        mtime = os.path.getmtime(config_path)
    except OSError:
        raise FileNotFoundError(f"Config not found: {config_path}")

    if mtime != _config_mtime:
        with open(config_path) as f:
            raw = f.read()
        new_hash = hashlib.sha256(raw.encode()).hexdigest()
        if new_hash != _config_hash:
            data = _resolve_env_vars(yaml.safe_load(raw))
            _app_config = AppConfig(**data)
            _config_hash = new_hash
        _config_mtime = mtime

    # Check for ContextVar override (tests)
    ctx_override = _current_app_config_ctx.get()
    return ctx_override if ctx_override is not None else _app_config
```

**Key behaviors:**
- Checks `config.yaml` mtime on every call → sub-millisecond when unchanged
- Hashes content to detect rewrites that preserve mtime
- Resolves `$ENV_VAR` placeholders in YAML values
- ContextVar override for test isolation
- Missing file → `FileNotFoundError` (gateway returns 503)

## Config Sections

```yaml
# config.yaml
config_version: 1

log_level: info

models:
  - name: gpt-4o
    model: gpt-4o
    display_name: GPT-4o
    use: langchain_openai:ChatOpenAI
    api_key: $OPENAI_API_KEY

database:
  backend: sqlite                # sqlite | postgres
  sqlite:
    url: sqlite+aiosqlite:///./data/deerflow.db

auth:
  jwt_secret: $JWT_SECRET
  token_expiry_hours: 24
  bcrypt_rounds: 12

checkpointer:
  backend: database              # memory | database (follows database.backend)

stream_bridge:
  backend: memory                # memory | redis
```

## AppConfig Model

```python
class AppConfig(BaseModel):
    config_version: int = 1
    log_level: str = "info"
    models: list[ModelConfig] = []
    database: DatabaseConfig = DatabaseConfig()
    auth: AuthConfig = AuthConfig()
    checkpointer: CheckpointerConfig = CheckpointerConfig()
    stream_bridge: StreamBridgeConfig = StreamBridgeConfig()
```

## Reload Boundary

Some fields require a process restart to change. They're documented in
`reload_boundary.py` and annotated with `"startup-only:"` in their
`Field(description=...)`:

| Field | Reason |
|-------|--------|
| `database.*` | Connection pool, engine |
| `checkpointer.backend` | Persistence backend |
| `stream_bridge.backend` | Redis connection |
| `log_level` | Logging handler |
| `auth.bcrypt_rounds` | Auth provider singleton |

All other fields (models, feature flags, auth expiry) hot-reload automatically.

## Environment Variable Resolution

YAML values starting with `$` are resolved from environment:

```yaml
api_key: $OPENAI_API_KEY        # → os.environ["OPENAI_API_KEY"]
url: $DATABASE_URL              # → os.environ["DATABASE_URL"]
```

Unset variables raise a clear error at startup. Use `$$` to escape a literal `$`.

## Test Overrides

```python
from app.config.app_config import push_current_app_config, pop_current_app_config

# Override for test
test_config = AppConfig(models=[...])
push_current_app_config(test_config)
# ... test code ...
pop_current_app_config()
```

ContextVar-based, thread-safe, no file I/O.
