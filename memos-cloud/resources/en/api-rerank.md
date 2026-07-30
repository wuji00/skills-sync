# rerank API

Reorder a set of candidate documents by relevance to a query. Commonly used as retrieval post-processing. **It is not a replacement for searchMemory**: searchMemory recalls from user memory, while rerank only reorders candidate texts you already have.

## Endpoint

```text
POST https://memos.memtensor.cn/api/openmem/v1/rerank
```

## Required Parameters

| Parameter | Type | Meaning |
| --- | --- | --- |
| `query` | string | Query used to measure relevance. |
| `documents` | array | List of candidate document texts. |

## Optional Parameters

| Parameter | Type | Meaning |
| --- | --- | --- |
| `model` | string | Reranker model, for example `"memos-reranker-0.6b"`. |
| `top_n` | int | Return only the top N most relevant items (CLI `--top-n`). |

## Usage

### HTTP

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"

payload = {
    "model": "memos-reranker-0.6b",
    "query": "What are the user's hobbies?",
    "documents": [
        "The user plays badminton.",
        "The user is a backend developer in Hangzhou.",
        "The user prefers concise replies.",
        "The user travels to Beijing next Wednesday."
    ]
}

res = requests.post(
    f"{BASE_URL}/rerank",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
print(res.json())
```

### cURL

```bash
curl "$MEMOS_BASE_URL/rerank" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "memos-reranker-0.6b",
    "query": "What are the user'\''s hobbies?",
    "documents": ["The user plays badminton.", "The user is a backend developer."]
  }'
```

### CLI (for verification)

```bash
memos rerank "python backend" "Flask guide" "React guide" --top-n 2 --format json
```

## Response

Returns the candidates ordered by relevance (each with a relevance score/index). Refer to the API reference / OpenAPI for exact fields.

## When To Use, When Not To

| Scenario | Guidance |
| --- | --- |
| You already have candidate snippets (for example external RAG results) and want to rank them | Use rerank. |
| You want to recall facts/preferences from long-term user memory | Use `searchMemory`, not rerank. |
| The candidate list is short and order does not matter | Skip rerank. |
