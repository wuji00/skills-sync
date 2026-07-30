# Chat API

MemOS 提供内置记忆管理的对话 API，一次调用完成记忆召回、Prompt 组装、模型回复生成和会话写入。

## 端点

```
POST https://memos.memtensor.cn/api/openmem/v1/chat
```

## 与记忆操作 API 的区别

| 维度 | Chat API | 记忆操作 API (addMessage + searchMemory) |
|------|----------|----------------------------------------|
| 集成复杂度 | 低，开箱即用 | 中等，需自行编排 |
| 记忆管理 | 自动 | 手动添加、检索、组装 |
| 模型回复 | MemOS 内置模型生成 | 调用你自己的外部模型 |
| 控制力 | 适合通用配置 | 适合复杂 Pipeline 和精细控制 |

**选择建议**：快速验证 PoC 或通用 AI 对话 → Chat API；复杂 Agent 或深度业务集成 → addMessage + searchMemory。

## 必要参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `user_id` | string | 用户唯一标识 |
| `conversation_id` | string | 会话唯一标识 |
| `query` | string | 用户当前消息 |

## 基本用法

### Python SDK

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.chat(
    user_id="user_001",
    conversation_id="conv_002",
    query="国庆想去旅游，推荐一个我没去过的城市"
)
print(res)
```

### HTTP

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"

data = {
    "user_id": "user_001",
    "conversation_id": "conv_002",
    "query": "国庆想去旅游，推荐一个我没去过的城市"
}

res = requests.post(
    f"{BASE_URL}/chat",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
print(res.json())
```

### cURL

```bash
curl "$MEMOS_BASE_URL/chat" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "conversation_id": "conv_002",
    "query": "国庆想去旅游，推荐一个我没去过的城市"
  }'
```

## 可选参数

### 控制记忆召回

| 参数 | 类型 | 说明 |
|------|------|------|
| `filter` | object | 记忆过滤条件 |
| `knowledgebase_ids` | array | 可搜索的知识库 ID |
| `relativity` | float | 相关性阈值 |
| `memory_limit_number` | int | 事实记忆最大数量 |

### 控制模型行为

| 参数 | 类型 | 说明 |
|------|------|------|
| `model_name` | string | 指定对话模型（如 `"qwen2.5-72b-instruct"`） |
| `stream` | bool | 是否流式返回 |
| `temperature` | float | 随机性控制 |
| `top_p` | float | 候选 token 范围 |
| `max_tokens` | int | 最大生成长度 |
| `system_prompt` | string | 自定义系统提示词（覆盖默认） |

### 控制记忆写入

| 参数 | 类型 | 说明 |
|------|------|------|
| `add_message_on_answer` | bool | 是否将本轮对话写入记忆（默认 true） |
| `agent_id` | string | 标记所属 Agent |
| `app_id` | string | 标记所属应用 |
| `tags` | array | 添加标签 |
| `info` | object | 业务元数据 |

## 高级用法

### 联合知识库 + 过滤

```python
data = {
    "user_id": "user_001",
    "conversation_id": "conv_002",
    "query": "用知识库总结差旅报销规则",
    "knowledgebase_ids": ["kb_xxx"],
    "filter": {
        "and": [
            {"tags": {"contains": "差旅"}},
            {"create_time": {"gte": "2025-01-01"}}
        ]
    },
    "relativity": 0.8,
    "memory_limit_number": 9
}
```

### 指定模型和生成参数

```python
data = {
    "user_id": "user_001",
    "conversation_id": "conv_002",
    "query": "用简洁的语气总结我的旅行偏好",
    "model_name": "qwen2.5-72b-instruct",
    "temperature": 0.7,
    "max_tokens": 1024
}
```

### 仅回复不写入记忆

```python
data = {
    "user_id": "user_001",
    "conversation_id": "conv_002",
    "query": "这次只是随便问问，不需要记住",
    "add_message_on_answer": False
}
```

## 限制

- 输入上限：8,000 tokens
- 输出上限：最多召回 25 条事实记忆 + 25 条偏好记忆
