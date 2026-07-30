---
name: windows-python-utf8
description: >-
  Use when Python on Windows fails to parse stdin JSON containing non-ASCII
  (errors like json.decoder.JSONDecodeError, Expecting comma delimiter,
  UnicodeDecodeError gbk codec can't decode), or when Claude Code hooks
  (hookify or custom) error on Read responses / UserPromptSubmit prompts
  containing Chinese or other Unicode text. Also covers mojibake and
  UnicodeEncodeError gbk in Python stdout on Windows.
---

# Windows Python UTF-8 编码坑

## 核心原理

Windows 上 Python 3 的 `stdin` / `stdout` / `stderr` / `open()` 默认用**系统区域编码**（中文系统 = `gbk` / `cp936`），**不是 UTF-8**。任何经 stdin 读入或经 stdout 输出的非 ASCII 字节（UTF-8 编码的中文等）都会被 gbk 错位解码，导致：

- `json.load(sys.stdin)` → `json.decoder.JSONDecodeError`（典型：`Expecting ',' delimiter`）
- `print(中文)` 经管道/重定向 → `UnicodeEncodeError: 'gbk' codec can't encode character`
- 字符串含中文 → 乱码（mojibake）

**根治开关**：`PYTHONUTF8=1`（Python 3.7+ 的 UTF-8 Mode），让 stdin/stdout/open 全部默认 UTF-8。

## When to Use

**症状（命中任一即用）：**
- `JSONDecodeError: Expecting ',' delimiter` / `Expecting property name` —— 且 payload 含中文/非 ASCII
- `UnicodeDecodeError: 'gbk' codec can't decode byte ...`
- `UnicodeEncodeError: 'gbk' codec can't encode character ...`
- Claude Code hook 报 `Hookify error: Expecting ',' delimiter`（PostToolUse 处理 Read 响应时）
- Python 输出中文是乱码

**场景：** Claude Code hooks（hookify / 自定义）读 stdin JSON；Python 脚本处理含中文的 stdin/文件/管道；任何 Windows + Python + 非 ASCII 数据流。

**When NOT to use：** Linux/macOS（默认 UTF-8，无此问题）；JSON 本身格式错（非编码问题）——先用下方诊断步骤确认。

## 诊断（30 秒确认根因）

```bash
python -c "import sys,locale; print('stdin:', sys.stdin.encoding, '| preferred:', locale.getpreferredencoding())"
```
- 输出 `gbk` / `cp936` → 命中本坑。
- 验证修复有效：
```bash
PYTHONUTF8=1 python -c "import sys; print(sys.stdin.encoding)"
```
应变 `utf-8`。

**为什么 PostToolUse:Read 特别容易触发**：PreToolUse 的 stdin payload 只含 `tool_input`（file_path，通常纯 ASCII 路径）；PostToolUse 的 payload 含 `tool_response`（**整个文件正文**）——中文一多，gbk 解码立刻翻车。所以纯英文文件不报错、含中文文件必报。UserPromptSubmit 含中文 prompt 同理。

## 三层修复（按范围选，首选全局）

| 层级 | 方式 | 适用 | 持久化 |
|------|------|------|--------|
| **全局（Claude Code）** | `settings.json` → `env` 加 `"PYTHONUTF8": "1"` | 所有 CC 启动的 Python 子进程（hook + Bash 里的 python） | 配置文件，**重启 CC** 生效 |
| **系统（Windows 用户）** | `setx PYTHONUTF8 1` | 该用户所有新进程 | 注册表，新 shell 生效 |
| **脚本级** | 代码里显式处理 | 单个脚本、不能改环境时 | 代码内 |

### 全局修复（推荐，CC 场景）

```json
// ~/.claude/settings.json
{
  "env": {
    "PYTHONUTF8": "1"
  }
}
```
改完**重启 Claude Code**——env 只对新进程生效，已运行进程不会重读。

### 系统级修复

```bash
setx PYTHONUTF8 1          # 写注册表（用户级），重开终端生效
```

### 脚本级修复（不能改环境时）

读 stdin JSON（最常见，hook 场景）：
```python
import json, sys
# ❌ Windows 上 sys.stdin 默认 gbk，中文会解坏
# data = json.load(sys.stdin)
# ✅ 读原始字节再 UTF-8 解码，绕过 locale
data = json.loads(sys.stdin.buffer.read().decode('utf-8'))
```

写 stdout 中文：
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')   # Python 3.7+
print("中文输出")
```

读文件：
```python
with open(path, 'r', encoding='utf-8') as f:   # 显式指定
    content = f.read()
```

## Quick Reference

| 想做的事 | 代码 |
|---------|------|
| 检查 stdin 编码 | `python -c "import sys;print(sys.stdin.encoding)"` |
| 读 stdin JSON 不踩坑 | `json.loads(sys.stdin.buffer.read().decode('utf-8'))` |
| stdout 输出中文 | `sys.stdout.reconfigure(encoding='utf-8')` |
| 一劳永逸（CC 场景） | `settings.json` env `"PYTHONUTF8":"1"` |
| 一劳永逸（系统） | `setx PYTHONUTF8 1` |

## Common Mistakes

- ❌ **改插件源码**（如 `.claude/plugins/cache/` 下的 hookify）——下次插件更新被覆盖；用环境层修复。
- ❌ **设了 `PYTHONUTF8=1` 但没重启 Claude Code**——当前会话 hook 仍跑旧环境，误以为没修好。
- ❌ **只写进 `.bashrc`**——只对 bash 子 shell 生效；Windows 原生进程（CC 直接启动的 python hook）不读 `.bashrc`。CC 场景放 `settings.json` env，系统场景用 `setx`。
- ❌ **用 `PYTHONIOENCODING=utf-8` 当等价替代**——它只改 stdin/stdout/stderr，而 `PYTHONUTF8=1` 还顺带让 `open()` 默认 UTF-8，覆盖更全。优先 `PYTHONUTF8=1`。
- ❌ **把 Python 装成英文 locale 来绕过**——治标不治本，且影响其他工具；用 `PYTHONUTF8=1`。

## Real-World Impact

真实案例（Claude Code + hookify，Windows 11 中文系统）：
- **现象**：每次 `Read` 含中文文件，PostToolUse hook 报 `Hookify error: Expecting ',' delimiter: line 1 column 2140`。
- **根因**：`hooks/posttooluse.py` 的 `json.load(sys.stdin)`，stdin 默认 `gbk`，把 Read 返回的 UTF-8 中文文件解坏。
- **修复**：`settings.json` env 加 `PYTHONUTF8=1` + 重启 CC。hook 不再报错，Bash 工具里 python 处理中文也无需手动 reconfigure。
