# MemOS Cloud Skill

MemOS Cloud long-term memory skill for AI applications.

为 AI 应用接入 MemOS Cloud 长期记忆的 Skill。

## Install

```bash
npx skills add https://github.com/MemTensor/MemOS-Cloud-Skill --skill memos-cloud -g -y
```

## Usage

Copy the following prompt into your AI Agent (Codex, Cursor, Claude Code, Trae, OpenClaw, etc.):

将以下 prompt 复制到你的 AI Agent（Codex、Cursor、Claude Code、Trae、OpenClaw 等）聊天框中：

```text
帮我为本项目接入 MemOS Cloud，为我的 Agent 产品添加长期记忆能力。

请按以下步骤操作：

1. 安装 memos-cloud Skill（如已安装则跳过）：
   npx skills add https://github.com/MemTensor/MemOS-Cloud-Skill --skill memos-cloud -g -y
   根据当前 Agent 环境自动填充 --agent 参数。

2. 读取该 Skill 安装路径下的 SKILL.md，严格按照其中的指令顺序执行。

3. 结合本项目的实际技术栈和架构，生成完整的 MemOS Cloud 集成代码。
```

## Get API Key

Sign up at [MemOS Dashboard](https://memos-dashboard.openmem.net/quickstart) and get your API Key (format: `mpg-...`).

前往 [MemOS Dashboard](https://memos-dashboard.openmem.net/cn/quickstart) 注册并获取 API Key（格式：`mpg-...`）。
