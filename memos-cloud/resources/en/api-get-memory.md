# getMemory API

Fetch a user's existing memories by `user_id`, with pagination. Commonly used to inspect a user's full memory set and to **resolve `memory_ids` before deletion** (deletion is high risk, so confirm what you are about to remove).

Difference from `searchMemory`: `searchMemory` semantically recalls memories relevant to a query; `getMemory` **lists/paginates** a user's memories without query semantics.

## Endpoint

```text
POST https://memos.memtensor.cn/api/openmem/v1/get/memory
```

## Required Parameters

| Parameter | Type | Meaning |
| --- | --- | --- |
| `user_id` | string | Stable end-user identifier. |

## Optional Parameters

| Parameter | Type | Default | Meaning |
| --- | --- | --- | --- |
| `page` | int | 1 | Page number (CLI `--page`). |
| `size` | int | 10 | Page size (CLI `--size`). |
| `include_preference` | bool | true | Also return preference memories. |
| `include_tool_memory` | bool | false | Also return Tool Memory. |

## Usage

### Python SDK

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.get_memory(
    user_id="memos_user_123",
    include_preference=True,
    page=1,
    size=10
)
print(res)
```

> SDK signature: `get_memory(user_id, include_preference=True, page=1, size=10, include_tool_memory=False)`

### HTTP

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"

payload = {"user_id": "memos_user_123"}

res = requests.post(
    f"{BASE_URL}/get/memory",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
print(res.json())
```

### cURL

```bash
curl "$MEMOS_BASE_URL/get/memory" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "memos_user_123"}'
```

### CLI (for verification)

```bash
memos get user_123 --format json --detail detail
```

## Response

Returns the user's memory list. The shape is similar to `searchMemory`'s `memory_detail_list`, where each item carries `id`, `memory_value`, and related fields. Refer to the API reference / OpenAPI for exact fields.

## Pair With Delete (Recommended Loop)

1. List memories by `user_id` with `getMemory` (or `searchMemory`) and record the target `id` and `memory_value`.
2. Delete precisely by `memory_ids` via [api-delete-memory.md](api-delete-memory.md); avoid user-wide deletion by `user_id`.
3. Run `getMemory` / `searchMemory` again to confirm the target memory is gone.
