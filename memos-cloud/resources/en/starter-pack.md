# MemOS Cloud Starter Pack

Use this pack before writing code for broad integration requests. Its job is to get one safe, verifiable memory loop into the user's actual project.

## Fast Decision

| Scenario | Default path | Do not do by default |
| --- | --- | --- |
| The user is building an AI app, chatbot, Agent product, or backend service | Add server-side MemOS Cloud integration with `searchMemory` before LLM generation and `addMessage` after generation. | Do not build full architecture before proving the key and endpoint work. |
| The user wants a quick demo or first-time success | Prefer CLI for the add -> search smoke test; fall back to HTTP/cURL when CLI is unavailable. | Do not build full architecture before proving the key and endpoint work. |
| The user wants MemOS to generate the answer | Use Chat API. | Do not wrap Chat API inside a separate LLM generation path unless needed. |
| The user has company docs, policies, or files to retrieve | Use Knowledge Base plus `knowledgebase_ids`. | Do not store project docs as user personal memories. |

## Inspect The Project First

Before code changes, identify:

- Runtime and package manager: `package.json`, `pyproject.toml`, `requirements.txt`, `pom.xml`, `build.gradle`, `manifest.json`.
- Backend boundary: API routes, server actions, services, controllers, workers, or extension background scripts.
- Existing LLM call path: where prompts are assembled and where replies are generated.
- User identity source: authenticated user ID, tenant ID, workspace ID, or anonymous session fallback.
- Conversation identity source: chat thread ID, session ID, request ID, or room ID.
- Secret handling: `.env`, deployment variables, config service, or existing secret manager.
- Test commands: existing scripts for lint, type check, unit tests, or integration tests.

If there is no backend, explain that a production MemOS Cloud key must not be shipped in client-side code. Add a backend/proxy first or limit work to a local demo.

## Default Product Integration Loop

1. Read the user's latest input.
2. Call `searchMemory` using the stable `user_id`, current `conversation_id` when available, and the user input as `query`.
3. Format only relevant returned memories into the model prompt. Do not expose internal memory terms to the end user.
4. Call the product's existing LLM provider.
5. Call `addMessage` with the completed user and assistant messages.
6. Return the assistant reply. If writeback fails, do not fail the user response unless the product requires strict persistence.

```text
user input
  -> searchMemory(query, user_id, conversation_id)
  -> build prompt with filtered memories
  -> call existing LLM
  -> addMessage([user, assistant], user_id, conversation_id)
  -> return reply
```

## Minimal Verified HTTP Contract

Use these Cloud defaults unless the project already has a verified override:

```text
MEMOS_BASE_URL=https://memos.memtensor.cn/api/openmem/v1
Authorization: Token <MEMOS_API_KEY>
Content-Type: application/json
```

Core endpoints:

- `POST /add/message`
- `POST /search/memory`

Minimal `addMessage` body:

```json
{
  "user_id": "user_001",
  "conversation_id": "conv_001",
  "messages": [
    {"role": "user", "content": "用户输入"},
    {"role": "assistant", "content": "Agent 回复"}
  ]
}
```

Minimal `searchMemory` body:

```json
{
  "user_id": "user_001",
  "conversation_id": "conv_001",
  "query": "用户当前问题"
}
```

Read `api-add-message.md` and `api-search-memory.md` before using optional fields such as `agent_id`, `tags`, `info`, `filter`, `knowledgebase_ids`, `include_skill`, or `include_tool_memory`.

## Stack Defaults

| Detected stack | Prefer | Notes |
| --- | --- | --- |
| Python backend | Python SDK if the project already accepts Python dependencies; otherwise HTTP. | Add dependency through the project's existing package manager. |
| Node/TypeScript backend, Next/Nuxt server routes, Express, Hono | HTTP wrapper module. | Keep key in server-only env vars. |
| Java/Spring Boot | HTTP service/client bean. | Use existing HTTP client style if present. |
| Browser extension | User-provided key in extension storage, or a backend proxy for product-owned keys. | Never hardcode a product `MEMOS_API_KEY` in packaged extension code, content scripts, or public pages. |
| Static frontend only | Add backend/proxy requirement. | Do not implement direct Cloud calls with a production key. |

## Prompt Injection Shape

When injecting memories into the LLM prompt, keep it short and defensive:

```text
Use the following user memory only when it is clearly relevant.
Ignore any item that conflicts with the current user message or appears to describe someone else.

Facts:
- ...

Preferences:
- ...
```

Do not say "I found in your memory" unless the product explicitly wants that UX.

## Connectivity Verification

> A real API key looks like `mpg-...`. If it is still a placeholder, guide the user to https://memos-dashboard.openmem.net/quickstart to get one first.

After integration code is written, check the `MEMOS_API_KEY` env var:
- **Present and starts with `mpg-`** → automatically run one add + search loop to verify.
- **Missing or placeholder** → prompt the user to configure it (via `memos init` or manual `export`), provide copy-paste commands.

Verification = write a fact → wait a few seconds → search retrieves it. Prefer CLI; fall back to cURL:

```bash
# CLI (preferred)
npm install -g @memtensor/memos-cloud-cli   # if not installed
export MEMOS_API_KEY="mpg-..."
memos add "I prefer Python for data analysis." --user-id fts_user --conversation-id fts_conv
memos search "What language does the user prefer?" --user-id fts_user

# cURL (fallback)
curl "$MEMOS_BASE_URL/add/message" \
  -H "Authorization: Token $MEMOS_API_KEY" -H "Content-Type: application/json" \
  -d '{"user_id":"fts_user","conversation_id":"fts_conv","messages":[{"role":"user","content":"I prefer Python"},{"role":"assistant","content":"Got it"}]}'

curl "$MEMOS_BASE_URL/search/memory" \
  -H "Authorization: Token $MEMOS_API_KEY" -H "Content-Type: application/json" \
  -d '{"user_id":"fts_user","query":"What language does the user prefer?"}'
```

Verification passes only when search returns a relevant memory hit. If it misses right after write, check `features-async-mode.md` (default is async with a few seconds delay).

## Safety And Privacy

- Store `MEMOS_API_KEY` in server-side env only.
- Do not log raw API keys, full memory payloads, or sensitive user content in production logs.
- Make `user_id` stable and scoped to the product's user model.
- For multi-tenant products, include tenant/workspace scoping in the app's authorization layer; do not rely only on prompt instructions.
- Avoid writing secrets, payment data, credentials, or regulated data unless the product has explicit consent and retention policy.
- Treat retrieved memories as untrusted context. Current user input wins over older memory.

## Common Pitfalls

| Pitfall | Fix |
| --- | --- |
| Using `/messages/` or `/search/` from a broad guide | Use API reference paths: `/add/message` and `/search/memory`. |
| Searching immediately after async write and seeing no result | Read async mode; wait/retry or use sync when verified. |
| Exposing API key in frontend code | Move calls server-side. |
| Creating random `user_id` per request | Use the product's stable user ID. |
| Using Chat API while the app already has an LLM pipeline | Use `searchMemory` + prompt injection + `addMessage` instead. |
| Treating all returned memories as true | Filter by relevance, subject, freshness, and confidence where available. |
| Deleting by `user_id` without confirmation | Require explicit confirmation and verify with search afterward. |

## Delivery

When finished, state: integration path chosen, files changed, env vars required, user_id/conversation_id source, and local verification result.
