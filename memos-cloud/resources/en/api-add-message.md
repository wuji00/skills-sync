# addMessage API

Use `addMessage` to write raw conversation turns or user information to MemOS. MemOS extracts facts, preferences, Tool Memory, and Skill Memory from the submitted content.

## Endpoint

```text
POST https://memos.memtensor.cn/api/openmem/v1/add/message
```

## Required Parameters

| Parameter | Type | Meaning |
| --- | --- | --- |
| `user_id` | string | Stable end-user identifier. |
| `conversation_id` | string | Stable conversation/thread identifier. |
| `messages` | array | Ordered messages. Each message should include `role` and content data. |

## Basic Usage

### Python SDK

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.add_message(
    messages=[
        {"role": "user", "content": "I like spicy food."},
        {"role": "assistant", "content": "Got it."}
    ],
    user_id="user_001",
    conversation_id="conv_001"
)
print(res)
```

### HTTP

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"

payload = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "messages": [
        {"role": "user", "content": "I like spicy food."},
        {"role": "assistant", "content": "Got it."}
    ]
}

res = requests.post(
    f"{BASE_URL}/add/message",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
print(res.json())
```

### cURL

```bash
curl "$MEMOS_BASE_URL/add/message" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "messages": [
      {"role": "user", "content": "I like spicy food."},
      {"role": "assistant", "content": "Got it."}
    ]
  }'
```

## Optional Parameters

| Parameter | Type | Meaning |
| --- | --- | --- |
| `chat_time` | string | Actual time for a message, for example `"2025-09-12 08:00:00"`. |
| `agent_id` | string | Agent identifier for isolating memories by Agent. |
| `app_id` | string | App identifier. |
| `tags` | array | Custom tags used later in retrieval filters. |
| `info` | object | Business metadata such as `scene`, `biz_id`, `business_type`, or `custom_status`. |
| `async_mode` | bool | Write-processing mode. Defaults to true. See [Async Mode](features-async-mode.md). |
| `source` | string | Source identifier. |
| `allow_public` | bool | Allow memory to be publicly retrievable. Defaults to false. |
| `allow_knowledgebase_ids` | array | Knowledge base IDs allowed for writeback. |

## Patterns

### Import Historical Conversation With Timestamps

```python
payload = {
    "user_id": "user_001",
    "conversation_id": "conv_history",
    "messages": [
        {"role": "user", "content": "I like spicy food.", "chat_time": "2025-09-12 08:00:00"},
        {"role": "assistant", "content": "Got it.", "chat_time": "2025-09-12 08:01:00"}
    ]
}
```

### Isolate By Agent

```python
payload = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "agent_id": "health_assistant",
    "messages": [
        {"role": "user", "content": "I ran 5 km today and my knee feels sore."},
        {"role": "assistant", "content": "Consider lowering tomorrow's training intensity."}
    ]
}
```

### Add Tags And Metadata

```python
payload = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "tags": ["fitness", "training"],
    "info": {"scene": "fitness", "business_type": "health"},
    "messages": [
        {"role": "user", "content": "I ran 5 km today."},
        {"role": "assistant", "content": "Logged."}
    ]
}
```

## Multimodal And Tool Messages

- For images and files, read [Multimodal](features-multimodal.md).
- For `tool_calls` and `tool` role messages, read [Tool Memory](features-tool-memory.md).

## Write Timing

| Strategy | Use when |
| --- | --- |
| One-time import | Migrating existing conversation history. |
| Real-time write | Writing every completed turn. |
| Batch by turns | Reducing write frequency for high-volume conversations. |

## Limits

- Single request input: up to 40,000 tokens.
- Total tokens per minute: up to 400,000.
- Suggested QPS: 50 or lower.
