# Chat API

The Chat API combines memory retrieval, prompt assembly, model generation, and turn writeback in one call.

## Endpoint

```text
POST https://memos.memtensor.cn/api/openmem/v1/chat
```

## Chat API vs Memory Operation APIs

| Dimension | Chat API | `addMessage` + `searchMemory` |
| --- | --- | --- |
| Integration complexity | Lower | Medium |
| Memory orchestration | Automatic | You control write, search, and prompt injection |
| Reply generation | MemOS built-in model | Your existing LLM provider |
| Control | Best for quick PoC or generic chat | Best for complex Agents and product pipelines |

Use Chat API for PoC or when the user wants MemOS to generate the final reply. For existing LLM pipelines, prefer `searchMemory` + prompt injection + `addMessage`.

## Required Parameters

| Parameter | Type | Meaning |
| --- | --- | --- |
| `user_id` | string | Stable end-user identifier. |
| `conversation_id` | string | Stable conversation/thread identifier. |
| `query` | string | Current user message. |

## Basic Usage

### Python SDK

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.chat(
    user_id="user_001",
    conversation_id="conv_002",
    query="Recommend a city I have not visited for the holiday."
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
    "conversation_id": "conv_002",
    "query": "Recommend a city I have not visited for the holiday."
}

res = requests.post(
    f"{BASE_URL}/chat",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
print(res.json())
```

### cURL

```bash
curl "$MEMOS_BASE_URL/chat" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "conversation_id": "conv_002",
    "query": "Recommend a city I have not visited for the holiday."
  }'
```

## Optional Parameters

### Retrieval Controls

| Parameter | Type | Meaning |
| --- | --- | --- |
| `filter` | object | Structured memory filters. |
| `knowledgebase_ids` | array | Knowledge bases to search. |
| `relativity` | float | Relevance threshold. |
| `memory_limit_number` | int | Max fact memories. |

### Generation Controls

| Parameter | Type | Meaning |
| --- | --- | --- |
| `model_name` | string | Chat model, for example `"qwen2.5-72b-instruct"`. |
| `stream` | bool | Stream response. |
| `temperature` | float | Sampling temperature. |
| `top_p` | float | Top-p sampling. |
| `max_tokens` | int | Max generated tokens. |
| `system_prompt` | string | Custom system prompt. |

### Writeback Controls

| Parameter | Type | Meaning |
| --- | --- | --- |
| `add_message_on_answer` | bool | Whether to write the completed turn to memory. Defaults to true. |
| `agent_id` | string | Agent identifier. |
| `app_id` | string | App identifier. |
| `tags` | array | Tags to attach. |
| `info` | object | Business metadata. |

## Patterns

### Knowledge Base + Filter

```python
payload = {
    "user_id": "user_001",
    "conversation_id": "conv_002",
    "query": "Summarize the travel reimbursement policy.",
    "knowledgebase_ids": ["kb_xxx"],
    "filter": {
        "and": [
            {"tags": {"contains": "travel"}},
            {"create_time": {"gte": "2025-01-01"}}
        ]
    },
    "relativity": 0.8,
    "memory_limit_number": 9
}
```

### Model Parameters

```python
payload = {
    "user_id": "user_001",
    "conversation_id": "conv_002",
    "query": "Summarize my travel preferences concisely.",
    "model_name": "qwen2.5-72b-instruct",
    "temperature": 0.7,
    "max_tokens": 1024
}
```

### Reply Without Memory Writeback

```python
payload = {
    "user_id": "user_001",
    "conversation_id": "conv_002",
    "query": "This is a one-off question. Do not remember it.",
    "add_message_on_answer": False
}
```

## Limits

- Input: up to 8,000 tokens.
- Output memory context: up to 25 fact memories and 25 preference memories.
