# searchMemory API

Use `searchMemory` to retrieve memories relevant to the current user query. It can return fact memories, preference memories, Tool Memory, Skill Memory, and knowledge-base memories.

## Endpoint

```text
POST https://memos.memtensor.cn/api/openmem/v1/search/memory
```

## Required Parameters

| Parameter | Type | Meaning |
| --- | --- | --- |
| `user_id` | string | Stable end-user identifier. |
| `query` | string | Semantic retrieval query. Usually the user's latest message. |

## Basic Usage

### Python SDK

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.search_memory(
    query="What food does the user like?",
    user_id="user_001",
    conversation_id="conv_002"
)
print(res)
```

### HTTP

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"

payload = {
    "query": "What food does the user like?",
    "user_id": "user_001",
    "conversation_id": "conv_002"
}

res = requests.post(
    f"{BASE_URL}/search/memory",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
print(res.json())
```

### cURL

```bash
curl "$MEMOS_BASE_URL/search/memory" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What food does the user like?",
    "user_id": "user_001",
    "conversation_id": "conv_002"
  }'
```

## Response Shape

```json
{
  "code": 0,
  "data": {
    "memory_detail_list": [
      {
        "id": "uuid",
        "memory_key": "food preference",
        "memory_value": "The user likes spicy food.",
        "memory_type": "LongTermMemory",
        "create_time": 1766041646311,
        "conversation_id": "conv_001",
        "status": "activated",
        "confidence": 0.99,
        "tags": ["food", "preference"],
        "relativity": 0.89
      }
    ],
    "preference_detail_list": [
      {
        "preference_type": "explicit_preference",
        "preference": "The user likes spicy food.",
        "conversation_id": "conv_001"
      }
    ],
    "tool_memory_detail_list": [],
    "skill_detail_list": []
  },
  "message": "ok"
}
```

## Optional Parameters

| Parameter | Type | Default | Meaning |
| --- | --- | --- | --- |
| `conversation_id` | string | - | Prefer memories related to the current conversation. |
| `filter` | object | - | Structured filters. See [Memory Filters](features-filters.md). |
| `relativity` | float | 0.45 | Relevance threshold. Higher is stricter. |
| `memory_limit_number` | int | 6 | Max fact memories. |
| `include_preference` | bool | true | Include preference memories. |
| `preference_limit_number` | int | 6 | Max preference memories. |
| `include_skill` | bool | false | Include Skill Memory. |
| `include_tool_memory` | bool | false | Include Tool Memory. |
| `tool_memory_limit_number` | int | 6 | Max Tool Memory items. |
| `knowledgebase_ids` | array | - | Knowledge bases to search. |

## Patterns

### Filter Candidate Scope

```python
payload = {
    "user_id": "user_001",
    "query": "Summarize this year's reading memories.",
    "filter": {
        "and": [
            {"tags": {"contains": "reading"}},
            {"create_time": {"gte": "2025-01-01"}},
            {"create_time": {"lte": "2025-12-31"}}
        ]
    }
}
```

### Control Quality And Count

```python
payload = {
    "user_id": "user_001",
    "query": "Plan a five-day trip to Chengdu.",
    "relativity": 0.8,
    "memory_limit_number": 9
}
```

### Search Skill And Tool Memory

```python
payload = {
    "user_id": "user_001",
    "query": "Plan a Yunnan trip.",
    "include_skill": True,
    "include_tool_memory": True,
    "tool_memory_limit_number": 10
}
```

### Search Knowledge Bases

```python
payload = {
    "user_id": "user_001",
    "query": "What is the company travel reimbursement policy?",
    "knowledgebase_ids": ["kb_xxx"],
    "include_skill": True
}
```

## Inject Memories Into Prompt

```python
memories = result["data"].get("memory_detail_list", [])
preferences = result["data"].get("preference_detail_list", [])

memory_text = "\n".join(f"- {m['memory_value']}" for m in memories)
pref_text = "\n".join(f"- {p['preference']}" for p in preferences)

system_prompt = f"""You are an assistant with long-term memory.

Use the following memory only when it is relevant.
Ignore any item that conflicts with the current user message or appears to describe someone else.

Facts:
{memory_text}

Preferences:
{pref_text}
"""
```

Do not expose internal memory implementation details to end users unless the product UX requires it.

## Limits

- Single request input: up to 40,000 tokens.
- Fact memory output: up to 25 items.
- Preference memory output: up to 25 items.
- Tool Memory output: up to 25 items.
- Skill output: up to 25 items.
