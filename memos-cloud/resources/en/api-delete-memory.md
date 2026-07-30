# deleteMemory API

Use `deleteMemory` to delete memories from MemOS. It supports deleting all memories for one user or deleting specific memory IDs.

## Endpoint

```text
POST https://memos.memtensor.cn/api/openmem/v1/delete/memory
```

## Deletion Modes

| Mode | Parameter | Effect |
| --- | --- | --- |
| Delete by user | `user_id` | Deletes all memories for the user, including fact, preference, Skill, and Tool memories. |
| Delete by ID | `memory_ids` | Deletes one or more specific memories. |

## Usage

### Delete All Memories For A User

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.delete_memory(user_id="user_001")
print(res)
```

### Delete Specific Memories

Memory IDs come from `search/memory` or [`get/memory`](api-get-memory.md) responses.

```python
res = client.delete_memory(
    memory_ids=["6b23b583-f4c4-4a8f-b345-58d0c48fea04"]
)
print(res)
```

### HTTP

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"

# Delete by user
payload = {"user_id": "user_001"}

# Or delete by ID
payload = {"memory_ids": ["6b23b583-f4c4-4a8f-b345-58d0c48fea04"]}

res = requests.post(
    f"{BASE_URL}/delete/memory",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
print(res.json())
```

### cURL

```bash
curl "$MEMOS_BASE_URL/delete/memory" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001"}'

curl "$MEMOS_BASE_URL/delete/memory" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"memory_ids": ["6b23b583-f4c4-4a8f-b345-58d0c48fea04"]}'
```

## Verification

`data.success == "true"` indicates the delete request succeeded. Run `searchMemory` afterward to verify the deleted memory is no longer returned.

## Guardrails

- Prefer deleting by `memory_ids` when the user wants to remove one concrete memory.
- Require explicit confirmation before deleting all memories for a `user_id`.
- Pass the exact configured `user_id`; do not normalize or shorten it.

## Failure Triage

| Symptom | Check |
| --- | --- |
| Similar memory still appears | Another similar memory may exist. Search, inspect IDs, and delete the concrete item if appropriate. |
| Delete by user removed too much | This is destructive. Add an explicit confirmation boundary before user-wide deletion. |
| Delete seems successful but search still returns the item | Check processing/index delay, wrong `user_id`, wrong `memory_ids`, or tenant/workspace authorization bugs in the app. |
