# Skill 记忆

MemOS 可以自动从对话中生成个性化 Skill，也支持上传自定义 Skill 文件到知识库，在检索时统一返回。

## 什么是 Skill

Skill 是可复用的任务处理方法，告诉 Agent "遇到某类任务时怎么做"。例如：
- 如何规划旅行
- 如何处理退货
- 如何生成周报

## 两种来源

### 1. 自动生成（来自对话历史）

只要通过 `addMessage` 写入用户对话历史，MemOS 自动：
1. 识别任务边界，切分任务文本块
2. 聚类相似任务，提取结构化 Skill
3. 转换为可复用的 Skill 文件

无需手动准备任何文件。

### 2. 上传自定义 Skill（通过知识库）

将 `.md` 或 `.zip` 文件上传到知识库：

```python
import requests, json, base64

skill_markdown = """---
name: 客户退货处理
description: 指导客服处理退货请求
---

## Procedure
1. 核实用户身份和订单号
2. 确认退货原因符合政策
3. 引导选择退货方式
4. 生成退货单号
5. 跟踪物流并通知退款

## Experience
- 收货7天内无理由退货
- 高价值商品需主管审批
"""

encoded = base64.b64encode(skill_markdown.encode("utf-8")).decode("utf-8")

data = {
    "knowledgebase_id": "kb_xxx",
    "file": [
        {
            "type": "skill",
            "name": "return-sop.md",
            "content": f"data:text/markdown;base64,{encoded}"
        }
    ]
}

res = requests.post(
    f"{BASE_URL}/add/knowledgebase-file",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
```

## 检索 Skill

在 searchMemory 中启用 `include_skill`：

```python
data = {
    "user_id": "user_001",
    "query": "用户想退三天前买的耳机",
    "conversation_id": "session_001",
    "knowledgebase_ids": ["kb_xxx"],
    "include_skill": True
}

res = requests.post(
    f"{BASE_URL}/search/memory",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
```

## 返回结构

```json
{
  "skill_detail_list": [
    {
      "skill_value": {"name": "客户退货处理", "description": "...", "procedure": "..."},
      "skill_url": "https://..."
    }
  ]
}
```

| 字段 | 说明 |
|------|------|
| `skill_value` | 结构化 Skill 内容，可转为字符串注入 prompt |
| `skill_url` | Skill 文件下载链接（ZIP 包含脚本/参考资料） |

## 使用 Skill

### Agent 支持 Skill 文件

```python
skill_url = result["skill_detail_list"][0]["skill_url"]
system_prompt = f"使用以下 Skill 文件处理任务：\n{skill_url}"
```

### Agent 不支持文件

```python
skill = str(result["skill_detail_list"][0]["skill_value"])
system_prompt = f"参考以下 Skill 处理任务：\n{skill}"
```

## Skill 文件规范

### 单文件 (.md)

- 大小 ≤ 100KB
- 必须包含 `name` 和 `description`

```markdown
---
name: (Skill 名称)
description: (一句话说明用途和场景)
---

## Procedure
1. 步骤一
2. 步骤二

## Experience
- 经验一
- 经验二

## User Preferences
- 偏好一

## Examples
### Example 1
(完整输入/输出示例)
```

### ZIP 包

| 约束 | 要求 |
|------|------|
| 格式 | 标准 ZIP |
| 压缩包大小 | ≤ 20MB |
| 解压后文件数 | ≤ 200 |
| 单文件大小 | ≤ 10MB |
| SKILL.md | ≤ 100KB，必须在第一层级 |

```
skill-package.zip
├── SKILL.md
├── references/
│   └── policy.md
├── scripts/
│   └── check_order.py
└── assets/
    └── flowchart.png
```
