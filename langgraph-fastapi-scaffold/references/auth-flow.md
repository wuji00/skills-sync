# Auth Flow

## Authentication Architecture

```
┌──────────┐     ┌────────────────┐     ┌──────────────────┐
│ Browser  │────▶│ AuthMiddleware │────▶│ Route Handler    │
│ (cookies)│     │ (fail-closed)  │     │ (request.user)   │
└──────────┘     └───────┬────────┘     └──────────────────┘
                         │
                  ┌──────┴──────┐
                  │ JWT decode  │
                  │ (PyJWT)     │
                  └──────┬──────┘
                         │
                  ┌──────┴──────┐
                  │ User lookup │
                  │ (SQLite/DB) │
                  └─────────────┘
```

## Token Flow

### Login

1. `POST /api/v1/auth/login` with email + password
2. `LocalAuthProvider.authenticate()` verifies bcrypt hash
3. `encode_token(user_id, token_version)` creates JWT:
   ```json
   {"sub": "uuid", "ver": 1, "exp": 86400, "iat": 1234567890}
   ```
4. Response sets cookies:
   - `access_token` (HttpOnly, Secure in prod, SameSite=Lax)
   - `csrf_token` (readable by JS, for CSRF header)

### Request Authentication

1. `AuthMiddleware` runs on every request
2. Checks if path is in public allowlist → pass through
3. Reads `access_token` cookie
4. `decode_token()` verifies signature + expiry
5. Looks up user by `sub` claim
6. Verifies `token_version` matches (password change → all tokens invalidated)
7. Attaches `request.state.user` for downstream use

### Password Change

1. Update password hash + increment `token_version`
2. All existing tokens for that user become invalid (version mismatch)

### Logout

1. `POST /api/v1/auth/logout`
2. Clears `access_token` and `csrf_token` cookies
3. Client redirected to `/login`

## First-Boot Setup

1. Gateway starts, checks if any admin user exists
2. If no admin: logs `"Visit /setup to complete admin account creation"`
3. `POST /api/v1/auth/setup` creates the first admin user
4. Only works when zero admin users exist
5. Returns 409 if admin already exists

## Auth-Disabled Mode

Set `DEER_FLOW_AUTH_DISABLED=1` (or equivalent env var) for development.

- `AuthMiddleware` stamps a synthetic "dev" user on all requests
- No login/setup required
- All requests are authenticated as admin
- **Never use in production**

## Public Paths

```python
PUBLIC_PATH_PREFIXES = [
    "/health",
    "/api/v1/auth/login",
    "/api/v1/auth/setup",
    "/api/v1/auth/me",        # Returns null when not authenticated
    "/docs",
    "/redoc",
    "/openapi.json",
]
```

## CSRF Protection

Double-submit cookie pattern:

1. Login response sets `csrf_token` cookie (not HttpOnly — JS reads it)
2. Frontend reads cookie on mutating requests
3. Sets `X-CSRF-Token` header to cookie value
4. `CSRFMiddleware` compares header to cookie:
   - GET/HEAD/OPTIONS/TRACE: skip
   - POST/PUT/DELETE/PATCH: require match, return 403 on mismatch

Frontend helper (`fetcher.ts`):
```ts
// Auto-injects X-CSRF-Token on state-changing methods
const res = await fetch("/api/threads", { method: "POST", body: ... });
```

## Authorization

Resource-action permission model:

```python
@require_permission("threads", "read", owner_check=True)
async def get_thread(thread_id: str, request: Request): ...
```

- `resource`: entity type (threads, runs)
- `action`: read, write, delete
- `owner_check`: verify `thread_meta.user_id == request.user.id`
- Returns 403 if check fails
