# Memory Filters

在检索记忆时，使用结构化过滤条件按标签、时间、Agent、业务字段等精确筛选候选记忆范围。

## 工作原理

1. **先过滤范围**：MemOS 根据 `filter` 条件严格筛选候选记忆
2. **再语义检索**：在过滤后的候选集中进行语义匹配

Filter 是检索前的范围控制机制，不是关键词搜索。

## 两种过滤模式

### 全局过滤

不区分记忆来源，条件直接放在 `filter` 根级：

```json
{
  "filter": {
    "and": [
      {"tags": {"contains": "阅读"}},
      {"create_time": {"gte": "2025-01-01"}},
      {"create_time": {"lte": "2025-12-31"}},
      {"scene": "chat"}
    ]
  }
}
```

### 分源过滤

对 `user`、`public`、`knowledgebase` 分别设置过滤条件：

```json
{
  "filter": {
    "knowledgebase": {
      "and": [
        {"tags": {"contains": "政策"}},
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
        {"tags": {"contains": "公告"}}
      ]
    }
  }
}
```

| 来源 | 说明 |
|------|------|
| `user` | 用户个人记忆（来自对话历史） |
| `public` | 项目级公共记忆（跨用户共享） |
| `knowledgebase` | 知识库记忆（来自文档/Skill） |

## 可用字段和运算符

Filter 根级必须是 `and` 或 `or`，不支持在 filter 中指定 `user_id`。

### 实例字段

| 字段 | 类型 | 运算符 | 示例 |
|------|------|--------|------|
| `agent_id` | string | `=` | `{"agent_id": "agent_123"}` |
| `app_id` | string | `=` | `{"app_id": "app_123"}` |

### 元数据字段（来自 addMessage 的 `info`）

在 filter 中直接用字段名，不要包裹在 `info` 中。

| 字段 | 类型 | 运算符 | 示例 |
|------|------|--------|------|
| `business_type` | string | `=` | `{"business_type": "shopping"}` |
| `biz_id` | string | `=` | `{"biz_id": "order_123456"}` |
| `scene` | string | `=` | `{"scene": "payment"}` |
| `custom_status` | string | `=` | `{"custom_status": "VIP3"}` |

### 标签字段

| 字段 | 类型 | 运算符 | 示例 |
|------|------|--------|------|
| `tags` | list | `contains` | `{"tags": {"contains": "finance"}}` |

### 时间字段

| 字段 | 类型 | 运算符 | 示例 |
|------|------|--------|------|
| `create_time` | string | `lt`, `gt`, `lte`, `gte` | `{"create_time": {"gte": "2025-12-10"}}` |
| `update_time` | string | `lt`, `gt`, `lte`, `gte` | `{"update_time": {"lte": "2025-12-10"}}` |

## 使用示例

### 按 Agent 过滤

```python
data = {
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

### 按业务场景过滤

```python
data = {
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

### 按标签和时间范围过滤

```python
data = {
    "user_id": "user_001",
    "query": "...",
    "filter": {
        "and": [
            {"tags": {"contains": "天气"}},
            {"create_time": {"gte": "2025-12-01"}},
            {"create_time": {"lte": "2025-12-31"}}
        ]
    }
}
```

## 注意

- 全局过滤和分源过滤二选一
- 写入时通过 `info` 传入的字段，检索时在 filter 中直接使用字段名
- 错误写法：`{"info": {"scene": "chat"}}` → 正确写法：`{"scene": "chat"}`
