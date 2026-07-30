# searchMemory API

从 MemOS 检索与查询相关的记忆，返回事实记忆、偏好记忆、Tool 记忆和 Skill。

## 端点

```
POST https://memos.memtensor.cn/api/openmem/v1/search/memory
```

## 必要参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `user_id` | string | 用户唯一标识（必填） |
| `query` | string | 检索查询，用于语义匹配 |

## 基本用法

### Python SDK

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.search_memory(
    query="用户喜欢什么类型的食物？",
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

data = {
    "query": "用户喜欢什么类型的食物？",
    "user_id": "user_001",
    "conversation_id": "conv_002"
}

res = requests.post(
    f"{BASE_URL}/search/memory",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
print(res.json())
```

### cURL

```bash
curl "$MEMOS_BASE_URL/search/memory" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "用户喜欢什么类型的食物？",
    "user_id": "user_001",
    "conversation_id": "conv_002"
  }'
```

## 返回结构

```json
{
  "code": 0,
  "data": {
    "memory_detail_list": [
      {
        "id": "uuid",
        "memory_key": "口味偏好",
        "memory_value": "用户喜欢辣的食物",
        "memory_type": "LongTermMemory",
        "create_time": 1766041646311,
        "conversation_id": "conv_001",
        "status": "activated",
        "confidence": 0.99,
        "tags": ["饮食", "偏好"],
        "relativity": 0.89
      }
    ],
    "preference_detail_list": [
      {
        "preference_type": "explicit_preference",
        "preference": "用户喜欢辣的食物",
        "conversation_id": "conv_001"
      }
    ],
    "tool_memory_detail_list": [],
    "skill_detail_list": []
  },
  "message": "ok"
}
```

## 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `conversation_id` | string | - | 优先召回当前会话相关记忆 |
| `filter` | object | - | 结构化过滤条件（参见 features-filters.md） |
| `relativity` | float | 0.45 | 相关性阈值，越高越严格 |
| `memory_limit_number` | int | 6 | 返回事实记忆的最大数量 |
| `include_preference` | bool | true | 是否召回偏好记忆 |
| `preference_limit_number` | int | 6 | 偏好记忆最大数量 |
| `include_skill` | bool | false | 是否召回 Skill 记忆 |
| `include_tool_memory` | bool | false | 是否召回 Tool 记忆 |
| `tool_memory_limit_number` | int | 6 | Tool 记忆最大数量 |
| `knowledgebase_ids` | array | - | 可搜索的知识库 ID 列表 |

## 高级用法

### 使用 Filter 精确筛选

```python
data = {
    "user_id": "user_001",
    "query": "总结今年的阅读记忆",
    "filter": {
        "and": [
            {"tags": {"contains": "阅读"}},
            {"create_time": {"gte": "2025-01-01"}},
            {"create_time": {"lte": "2025-12-31"}}
        ]
    }
}
```

### 控制召回质量和数量

```python
data = {
    "user_id": "user_001",
    "query": "帮我规划成都5天行程",
    "relativity": 0.8,
    "memory_limit_number": 9
}
```

### 召回 Skill 和 Tool Memory

```python
data = {
    "user_id": "user_001",
    "query": "帮我规划一趟云南之旅",
    "include_skill": True,
    "include_tool_memory": True,
    "tool_memory_limit_number": 10
}
```

### 联合知识库检索

```python
data = {
    "user_id": "user_001",
    "query": "公司差旅报销标准是什么？",
    "knowledgebase_ids": ["kb_xxx"],
    "include_skill": True
}
```

## 将记忆注入 Prompt

检索到记忆后，将其注入到模型 prompt 中：

```python
memories = result["data"]["memory_detail_list"]
preferences = result["data"]["preference_detail_list"]

memory_text = "\n".join([f"- {m['memory_value']}" for m in memories])
pref_text = "\n".join([f"- {p['preference']}" for p in preferences])

system_prompt = f"""你是一个具有长期记忆的智能助手。

<memories>
  <facts>
{memory_text}
  </facts>
  <preferences>
{pref_text}
  </preferences>
</memories>

使用上述记忆回答用户问题，但不要提及"记忆检索"等内部实现。
"""
```

## 限制

- 单次输入上限：40,000 tokens
- 事实记忆输出上限：25 条
- 偏好记忆输出上限：25 条
- Tool 记忆输出上限：25 条
- Skill 输出上限：25 条
