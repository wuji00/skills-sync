# Memory Filters

Use structured filters to narrow the candidate memory scope before semantic retrieval. Filters are not keyword search; they define which memories can be considered.

## How Filters Work

1. MemOS first applies the `filter` condition to candidate memories.
2. It then performs semantic matching inside that filtered candidate set.

## Two Filter Modes

### Global Filter

Put conditions directly under `filter`:

```json
{
  "filter": {
    "and": [
      {"tags": {"contains": "reading"}},
      {"create_time": {"gte": "2025-01-01"}},
      {"create_time": {"lte": "2025-12-31"}},
      {"scene": "chat"}
    ]
  }
}
```

### Source-Specific Filter

Set separate filters for `user`, `public`, and `knowledgebase` sources:

```json
{
  "filter": {
    "knowledgebase": {
      "and": [
        {"tags": {"contains": "policy"}},
        {"create_time": {"gte": "2025-01-01"}}
      ]
    },
    "user": {
      "and": [
        {"agent_id": "compliance_assistant"},
        {"scene": "chat"}
      ]
    },
    "public": {
      "and": [
        {"tags": {"contains": "announcement"}}
      ]
    }
  }
}
```

| Source | Meaning |
| --- | --- |
| `user` | User personal memories from conversation history. |
| `public` | Project-level public memories shared across users. |
| `knowledgebase` | Memories extracted from documents or Skill uploads. |

## Fields And Operators

The top level of a filter must be `and` or `or`. Do not put `user_id` inside `filter`; pass `user_id` as a request parameter.

### Instance Fields

| Field | Type | Operator | Example |
| --- | --- | --- | --- |
| `agent_id` | string | equals | `{"agent_id": "agent_123"}` |
| `app_id` | string | equals | `{"app_id": "app_123"}` |

### Metadata Fields From `info`

Fields written through `info` are referenced directly in the filter, not nested under `info`.

| Field | Type | Operator | Example |
| --- | --- | --- | --- |
| `business_type` | string | equals | `{"business_type": "shopping"}` |
| `biz_id` | string | equals | `{"biz_id": "order_123456"}` |
| `scene` | string | equals | `{"scene": "payment"}` |
| `custom_status` | string | equals | `{"custom_status": "VIP3"}` |

### Tags

| Field | Type | Operator | Example |
| --- | --- | --- | --- |
| `tags` | list | `contains` | `{"tags": {"contains": "finance"}}` |

### Time Fields

| Field | Type | Operators | Example |
| --- | --- | --- | --- |
| `create_time` | string | `lt`, `gt`, `lte`, `gte` | `{"create_time": {"gte": "2025-12-10"}}` |
| `update_time` | string | `lt`, `gt`, `lte`, `gte` | `{"update_time": {"lte": "2025-12-10"}}` |

## Examples

### Filter By Agent

```python
payload = {
    "user_id": "user_001",
    "query": "...",
    "filter": {
        "or": [
            {"agent_id": "agent_123"},
            {"agent_id": "agent_456"}
        ]
    }
}
```

### Filter By Business Scenario

```python
payload = {
    "user_id": "user_001",
    "query": "...",
    "filter": {
        "and": [
            {"business_type": "travel"},
            {"scene": "payment"},
            {"custom_status": "v1"}
        ]
    }
}
```

### Filter By Tag And Time Range

```python
payload = {
    "user_id": "user_001",
    "query": "...",
    "filter": {
        "and": [
            {"tags": {"contains": "weather"}},
            {"create_time": {"gte": "2025-12-01"}},
            {"create_time": {"lte": "2025-12-31"}}
        ]
    }
}
```

## Common Mistakes

- Do not mix global and source-specific filter shapes in one request.
- Do not write `{"info": {"scene": "chat"}}`; use `{"scene": "chat"}`.
- Do not use filters to replace application authorization. Tenant/workspace scoping still belongs in your app.
