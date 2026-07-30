# getMemory API

按 `user_id` 拉取某个用户已有的记忆，支持分页。常用于查看用户记忆全貌，以及**删除前定位 `memory_ids`**（删除高风险，先看清要删什么）。

与 `searchMemory` 的区别：`searchMemory` 是按 query 语义召回相关记忆；`getMemory` 是按用户**列出/翻页**记忆，不依赖查询语义。

## 端点

```
POST https://memos.memtensor.cn/api/openmem/v1/get/memory
```

## 必要参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `user_id` | string | 用户唯一标识 |

## 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | int | 1 | 页码（对应 CLI `--page`） |
| `size` | int | 10 | 每页条数（对应 CLI `--size`） |
| `include_preference` | bool | true | 是否一并返回偏好记忆 |
| `include_tool_memory` | bool | false | 是否一并返回工具记忆 |

## 用法

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

> SDK 签名: `get_memory(user_id, include_preference=True, page=1, size=10, include_tool_memory=False)`

### HTTP

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"

data = {"user_id": "memos_user_123"}

res = requests.post(
    f"{BASE_URL}/get/memory",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
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

### CLI（验证用）

```bash
memos get user_123 --format json --detail detail
```

## 返回

返回该用户的记忆列表，结构与 `searchMemory` 的 `memory_detail_list` 类似，每条带 `id`、`memory_value` 等字段。具体字段以 API reference / OpenAPI 为准。

## 与删除配合（推荐闭环）

1. 用 `getMemory`（或 `searchMemory`）按 `user_id` 列出记忆，记录目标 `id`、`memory_value`。
2. 用 [api-delete-memory.md](api-delete-memory.md) 按 `memory_ids` 精确删除，避免按 `user_id` 全量删。
3. 删除后再 `getMemory` / `searchMemory` 确认目标记忆已不在。
