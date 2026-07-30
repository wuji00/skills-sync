# addFeedback API

通过自然语言反馈修正和更新记忆，无需手动定位具体记忆条目。

## 端点

```
POST https://memos.memtensor.cn/api/openmem/v1/add/feedback
```

## 必要参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `user_id` | string | 用户唯一标识 |
| `conversation_id` | string | 提供上下文的会话标识 |
| `feedback_content` | string | 自然语言反馈内容 |

## 可选参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `allow_knowledgebase_ids` | array | 允许反馈写入的知识库 ID 列表 |

## 工作原理

1. **有效性分析**：结合当前对话上下文判断反馈是否有效
2. **更新类型识别**：判定是关键词替换还是语义更新
3. **记忆更新**：写入新记忆并更新/覆盖冲突的旧记忆

## 用法

### 语义修正

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.add_feedback(
    user_id="user_001",
    conversation_id="feedback_conv",
    feedback_content="办公软件采购限额是600元，不是800元。",
    allow_knowledgebase_ids=["kb_xxx"]
)
print(res)
```

### 关键词替换

```python
res = client.add_feedback(
    user_id="user_001",
    conversation_id="feedback_conv",
    feedback_content="以后我改名了，把所有的「用户1」替换成「用户2」"
)
```

### HTTP

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"

data = {
    "user_id": "user_001",
    "conversation_id": "feedback_conv",
    "feedback_content": "办公软件采购限额是600元，不是800元。",
    "allow_knowledgebase_ids": ["kb_xxx"]
}

res = requests.post(
    f"{BASE_URL}/add/feedback",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
print(res.json())
```

## 适用场景

| 场景 | 示例反馈 |
|------|---------|
| 纠正错误事实 | "我的生日是3月15日，不是3月5日" |
| 更新过时信息 | "我已经从上海搬到北京了" |
| 修正知识库内容 | "报销标准已更新为新版本" |
| 全局关键词替换 | "把所有的A替换成B" |

## 反馈后如何验证

1. 调用 `addFeedback` 后等待处理完成；如果是异步处理，几秒后重试检索。
2. 用能够命中新事实的 `query` 调用 `searchMemory`。
3. 检查新事实是否出现，旧事实是否被降权、覆盖或不再召回。
4. 如果更新的是知识库，必须传入正确的 `allow_knowledgebase_ids` 并用知识库相关问题验证。

## 什么时候不适合用 addFeedback

| 场景 | 推荐方式 |
|------|---------|
| 用户要删除某条具体记忆 | 使用 `deleteMemory`，不要用反馈暗示删除。 |
| 需要导入大量历史信息 | 使用 `addMessage` 批量写入，不要把大段历史塞进反馈。 |
| 只是当前对话临时纠正 | 在当前 prompt 中处理即可，不一定写长期反馈。 |
| 涉及敏感或受监管数据 | 先确认产品同意、留存和删除策略。 |
