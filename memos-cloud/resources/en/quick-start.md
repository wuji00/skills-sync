# Quick Start

If the user wants to integrate MemOS Cloud into an existing project, start from [Starter Pack](starter-pack.md). It includes the copy-paste Agent prompt, project inspection checklist, first-time-success validation, and safety boundaries. This file is only for the minimal Cloud API/SDK path.

## Copy-Paste Prompt

The copy-paste integration prompt is maintained in one place, [starter-pack.md](starter-pack.md) ("Copy-Paste English Prompt For Agents"). It is not duplicated here to avoid drift.

## Environment Setup

1. Register and sign in to [MemOS Cloud](https://memos-dashboard.openmem.net/quickstart).
2. Get an API key from [API Keys](https://memos-dashboard.openmem.net/apikeys).
3. Prepare Python 3.10+ if using the Python SDK, or use direct HTTP from other backends.

## Install SDK

```bash
pip install MemoryOS -U
```

## Authentication

### Python SDK

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")
```

### HTTP

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"
headers = {"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"}
```

### cURL

```bash
export MEMOS_API_KEY="YOUR_API_KEY"
export MEMOS_BASE_URL="https://memos.memtensor.cn/api/openmem/v1"
```

## Core Concepts

| Concept | Meaning |
| --- | --- |
| `user_id` | Stable end-user identifier. Every memory operation is scoped to a user. |
| `conversation_id` | Stable conversation/thread identifier. |
| `agent_id` | Optional Agent identifier used to isolate memories by Agent. |
| `messages` | Ordered message list with roles such as `user`, `assistant`, `system`, or `tool`. |

## First Memory Operation

### Step 1: Add A Turn

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.add_message(
    messages=[
        {"role": "user", "content": "I prefer Python for data analysis."},
        {"role": "assistant", "content": "Got it."}
    ],
    user_id="user_001",
    conversation_id="conv_001"
)
print(res)
```

### Step 2: Search Memory

```python
res = client.search_memory(
    query="Which programming language does the user prefer for data analysis?",
    user_id="user_001",
    conversation_id="conv_001"
)
print(res)
```

MemOS extracts facts and preferences from conversation history and returns relevant memory for later turns.

## Memory Types

| Type | Meaning | Example |
| --- | --- | --- |
| Fact memory | Objective user information | "The user lives in Shanghai." |
| Preference memory | User preferences | "The user prefers concise answers." |
| Skill memory | Reusable task procedure | "How to plan a trip." |
| Tool memory | Tool-use experience | "Use get_weather for weather queries." |
| Knowledge-base memory | Document or policy memory | "Expense policy: software budget is 600." |

## Next Steps

- Read [addMessage API](api-add-message.md) for write parameters.
- Read [searchMemory API](api-search-memory.md) for retrieval parameters.
- Use [Chat API](api-chat.md) only when MemOS should generate the reply.
