# 知识库

创建项目级知识库，上传文档建立知识记忆，与用户个人记忆联合检索。

## 与传统 RAG 的区别

| 维度 | 传统 RAG | MemOS 知识库 |
|------|---------|-------------|
| 准确性 | 语料越多噪声越大 | 结构化提取+生命周期管理 |
| 结果形态 | 原始文本段落 | 精炼的记忆单元 |
| 检索范围 | 全量语料扫描 | 分层调度，精准命中 |
| 理解能力 | 仅相似度匹配 | 结合用户偏好理解 |
| 进化能力 | 静态 | 通过反馈和对话动态更新 |

## 创建知识库

### 通过控制台

在 [Dashboard - 知识库](https://memos-dashboard.openmem.net/knowledgeBase/) 页面创建。

### HTTP

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"

data = {
    "knowledgebase_name": "企业政策知识库",
    "knowledgebase_description": "包含公司各项政策和流程文档"
}

res = requests.post(
    f"{BASE_URL}/create/knowledgebase",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
kb_id = res.json()["data"]["knowledgebase_id"]
print(kb_id)
```

### Python SDK

```python
from memos.api.client import MemOSClient

client = MemOSClient(api_key="YOUR_API_KEY")

res = client.create_knowledgebase(
    knowledgebase_name="企业政策知识库",
    knowledgebase_description="包含公司各项政策和流程文档"
)
kb_id = res.knowledgebase_id
print(kb_id)
```

## 上传文档

### 上传普通文档

```python
data = {
    "knowledgebase_id": "kb_xxx",
    "file": [
        {"content": "https://cdn.example.com/policy.pdf"}
    ]
}

res = requests.post(
    f"{BASE_URL}/add/knowledgebase-file",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
print(res.json())
```

SDK：

```python
res = client.add_knowledgebase_file(
    knowledgebase_id="kb_xxx",
    file=[{"content": "https://cdn.example.com/policy.pdf"}]
)
```

支持的文档类型：PDF, DOCX, DOC, TXT, JSON, MD, XML

### 上传 Skill（base64）

Skill 文件以 base64 编码传入，`type` 设为 `"skill"`：

```python
import base64

skill_markdown = """---
name: 客服退货处理流程
description: 指导客服按标准流程处理用户退货请求
---

## Procedure

1. 确认用户身份和订单号
2. 核实退货原因是否符合政策
3. 引导用户选择退货方式
4. 生成退货单号并告知用户
"""

encoded = base64.b64encode(skill_markdown.encode("utf-8")).decode("utf-8")

data = {
    "knowledgebase_id": "kb_xxx",
    "file": [
        {
            "type": "skill",
            "name": "customer-return-sop.md",
            "content": f"data:text/markdown;base64,{encoded}"
        }
    ]
}

res = requests.post(
    f"{BASE_URL}/add/knowledgebase-file",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
print(res.json())
```

也可以上传远程 Skill URL：

```python
data = {
    "knowledgebase_id": "kb_xxx",
    "file": [{"type": "skill", "content": "https://cdn.example.com/SKILL.md"}]
}
```

更多 Skill 记忆用法参见 [features-skill.md](features-skill.md)。

## 查询知识库文件

### 按知识库 ID 列出文件

```python
data = {
    "knowledgebase_id": "kb_xxx",
    "type": "skill",   # 可选："document" / "skill"
    "page": 1,
    "page_size": 20
}

res = requests.post(
    f"{BASE_URL}/get/knowledgebase-file",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
print(res.json())
```

### 按文件 ID 查询

```python
data = {"file_ids": ["file_xxx"]}

res = requests.post(
    f"{BASE_URL}/get/knowledgebase-file",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
print(res.json())
```

SDK：

```python
res = client.get_knowledgebase_file(file_ids=["file_xxx"])
```

用途：上传后查处理进度、确认文件是否就绪。

## 删除知识库文件

```python
data = {"file_ids": ["file_xxx"]}

res = requests.post(
    f"{BASE_URL}/delete/knowledgebase-file",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
print(res.json())
```

SDK：

```python
res = client.delete_knowledgebase_file(file_ids=["file_xxx"])
```

## 删除整个知识库

```python
data = {"knowledgebase_id": "kb_xxx"}

res = requests.post(
    f"{BASE_URL}/delete/knowledgebase",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
print(res.json())
```

SDK：

```python
res = client.delete_knowledgebase(knowledgebase_id="kb_xxx")
```

> 删除知识库会同时删除其下所有文件和相关记忆，不可恢复。

## 联合检索

在 searchMemory 中指定 `knowledgebase_ids`：

```python
data = {
    "user_id": "user_001",
    "query": "公司差旅报销标准是什么？",
    "knowledgebase_ids": ["kb_xxx"]
}

res = requests.post(
    f"{BASE_URL}/search/memory",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
```

MemOS 会同时检索：
- 用户个人记忆（如"用户用 Intel MacBook Pro"）
- 知识库记忆（如"安装步骤"）

两者结合生成更精准的回答。

## 在 Chat API 中使用

```python
data = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "query": "内网代理打不开了，该装哪个版本？",
    "knowledgebase_ids": ["kb_xxx"]
}

res = requests.post(
    f"{BASE_URL}/chat",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
```

## 通过反馈更新知识库

使用 `addFeedback` + `allow_knowledgebase_ids` 可以通过自然语言更新知识库中的记忆：

```python
data = {
    "user_id": "user_001",
    "conversation_id": "feedback",
    "feedback_content": "报销标准已改为新版，办公软件限额600元",
    "allow_knowledgebase_ids": ["kb_xxx"]
}
```

## 知识库 API 端点汇总

| 端点 | 功能 | SDK 方法 |
|------|------|---------|
| `POST /create/knowledgebase` | 创建知识库 | `client.create_knowledgebase(...)` |
| `POST /add/knowledgebase-file` | 上传文档或 Skill | `client.add_knowledgebase_file(...)` |
| `POST /get/knowledgebase-file` | 查询文件列表/状态 | `client.get_knowledgebase_file(...)` |
| `POST /delete/knowledgebase-file` | 删除文件 | `client.delete_knowledgebase_file(...)` |
| `POST /delete/knowledgebase` | 删除整个知识库 | `client.delete_knowledgebase(...)` |

## 文档上传限制

- 支持类型：PDF, DOCX, DOC, TXT, JSON, MD, XML
- 单文件大小：≤ 100 MB，≤ 500 页
- 单次上传：≤ 20 个文件
- Skill 文件：.md ≤ 100KB 或 .zip ≤ 20MB（解压后 ≤ 200 文件）
