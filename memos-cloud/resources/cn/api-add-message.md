# addMessage API

向 MemOS 写入原始对话或信息，系统自动提取事实、偏好等记忆并存储。

## 端点

```
POST https://memos.memtensor.cn/api/openmem/v1/add/message
```

## 必要参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `user_id` | string | 用户唯一标识 |
| `conversation_id` | string | 会话唯一标识 |
| `messages` | array | 消息列表，每条含 `role` 和 `content` |

## 基本用法

### Python SDK

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.add_message(
    messages=[
        {"role": "user", "content": "我喜欢辣的食物"},
        {"role": "assistant", "content": "好的，已记下您的口味偏好。"}
    ],
    user_id="user_001",
    conversation_id="conv_001"
)
```

### HTTP

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"

data = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "messages": [
        {"role": "user", "content": "我喜欢辣的食物"},
        {"role": "assistant", "content": "好的，已记下您的口味偏好。"}
    ]
}

res = requests.post(
    f"{BASE_URL}/add/message",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
```

### cURL

```bash
curl "$MEMOS_BASE_URL/add/message" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "messages": [
      {"role": "user", "content": "我喜欢辣的食物"},
      {"role": "assistant", "content": "好的，已记下您的口味偏好。"}
    ]
  }'
```

## 可选参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `chat_time` | string | 消息中每条的实际发生时间，格式 `"2025-09-12 08:00:00"` |
| `agent_id` | string | Agent 标识，用于按 Agent 隔离记忆 |
| `app_id` | string | 应用标识 |
| `tags` | array | 自定义标签，用于后续过滤 |
| `info` | object | 业务元数据（如 `scene`, `biz_id`, `business_type`, `custom_status`） |
| `async_mode` | bool | 异步模式，默认 true（参见 features-async-mode.md） |
| `source` | string | 来源标识 |
| `allow_public` | bool | 是否允许记忆被公开检索（默认 false） |
| `allow_knowledgebase_ids` | array | 允许写入的知识库 ID 列表 |

## 高级用法

### 指定消息时间（批量导入历史对话）

```python
data = {
    "user_id": "user_001",
    "conversation_id": "conv_history",
    "messages": [
        {"role": "user", "content": "我喜欢辣的", "chat_time": "2025-09-12 08:00:00"},
        {"role": "assistant", "content": "好的", "chat_time": "2025-09-12 08:01:00"},
    ]
}
```

### 按 Agent 隔离记忆

```python
data = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "agent_id": "health_assistant",
    "messages": [
        {"role": "user", "content": "今天跑了5公里，膝盖有点酸"},
        {"role": "assistant", "content": "建议明天降低运动强度"}
    ]
}
```

### 写入用户偏好/行为数据

不只是对话，也可以直接写入结构化的用户偏好信息：

```python
data = {
    "user_id": "user_001",
    "conversation_id": "profile_import",
    "messages": [
        {
            "role": "user",
            "content": """
喜欢的电影类型：科幻、动作、喜剧
聊天风格偏好：幽默、温暖、随意
希望 AI 帮忙的事情：每日学习规划、电影推荐
"""
        }
    ]
}
```

### 带标签和业务元数据

```python
data = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "tags": ["运动建议", "健身计划"],
    "info": {"scene": "fitness", "business_type": "health"},
    "messages": [
        {"role": "user", "content": "今天跑了5公里"},
        {"role": "assistant", "content": "跑步记录已更新"}
    ]
}
```

## 多模态消息

支持图片和文档，参见 [features-multimodal.md](features-multimodal.md)。

## Tool Calling 消息

支持 tool_calls 和 tool 角色消息，参见 [features-tool-memory.md](features-tool-memory.md)。

## 写入时机建议

| 策略 | 适用场景 |
|------|---------|
| 一次性导入 | 将已有用户对话历史批量导入 MemOS |
| 实时写入 | 每次用户发消息时同步写入 |
| 按轮次写入 | 每隔几轮对话批量写入 |

## 限制

- 单次输入上限：40,000 tokens
- 每分钟总 tokens 上限：400,000
- 建议 QPS ≤ 50
