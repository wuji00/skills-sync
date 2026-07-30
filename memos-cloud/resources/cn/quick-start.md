# 快速入门

如果用户的目标是“把 MemOS Cloud 接入现有项目”，先从 [Starter Pack](starter-pack.md) 开始。它包含可复制给 Agent 的中文 Prompt、项目检查清单、FTS 验证和安全边界。本文件只用于最小 Cloud API/SDK 跑通。

## 可复制给 Agent 的 Prompt

可复制的接入 Prompt 统一维护在 [starter-pack.md](starter-pack.md)（“可复制给 Agent 的中文 Prompt”一节），此处不重复，避免多处漂移。

## 环境准备

1. 注册并登录 [MemOS Cloud](https://memos-dashboard.openmem.net/quickstart)
2. 在 [API Key 页面](https://memos-dashboard.openmem.net/apikeys) 获取 API Key
3. 准备 Python 3.10+ 环境

## 安装 SDK

```bash
pip install MemoryOS -U
```

## 鉴权配置

### Python SDK

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")
```

### HTTP 直调

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"
headers = {"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"}
```

### cURL

```bash
export MEMOS_API_KEY="YOUR_API_KEY"
export MEMOS_BASE_URL="https://memos.memtensor.cn/api/openmem/v1"
```

## 核心概念

| 概念 | 说明 |
|------|------|
| `user_id` | 用户唯一标识，所有记忆操作必须关联用户 |
| `conversation_id` | 会话标识，区分不同对话上下文 |
| `agent_id` | Agent 标识，隔离不同 Agent 产生的记忆 |
| `messages` | 有序消息列表（role: user/assistant/system/tool） |

## 第一个记忆操作

### Step 1: 写入记忆

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.add_message(
    messages=[
        {"role": "user", "content": "我下周要去成都出差，帮我订靠近天府广场的酒店"},
        {"role": "assistant", "content": "好的，我来帮您查找天府广场附近的酒店。"}
    ],
    user_id="user_001",
    conversation_id="conv_001"
)
print(res)
```

### Step 2: 检索记忆

```python
res = client.search_memory(
    query="用户下次出差想住哪个区域？",
    user_id="user_001"
)
print(res)
```

MemOS 会自动从历史对话中提取事实记忆（用户下周去成都出差）和偏好记忆（倾向天府广场附近酒店），在后续对话中提供精准上下文。

## 记忆类型

MemOS 自动生成以下类型的记忆：

| 类型 | 说明 | 示例 |
|------|------|------|
| 事实记忆 | 客观信息 | "用户住在上海" |
| 偏好记忆 | 用户倾向 | "用户偏好简洁直接的回答" |
| Skill 记忆 | 可复用任务方法 | "如何规划旅行行程" |
| Tool 记忆 | 工具使用经验 | "查天气用 get_weather 工具" |
| 知识库记忆 | 文档/策略/FAQ | "报销政策：办公软件限额600元" |

## 下一步

- 深入了解 [addMessage API](api-add-message.md) 的完整参数
- 了解 [searchMemory API](api-search-memory.md) 的过滤和控制
- 使用 [Chat API](api-chat.md) 一步完成记忆召回+生成回复
