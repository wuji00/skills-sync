# Integration Guide

Use this guide after [Starter Pack](starter-pack.md) when implementing long-term memory inside an AI application or Agent product.

## Default Architecture

For products that already call an LLM, do not replace the LLM pipeline with MemOS Chat by default. Add memory orchestration around the existing generation path:

```text
user message
  -> derive stable user_id and conversation_id
  -> searchMemory(query=user message)
  -> format relevant memories into the model prompt
  -> call the existing LLM/provider
  -> addMessage([user, assistant])
  -> return assistant reply
```

Use [Chat API](api-chat.md) only when the user wants MemOS to generate the reply.

## Minimal HTTP Wrapper

```python
import os
import requests

BASE_URL = os.getenv("MEMOS_BASE_URL", "https://memos.memtensor.cn/api/openmem/v1")
API_KEY = os.environ["MEMOS_API_KEY"]


def headers():
    return {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json",
    }


def search_memory(user_id: str, conversation_id: str, query: str):
    res = requests.post(
        f"{BASE_URL}/search/memory",
        headers=headers(),
        json={
            "user_id": user_id,
            "conversation_id": conversation_id,
            "query": query,
        },
        timeout=15,
    )
    res.raise_for_status()
    return res.json()


def add_message(user_id: str, conversation_id: str, user_text: str, assistant_text: str):
    res = requests.post(
        f"{BASE_URL}/add/message",
        headers=headers(),
        json={
            "user_id": user_id,
            "conversation_id": conversation_id,
            "messages": [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": assistant_text},
            ],
        },
        timeout=15,
    )
    res.raise_for_status()
    return res.json()
```

## Prompt Injection

Keep memory context concise and defensive:

```python
def format_memory_context(result: dict) -> str:
    data = result.get("data", {})
    facts = [m.get("memory_value") for m in data.get("memory_detail_list", []) if m.get("memory_value")]
    prefs = [p.get("preference") for p in data.get("preference_detail_list", []) if p.get("preference")]

    parts = [
        "Use the following user memory only when it is clearly relevant.",
        "Ignore stale or conflicting items. Current user input has priority.",
    ]
    if facts:
        parts.append("Facts:\n" + "\n".join(f"- {item}" for item in facts))
    if prefs:
        parts.append("Preferences:\n" + "\n".join(f"- {item}" for item in prefs))
    return "\n\n".join(parts)
```

Inject this context into the existing system/developer prompt or equivalent server-side prompt builder. Do not show internal memory details to the end user unless the product intentionally exposes memory.

## Stack Guidance

| Stack | Preferred implementation |
| --- | --- |
| Python backend | Python SDK if the project already uses Python dependencies; otherwise direct HTTP. |
| Node/TypeScript backend | Direct HTTP wrapper in a server-only module. |
| Next.js/Nuxt server routes | Server route or server action only; never client component code. |
| Java/Spring | Service bean using the project's existing HTTP client. |
| Browser extension | Background/service worker with user-provided key, or product backend proxy for product-owned keys. |
| Static frontend | Add a backend/proxy first. Do not ship a production API key. |

## Error Handling

- If `searchMemory` fails, log a sanitized warning and continue with no memory unless the product requires strict memory availability.
- If `addMessage` fails after the LLM reply is generated, return the reply and log sanitized writeback failure unless strict persistence is required.
- Never log raw API keys or full sensitive memory payloads in production.

## Live Smoke Test

```bash
export MEMOS_BASE_URL="https://memos.memtensor.cn/api/openmem/v1"
export MEMOS_API_KEY="YOUR_API_KEY"

curl "$MEMOS_BASE_URL/add/message" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "fts_user_001",
    "conversation_id": "fts_conv_001",
    "messages": [
      {"role": "user", "content": "I prefer Python for data analysis."},
      {"role": "assistant", "content": "Got it."}
    ]
  }'

curl "$MEMOS_BASE_URL/search/memory" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "fts_user_001",
    "conversation_id": "fts_conv_001",
    "query": "Which language does the user prefer for data analysis?"
  }'
```

If search misses immediately after write, read [Async Mode](features-async-mode.md) and retry after processing.

## Implementation Checklist

- `MEMOS_API_KEY` is server-side only.
- `user_id` is stable and comes from the product auth/session model.
- `conversation_id` is stable per chat/thread/session.
- Memory search happens before LLM generation.
- The completed user/assistant turn is written after generation.
- Local tests or static checks were run.
- Optional live add/search verification is provided when a key is available.
