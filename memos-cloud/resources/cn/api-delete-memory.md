# deleteMemory API

从 MemOS 删除记忆，支持按用户全部删除或按指定记忆 ID 删除。

## 端点

```
POST https://memos.memtensor.cn/api/openmem/v1/delete/memory
```

## 两种删除方式

| 方式 | 参数 | 效果 |
|------|------|------|
| 按用户删除 | `user_id` | 删除该用户所有记忆（事实、偏好、Skill、Tool 等） |
| 按 ID 删除 | `memory_ids` | 删除指定的一条或多条记忆 |

## 用法

### 删除用户所有记忆

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.delete_memory(user_id="user_001")
print(res)
```

### 删除指定记忆

记忆 ID 来自 `search/memory` 或 [`get/memory`](api-get-memory.md) 返回的 `id` 字段。

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

# 按用户删除
data = {"user_id": "user_001"}

# 或按 ID 删除
data = {"memory_ids": ["6b23b583-f4c4-4a8f-b345-58d0c48fea04"]}

res = requests.post(
    f"{BASE_URL}/delete/memory",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
print(res.json())
```

### cURL

```bash
# 按用户删除
curl "$MEMOS_BASE_URL/delete/memory" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001"}'

# 按 ID 删除
curl "$MEMOS_BASE_URL/delete/memory" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"memory_ids": ["6b23b583-f4c4-4a8f-b345-58d0c48fea04"]}'
```

## 返回

`"data.success": "true"` 表示删除成功。可再次调用 searchMemory 确认记忆已不被召回。

## 验证步骤

1. 删除前先用 `searchMemory` 或 [getMemory](api-get-memory.md) 找到目标记忆，并记录 `id`、`memory_value`、`user_id`。
2. 优先按 `memory_ids` 删除具体记忆。
3. 删除后使用同一 `user_id` 和相近 `query` 再次调用 `searchMemory`。
4. 如果仍能召回，确认是否是异步索引延迟、同义记忆仍存在，或删除的是错误 `memory_id`。

## 边界与误用

| 场景 | 建议 |
|------|------|
| 用户只想删一条记忆 | 先搜索定位 `memory_ids`，不要直接按 `user_id` 全量删除。 |
| 用户要求清空所有记忆 | 需要明确确认，并传入完整原始 `user_id`。 |
| 多租户产品 | 删除前先在业务层校验 tenant/workspace 权限，不要只依赖 prompt。 |
| 删除后仍召回类似内容 | 检查是否存在另一条相似记忆；必要时继续按 ID 删除。 |

不要规范化、截断或猜测 `user_id`。如果用户提供的是带命名空间的 ID，必须原样传递。
