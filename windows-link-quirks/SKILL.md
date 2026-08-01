---
name: windows-link-quirks
description: Use when about to edit a cross-tool shared config file (AGENTS.md / CLAUDE.md hardlinked across Claude / Kimi / zcode / agents), OR `npx skills add` fails on Windows with "symlinks FAIL — would need Developer Mode/admin", OR a skill diagnose script reports "share the same install via symlink". Covers hardlink groups broken by Edit/Write, and symlink-vs-junction install quirks.
metadata:
  author: wuji00
---

# Windows 链接文件在 AI 工具下的坑

两类高发场景，根因同源：**Windows 链接语义 + AI 工具/安装器按"普通文件"重写**。

## 路由

| 症状 | 走 |
|---|---|
| 要改的文件是跨工具共享配置（多块"门牌"挂同一份），改完发现别的工具没同步 / inode 变了 | [A1 hardlink 断链](#a1-编辑硬链接文件被-editwrite-断链) |
| `npx skills add` / `ln -s` 失败，或诊断报 "share the same install via symlink"、`[ -L ]` 查不出 junction | [A2 symlink / junction 安装](#a2-npx-skills-add-的-symlink--junction) |

关键词：`Edit`/`Write` 断链、inode 变、hardlink、`mklink /J`、junction、`[ -L ]` 查不出、`os.path.realpath`、`symlinks FAIL`、Developer Mode、`--copy`、share same install via symlink、`UV_HANDLE_CLOSING`。

---

## A1: 编辑硬链接文件被 Edit/Write 断链

### 现象

多份硬链接（共享 inode，改一份等于改全部）。用 `Edit`/`Write` 工具改其中一份后：
- 被编辑的那份 inode 变了（脱链），内容可能还是旧的
- 其他伙伴仍指向旧 inode，**完全没同步**

典型：`.claude/CLAUDE.md` ↔ `.zcode/AGENTS.md` ↔ `.agents/mem/AGENTS.md` ↔ `.kimi/AGENTS.md` 四份硬链接。

### 根因

`Edit`/`Write` 底层是"写临时文件 + 原子替换"（保证写入失败不损坏原文件）。替换 = 新建 inode + 路径名重新指向新 inode + 旧 inode 链接数 -1。普通文件无感；**硬链接的路径名被摘走挂到新 inode，原 inode（和其他伙伴）就脱钩了**。

类比：硬链接是"同一房间挂 4 块门牌"。Edit 不是"进房间改家具"，是"造新房、摘一块门牌挂上去"——剩下门牌还挂旧房间。

### 规则

**改硬链接组文件，禁用 `Edit`/`Write`，必须用脚本原位读写（只改字节不重建文件）。**

#### 改前先验链接数

```bash
stat -c '%h links inode=%i %n' path   # %h>1 即硬链接；改后 inode 必须不变
```

#### Python 原位改（推荐，引号/转义最干净）

```python
import io
path = r"C:\Users\<you>\.claude\CLAUDE.md"
with io.open(path, "r", encoding="utf-8") as f: c = f.read()
c = c.replace("旧字符串", "新字符串")          # 内存里改
with io.open(path, "w", encoding="utf-8") as f: f.write(c)   # 原位覆写，inode 不变
```

> 关键：`open(path,"w")` 覆写已有文件，**不要**删了再建 / 写临时文件再 rename。

#### 多段替换带断言（防文件被并发改过，字符串漂移）

```python
for old, new in reps:
    n = c.count(old)
    assert n == 1, f"expected 1 match, got {n}: {old[:50]}"
    c = c.replace(old, new)
```

#### PowerShell 原位改

```powershell
$p = 'C:\Users\<you>\.claude\CLAUDE.md'
$c = [System.IO.File]::ReadAllText($p)
$c = $c.Replace('旧','新')
[System.IO.File]::WriteAllText($p, $c)
```

> ⚠ PowerShell here-string 在 Git Bash 传参会因反引号/引号转义混乱匹配失败，复杂替换优先 Python。

### 已断链怎么修

```bash
cd "C:\Users\<you>"
stat -c 'inode=%i %n' .zcode/AGENTS.md .agents/mem/AGENTS.md .claude/CLAUDE.md .kimi/AGENTS.md   # 1. 看哪份脱链
# 2. 在组内（仍链接的）任一份上用 Python 原位改成最新内容
rm .zcode/AGENTS.md                                                                              # 3. 删脱链那份
powershell -NoProfile -Command "New-Item -ItemType HardLink -Path 'C:\Users\<you>\.zcode\AGENTS.md' -Target 'C:\Users\<you>\.agents\mem\AGENTS.md'"   # 4. 重建硬链
stat -c 'inode=%i %n' .zcode/AGENTS.md .agents/mem/AGENTS.md .claude/CLAUDE.md .kimi/AGENTS.md   # 5. 验 inode 全同
md5sum  .zcode/AGENTS.md .agents/mem/AGENTS.md .claude/CLAUDE.md .kimi/AGENTS.md
```

> Git Bash 建硬链用 `powershell New-Item -ItemType HardLink`，**不要** `cmd //c mklink /H`（反斜杠转义失败）。

---

## A2: `npx skills add` 的 symlink / junction

### 现象

- `ln -s` / vercel `npx skills add` 默认 symlink 模式：`✗ symlinks FAIL — would need Developer Mode/admin`
- `install_ima_skill.sh` 之类脚本到建链那步挂

### 根因（symlink vs junction）

| 类型 | 命令 | 权限 | git-bash `[ -L ]` | Python `os.path.realpath` |
|---|---|---|---|---|
| symlink | `mklink` / `ln -s` | **需开发者模式或管理员** | 识别 | 跟随 |
| junction | `mklink /J` | **不需要管理员** | **查不出**（像普通目录） | 跟随（解析到目标） |

`ln -s` 在 Win 走 symlink API，没开发者模式就挂。junction 不需管理员——vercel skills 的 Node 实现用 junction 绕开限制，**即便指定 `--copy` 仍可能用 junction 把多 agent 联到同一正本**。

### 解决：加 `--copy`

```bash
npx -y skills add "<local-skill-path>" -g -y --copy -a claude-code -a codex -a openclaw
#                                              ^^^^^^ 关键：复制不软链
```

### 隐蔽副作用：`--copy` 也可能产 junction（诊断误报）

实测 `--copy` 装到三 agent 后，`~/.claude/skills/ima-skill` 可能是指向 `~/.agents/skills/ima-skill` 的 **junction**（不是独立拷贝）：

```bash
[ -L ~/.claude/skills/ima-skill ] && echo symlink || echo "not a symlink"   # => not a symlink（[ -L ] 查不出 junction，误判）
python -c "import os; print(os.path.realpath(r'C:/Users/<you>/.claude/skills/ima-skill/SKILL.md'))"   # 解析到 .agents\... 暴露真相
```

诊断脚本用 `realpath` 做 canonical 解析，会打印 "share the same install via symlink"——把 junction 也叫 symlink，**功能没问题，三处都能加载**。

### 判"到底几个物理目录"的正确方法

**别信 `[ -L ]` / inode，用 `realpath` 去重**：

```bash
python -c "import os; print(os.path.realpath(p))"   # 每个 agent 的 skill 路径跑一遍，相同=同一物理目录
```

修复类操作（改 upstream）**按物理目录去重执行一次**，别对 junction 副本重复改。

### 预防

- 装机先探 symlink 能力：`ln -s` 临时文件，失败就一律给 `npx skills add` 加 `--copy`
- 多 agent 共享 skill 目录的诊断/修复，统一 `realpath` 判同
- 一劳永逸：设置 → 隐私和安全性 → 开发者选项 → 开发人员模式（之后 `ln -s` 即可用）

相关：lobehub market-cli 的坑见 [[lobehub-market-register]]。
