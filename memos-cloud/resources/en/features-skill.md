# Skill Memory

MemOS can automatically generate personalized Skills from conversation history and can also retrieve uploaded custom Skill files from knowledge bases.

## What Is A Skill

A Skill is a reusable task method that tells an Agent how to handle a category of work, such as:

- Planning travel.
- Handling returns.
- Writing weekly reports.

## Two Sources

### 1. Automatically Generated From Conversation History

When conversation history is written through `addMessage`, MemOS can:

1. Detect task boundaries and split task text.
2. Cluster similar tasks.
3. Extract structured Skills.
4. Convert them into reusable Skill files.

No manual Skill file is required for this route.

### 2. Uploaded Custom Skill Through Knowledge Base

Upload a `.md` or `.zip` Skill package to a knowledge base:

```python
import base64
import requests

skill_markdown = """---
name: customer-return-handling
description: Guide support agents through return requests.
---

## Procedure
1. Verify customer identity and order ID.
2. Check whether the return reason matches policy.
3. Guide the customer to select a return method.
4. Generate a return ID.
5. Track logistics and notify refund status.

## Experience
- No-reason returns are allowed within 7 days after delivery.
- High-value products require manager approval.
"""

encoded = base64.b64encode(skill_markdown.encode("utf-8")).decode("utf-8")

payload = {
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
    json=payload,
)
```

## Search Skills

Enable `include_skill` in `searchMemory`:

```python
payload = {
    "user_id": "user_001",
    "query": "The user wants to return headphones bought three days ago.",
    "conversation_id": "session_001",
    "knowledgebase_ids": ["kb_xxx"],
    "include_skill": True
}

res = requests.post(
    f"{BASE_URL}/search/memory",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
```

## Response Shape

```json
{
  "skill_detail_list": [
    {
      "skill_value": {"name": "customer-return-handling", "description": "...", "procedure": "..."},
      "skill_url": "https://..."
    }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `skill_value` | Structured Skill content that can be injected into a prompt. |
| `skill_url` | Download URL for the Skill file. ZIP packages may include scripts or references. |

## Use Retrieved Skills

### Agent Supports Skill Files

```python
skill_url = result["skill_detail_list"][0]["skill_url"]
system_prompt = f"Use this Skill file for the task:\n{skill_url}"
```

### Agent Does Not Support Skill Files

```python
skill = str(result["skill_detail_list"][0]["skill_value"])
system_prompt = f"Use the following Skill guidance:\n{skill}"
```

## Skill File Constraints

### Single Markdown File

- Size: up to 100 KB.
- Frontmatter must include `name` and `description`.

```markdown
---
name: skill-name
description: When to use this skill.
---

## Procedure
1. Step one.
2. Step two.

## Experience
- Lesson one.
- Lesson two.

## User Preferences
- Preference one.

## Examples
### Example 1
Input and output example.
```

### ZIP Package

| Constraint | Requirement |
| --- | --- |
| Format | Standard ZIP. |
| Archive size | Up to 20 MB. |
| Extracted file count | Up to 200 files. |
| Single file size | Up to 10 MB. |
| `SKILL.md` | Up to 100 KB and located at the top level. |

```text
skill-package.zip
|-- SKILL.md
|-- references/
|   `-- policy.md
|-- scripts/
|   `-- check_order.py
`-- assets/
    `-- flowchart.png
```
