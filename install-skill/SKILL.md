---
name: install-skill
description: |
  Use when user wants to install a skill or plugin from a GitHub URL or resource link.
  Triggers: "安装 skill", "安装插件", "install skill", "install plugin", or user provides a GitHub URL.
  Auto-detects install method: plugin > npx skills add > follow repo's own install instructions.
argument-hint: "<GitHub URL 或 owner/repo>"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
  - Grep
  - Glob
  - WebSearch
  - WebFetch
---

# Install Skill / Plugin

通过资源链接为 Claude Code 安装 skill 或 plugin。自动判断安装方式，按优先级依次尝试。

## 安装优先级

```
1. Plugin 方式（claude plugin install）—— 如果仓库是 plugin marketplace
2. npx skills add（符号链接）—— 如果仓库包含 SKILL.md
3. 读取仓库文档中的安装说明 —— 按文档推荐方式安装（兜底）
```

## 工作流程

### Step 1: 解析输入

从用户输入中提取资源标识符，支持以下格式：

| 输入格式 | 示例 | 解析结果 |
|---------|------|---------|
| GitHub 完整 URL | `https://github.com/owner/repo` | `owner/repo` |
| GitHub 子目录 URL | `https://github.com/owner/repo/tree/main/skills/foo` | `owner/repo` + 子路径 `skills/foo` |
| owner/repo 简写 | `owner/repo` | `owner/repo` |
| 带 skill 指定 | `owner/repo@skill-name` | `owner/repo` + skill 名 |

### Step 2: 判断仓库类型

**必须先检查仓库结构再决定安装方式。**

#### 2.1 检查是否为 Plugin Marketplace

检查仓库根目录是否包含以下任一文件：
- `manifest.json`
- `plugins/*/manifest.json`
- `plugin.json`

如果存在，说明这是一个 **plugin marketplace**。

同时检查已有的 marketplace 列表：
```bash
claude plugin marketplace list
```

#### 2.2 检查是否包含 SKILL.md

检查仓库是否包含 `SKILL.md` 文件（根目录或 `skills/` 子目录下）。

#### 2.3 判断逻辑

```
仓库结构分析结果
    │
    ├── 有 manifest.json / plugin 结构？ ──→ Plugin 方式（优先级 1）
    │
    ├── 有 SKILL.md？ ──→ npx skills add（优先级 2）
    │
    └── 都没有？ ──→ 读取仓库 README/文档，按其中的安装说明执行（优先级 3）
```

**检查方法**（按速度优先排列）：

1. 用 `mcp__zread__get_repo_structure` 查看仓库结构
2. 或用 `curl` 请求 GitHub API：
   ```bash
   curl -s "https://api.github.com/repos/{owner}/{repo}/contents/" | grep -E '"name"'
   ```

### Step 3: 执行安装

#### 方式 A：Plugin 安装（最高优先级）

**前提**：仓库是 plugin marketplace。

```bash
# Step A1: 先添加 marketplace（如果还没有）
claude plugin marketplace add https://github.com/{owner}/{repo}

# Step A2: 更新 marketplace 索引
claude plugin marketplace update

# Step A3: 安装 plugin
claude plugin install {plugin-name}
```

**注意**：
- marketplace 名称通常由 CLI 自动从仓库名推断
- plugin 名称需要查看仓库内的 `manifest.json` 获取
- 如果用户只想安装仓库中的某个 skill 而非整个 plugin，跳到方式 B

#### 方式 B：npx skills add（默认符号链接）

**前提**：仓库包含 `SKILL.md`。

```bash
# 安装全部 skills（符号链接）
npx skills add {owner}/{repo} -g -y

# 或只安装指定 skill
npx skills add {owner}/{repo} -g -y -s {skill-name}

# 查看仓库中有哪些可安装的 skills
npx skills add {owner}/{repo} -l
```

**关键**：**不要加 `--copy` 参数**。默认行为是符号链接（symlink），更节省空间且方便更新。

如果 `npx skills` 命令不可用或执行失败，回退到方式 C。

#### 方式 C：读取仓库文档中的安装说明（兜底）

**前提**：方式 A 和方式 B 都不可用或执行失败。

**核心思路**：很多仓库的 README.md 或文档中包含安装说明（如 `claude skill add`、`npx skills add`、自定义脚本等）。
应**优先遵循仓库作者给出的安装方式**，而非自行猜测。

##### C1: 获取仓库 README

用以下任一方式读取仓库的 README.md：

```bash
# 方式 1: curl GitHub Raw URL
curl -sL "https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
# 如果 main 不存在，尝试 master
curl -sL "https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
```

