# 集成指南

本文档介绍如何将 MemOS Cloud 的长期记忆能力集成到你的 AI 应用中。

## 集成方式对比

| 集成方式 | 适合场景 | 特点 |
|---------|---------|------|
| Python SDK | Python Agent 应用、后端服务 | 推荐，OOP 接口，开箱即用 |
| HTTP 直调 | 非 Python 环境、需要更底层控制 | 语言无关，适合任何 HTTP 客户端 |
| cURL | 快速调试、接口验证 | 即时测试，无需编码 |

---

## 1. Python SDK

推荐方式，提供完整的面向对象接口。

### 安装

```bash
pip install MemoryOS -U
```

### 初始化

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")
```

### 核心调用

```python
# 写入记忆
client.add_message(
    messages=[
        {"role": "user", "content": "用户输入"},
        {"role": "assistant", "content": "Agent 回复"}
    ],
    user_id="user_001",
    conversation_id="conv_001"
)

# 检索记忆
result = client.search_memory(query="相关查询", user_id="user_001")

# 一站式对话（自动召回记忆 + 生成回复）
response = client.chat(
    messages=[{"role": "user", "content": "用户输入"}],
    user_id="user_001"
)
```

详见各 API 文档：[addMessage](api-add-message.md) | [searchMemory](api-search-memory.md) | [Chat](api-chat.md)

---

## 2. HTTP 直调

适合非 Python 环境或需要精细控制 HTTP 行为的场景。

### 基础配置

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"
headers = {"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"}
```

### 写入记忆

```python
resp = requests.post(
    f"{BASE_URL}/add/message",
    headers=headers,
    json={
        "messages": [
            {"role": "user", "content": "用户输入"},
            {"role": "assistant", "content": "Agent 回复"}
        ],
        "user_id": "user_001",
        "conversation_id": "conv_001"
    }
)
```

### 检索记忆

```python
resp = requests.post(
    f"{BASE_URL}/search/memory",
    headers=headers,
    json={
        "query": "相关查询",
        "user_id": "user_001"
    }
)
memories = resp.json()
```

---

## 3. cURL

适合快速验证接口和调试。

### 写入

```bash
curl -X POST "https://memos.memtensor.cn/api/openmem/v1/add/message" \
  -H "Authorization: Token YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "用户输入"}],
    "user_id": "user_001",
    "conversation_id": "conv_001"
  }'
```

### 检索

```bash
curl -X POST "https://memos.memtensor.cn/api/openmem/v1/search/memory" \
  -H "Authorization: Token YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "相关查询",
    "user_id": "user_001"
  }'
```

---

## 4. Agent Loop 集成架构

在自建 Agent 中集成 MemOS 的典型架构：

```
用户输入
   │
   ▼
┌──────────────────────────────────────┐
│  1. searchMemory(query=用户输入)      │  ← 检索相关记忆
│     获取 facts / preferences / tools │
└──────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────┐
│  2. 组装 Prompt                       │
│     System Prompt + 记忆上下文 + 用户输入 │
└──────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────┐
│  3. 调用 LLM 生成回复                 │
└──────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────┐
│  4. addMessage(messages=[...])        │  ← 写入本轮对话
│     MemOS 自动提取/更新记忆           │
└──────────────────────────────────────┘
   │
   ▼
返回回复给用户
```

### 伪代码示例

```python
from memos.api.client import MemOSClient
from your_llm import call_llm

client = MemOSClient(api_key="YOUR_API_KEY")

def agent_respond(user_input: str, user_id: str, conv_id: str) -> str:
    # Step 1: 检索记忆
    memories = client.search_memory(query=user_input, user_id=user_id)
    memory_context = format_memories(memories)

    # Step 2: 组装 Prompt
    messages = [
        {"role": "system", "content": f"你是一个智能助手。以下是关于该用户的记忆：\n{memory_context}"},
        {"role": "user", "content": user_input}
    ]

    # Step 3: 调用 LLM
    reply = call_llm(messages)

    # Step 4: 写入记忆
    client.add_message(
        messages=[
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": reply}
        ],
        user_id=user_id,
        conversation_id=conv_id
    )

    return reply
```

### 关键设计要点

- **检索在前，写入在后**：先获取历史记忆注入上下文，生成回复后再写入新记忆
- **user_id 隔离**：每个终端用户使用独立的 user_id，记忆互不干扰
- **conversation_id 关联**：同一会话使用同一 conv_id，帮助 MemOS 理解对话连贯性
- **异步写入可选**：写入操作可异步执行，不阻塞响应返回（详见 [异步模式](features-async-mode.md)）
