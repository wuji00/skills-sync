# Knowledge Base

Create project-level knowledge bases, upload documents to build knowledge memories, and search them together with user personal memory.

## Difference From Traditional RAG

| Dimension | Traditional RAG | MemOS Knowledge Base |
| --- | --- | --- |
| Accuracy | More corpus means more noise | Structured extraction + lifecycle management |
| Result shape | Raw text chunks | Refined memory units |
| Retrieval scope | Broad corpus scan | Layered scheduling and targeted hits |
| Understanding | Similarity matching only | Can combine with user preferences |
| Evolution | Mostly static | Updates through feedback and conversation |

## Create A Knowledge Base

### Dashboard

Create it in [Dashboard - Knowledge Base](https://memos-dashboard.openmem.net/knowledgeBase/).

### HTTP

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"

payload = {
    "knowledgebase_name": "Company policy KB",
    "knowledgebase_description": "All company policies and workflow documents"
}

res = requests.post(
    f"{BASE_URL}/create/knowledgebase",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
kb_id = res.json()["data"]["knowledgebase_id"]
print(kb_id)
```

### Python SDK

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.create_knowledgebase(
    knowledgebase_name="Company policy KB",
    knowledgebase_description="All company policies and workflow documents"
)
kb_id = res.knowledgebase_id
print(kb_id)
```

## Upload Documents

### Upload Regular Documents

```python
payload = {
    "knowledgebase_id": "kb_xxx",
    "file": [
        {"content": "https://cdn.example.com/policy.pdf"}
    ]
}

res = requests.post(
    f"{BASE_URL}/add/knowledgebase-file",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
print(res.json())
```

SDK:

```python
res = client.add_knowledgebase_file(
    knowledgebase_id="kb_xxx",
    file=[{"content": "https://cdn.example.com/policy.pdf"}]
)
```

Supported document types: PDF, DOCX, DOC, TXT, JSON, MD, XML.

### Upload Skill (base64)

Skill files are passed as base64 with `type` set to `"skill"`:

```python
import base64

skill_markdown = """---
name: Customer return SOP
description: Guide agents through standard return handling
---

## Procedure

1. Confirm user identity and order number
2. Verify return reason against policy
3. Guide user to choose return method
4. Generate return tracking number
"""

encoded = base64.b64encode(skill_markdown.encode("utf-8")).decode("utf-8")

payload = {
    "knowledgebase_id": "kb_xxx",
    "file": [
        {
            "type": "skill",
            "name": "customer-return-sop.md",
            "content": f"data:text/markdown;base64,{encoded}"
        }
    ]
}

res = requests.post(
    f"{BASE_URL}/add/knowledgebase-file",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
print(res.json())
```

Or upload a remote Skill URL:

```python
payload = {
    "knowledgebase_id": "kb_xxx",
    "file": [{"type": "skill", "content": "https://cdn.example.com/SKILL.md"}]
}
```

See [Skill Memory](features-skill.md) for more Skill usage patterns.

## Query Knowledge Base Files

### List Files By Knowledge Base ID

```python
payload = {
    "knowledgebase_id": "kb_xxx",
    "type": "skill",   # Optional: "document" / "skill"
    "page": 1,
    "page_size": 20
}

res = requests.post(
    f"{BASE_URL}/get/knowledgebase-file",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
print(res.json())
```

### Query By File IDs

```python
payload = {"file_ids": ["file_xxx"]}

res = requests.post(
    f"{BASE_URL}/get/knowledgebase-file",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
print(res.json())
```

SDK:

```python
res = client.get_knowledgebase_file(file_ids=["file_xxx"])
```

Use this to check processing progress after upload or confirm a file is ready.

## Delete Knowledge Base Files

```python
payload = {"file_ids": ["file_xxx"]}

res = requests.post(
    f"{BASE_URL}/delete/knowledgebase-file",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
print(res.json())
```

SDK:

```python
res = client.delete_knowledgebase_file(file_ids=["file_xxx"])
```

## Delete A Knowledge Base

```python
payload = {"knowledgebase_id": "kb_xxx"}

res = requests.post(
    f"{BASE_URL}/delete/knowledgebase",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
print(res.json())
```

SDK:

```python
res = client.delete_knowledgebase(knowledgebase_id="kb_xxx")
```

> Deleting a knowledge base removes all its files and related memories. This cannot be undone.

## Search With Knowledge Bases

Pass `knowledgebase_ids` to `searchMemory`:

```python
payload = {
    "user_id": "user_001",
    "query": "What is the company travel reimbursement policy?",
    "knowledgebase_ids": ["kb_xxx"]
}

res = requests.post(
    f"{BASE_URL}/search/memory",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
```

MemOS combines:

- User personal memory (e.g. the user's device, role, or preference).
- Knowledge-base memory (e.g. installation steps, policy, or SOP).

## Use With Chat API

```python
payload = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "query": "Which VPN client should I install for my laptop?",
    "knowledgebase_ids": ["kb_xxx"]
}

res = requests.post(
    f"{BASE_URL}/chat",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
```

## Update Through Feedback

Use `addFeedback` with `allow_knowledgebase_ids` to update knowledge-base memories through natural language:

```python
payload = {
    "user_id": "user_001",
    "conversation_id": "feedback",
    "feedback_content": "The software reimbursement limit has changed to 600.",
    "allow_knowledgebase_ids": ["kb_xxx"]
}
```

## Knowledge Base API Summary

| Endpoint | Purpose | SDK Method |
| --- | --- | --- |
| `POST /create/knowledgebase` | Create knowledge base | `client.create_knowledgebase(...)` |
| `POST /add/knowledgebase-file` | Upload documents or Skills | `client.add_knowledgebase_file(...)` |
| `POST /get/knowledgebase-file` | Query file list/status | `client.get_knowledgebase_file(...)` |
| `POST /delete/knowledgebase-file` | Delete files | `client.delete_knowledgebase_file(...)` |
| `POST /delete/knowledgebase` | Delete entire knowledge base | `client.delete_knowledgebase(...)` |

## Upload Limits

- Supported types: PDF, DOCX, DOC, TXT, JSON, MD, XML.
- Single file: up to 100 MB and up to 500 pages.
- Single upload request: up to 20 files.
- Skill file: `.md` up to 100 KB or `.zip` up to 20 MB (up to 200 extracted files).