或使用 MCP 工具（优先）：
- `mcp__zread__read_file` — 直接读取 GitHub 文件
- `mcp__open-websearch__fetchGithubReadme` — 获取 README

##### C2: 提取安装说明

在 README 中查找以下关键词区域：

| 关键词 | 含义 |
|--------|------|
| `Install` / `Installation` / `安装` | 安装章节 |
| `Quick Start` / `Getting Started` / `快速开始` | 快速上手 |
| `Usage` / `使用` | 使用说明中可能包含安装命令 |
| `claude skill add` / `npx skills add` | 具体安装命令 |
| `SKILL.md` | 提及 skill 结构 |

##### C3: 执行文档中的安装命令

找到安装说明后，按文档描述执行。常见模式：

```bash
# 模式 1: 文档推荐 npx skills add
npx skills add {owner}/{repo} -g -y

# 模式 2: 文档推荐 claude plugin install
claude plugin install {plugin-name}

# 模式 3: 文档推荐自定义命令（直接执行文档中的命令）
# 例如: claude skill add --url https://github.com/...

# 模式 4: 文档只提供了手动步骤（按步骤执行）
# 例如: mkdir -p ~/.claude/skills/my-skill && cp SKILL.md ~/.claude/skills/my-skill/
```

##### C4: 如果文档中也没有安装说明

如果 README 中找不到任何安装相关内容，告知用户：

> 该仓库没有提供标准的安装说明。可以：
> 1. 手动将 SKILL.md 复制到 `~/.claude/skills/` 目录
> 2. 联系仓库作者确认安装方式
> 3. 如果仓库有 SKILL.md 文件，用 Write 工具直接下载到 `~/.claude/skills/{skill-name}/SKILL.md`

### Step 4: 验证安装

安装完成后，验证 skill 是否可用：

```bash
# 检查 skills 目录
ls -la ~/.claude/skills/{skill-name}/SKILL.md

# 或检查 plugin
claude plugin list
```

如果安装了独立 skill，读取 `SKILL.md` 的前 10 行确认内容完整：
```bash
head -10 ~/.claude/skills/{skill-name}/SKILL.md
```

### Step 5: 同步文档

安装完成后，提醒用户更新 `E:\doc\skill\installed-extensions-reference.md`：
- 在对应分类中添加新 skill
- 更新统计数据
- 在 `E:\doc\skill\plugin.md` 中补充资源链接

---

## 常见场景处理

### 场景 1：用户给出 GitHub 仓库链接

```
用户：https://github.com/vercel-labs/agent-skills
```

→ 检查结构 → 包含 SKILL.md → `npx skills add vercel-labs/agent-skills -g -y`

### 场景 2：用户给出带子目录的链接

```
用户：https://github.com/GBSOSS/skill-from-masters/tree/main/skill-from-masters
```

→ 检查结构 → 包含 SKILL.md → `npx skills add GBSOSS/skill-from-masters -g -y -s skill-from-masters`

### 场景 3：仓库既是 marketplace 又有 skills

```
用户：https://github.com/anthropics/skills
```

→ 检查结构 → 既是 marketplace 又有 skills → 优先以 plugin 安装：
```bash
claude plugin install example-skills@anthropic-agent-skills
```

### 场景 4：npx skills 失败

→ 回退到方式 C：读取仓库 README，找到其中的安装说明并执行

### 场景 5：用户只想安装某个特定 skill

如果仓库包含多个 skills，用 `-l` 先列出再让用户选择：
```bash
npx skills add {owner}/{repo} -l
```

---

## 错误处理

| 错误 | 处理 |
|------|------|
| GitHub 仓库不存在或私有 | 提示用户检查 URL 是否正确，或仓库是否为私有 |
| `claude plugin marketplace add` 失败 | 提示检查网络，尝试用 Git URL 格式 |
| `npx skills` 命令不可用 | 自动回退到方式 C：读取仓库文档中的安装说明 |
| `npx skills add` 失败 | 自动回退到方式 C：读取仓库文档中的安装说明 |
| 目标目录已存在同名 skill | 用 AskUserQuestion 询问：覆盖 / 跳过 / 重命名 |
| 安装后 skill 不可用 | 检查 SKILL.md frontmatter 格式是否正确 |

---

## 注意事项

- **符号链接优先**：`npx skills add` 默认创建符号链接，不要加 `--copy`
- **文档优先于猜测**：兜底时优先读取仓库 README 中的安装说明，按作者推荐的方式安装
- **Windows 兼容**：Windows 上符号链接需要管理员权限，如果失败自动回退到 `--copy`
- **网络问题**：GitHub clone 失败时，建议用户配置代理或重试
- **权限问题**：plugin 安装需要 user scope 权限
