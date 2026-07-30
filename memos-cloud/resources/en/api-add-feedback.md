# addFeedback API

Use `addFeedback` to correct or update memories with natural-language feedback. The caller does not need to locate the exact memory item first.

## Endpoint

```text
POST https://memos.memtensor.cn/api/openmem/v1/add/feedback
```

## Required Parameters

| Parameter | Type | Meaning |
| --- | --- | --- |
| `user_id` | string | Stable end-user identifier. |
| `conversation_id` | string | Conversation that provides context. |
| `feedback_content` | string | Natural-language correction or update. |

## Optional Parameters

| Parameter | Type | Meaning |
| --- | --- | --- |
| `allow_knowledgebase_ids` | array | Knowledge-base IDs that may be updated by the feedback. |

## How It Works

1. MemOS checks whether the feedback is valid for the current context.
2. It identifies whether the feedback is a keyword replacement or semantic update.
3. It writes new memory and updates or overrides conflicting old memory.

## Usage

### Semantic Correction

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.add_feedback(
    user_id="user_001",
    conversation_id="feedback_conv",
    feedback_content="The software purchase budget is 600, not 800.",
    allow_knowledgebase_ids=["kb_xxx"]
)
print(res)
```

### Keyword Replacement

```python
res = client.add_feedback(
    user_id="user_001",
    conversation_id="feedback_conv",
    feedback_content="Replace all occurrences of old product name A with new product name B."
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
    "conversation_id": "feedback_conv",
    "feedback_content": "The software purchase budget is 600, not 800.",
    "allow_knowledgebase_ids": ["kb_xxx"]
}

res = requests.post(
    f"{BASE_URL}/add/feedback",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
print(res.json())
```

## Use Cases

| Scenario | Example feedback |
| --- | --- |
| Correct wrong fact | "My birthday is March 15, not March 5." |
| Update stale information | "I moved from Shanghai to Beijing." |
| Correct knowledge-base content | "The reimbursement policy has been updated." |
| Global keyword replacement | "Replace A with B everywhere." |

## Verification After Feedback

1. Call `addFeedback` and wait for processing if the route is async.
2. Run `searchMemory` with a query that should retrieve the corrected fact.
3. Check that the new fact appears and the old fact is downgraded, replaced, or no longer returned.
4. For knowledge-base updates, pass the correct `allow_knowledgebase_ids` and verify with a knowledge-base-specific query.

## When Not To Use addFeedback

| Scenario | Prefer |
| --- | --- |
| The user wants to remove one concrete memory | Use `deleteMemory` with `memory_ids`. |
| You need to import large historical content | Use `addMessage` in batches. |
| The correction is only temporary for the current turn | Handle it in the current prompt instead of writing long-term feedback. |
| The content is sensitive or regulated | Confirm consent, retention, and deletion policy first. |
