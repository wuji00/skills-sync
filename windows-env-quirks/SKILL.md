---
name: windows-env-quirks
description: Use on Windows when (1) non-ASCII (Chinese/CJK/emoji) typed into a bash command comes out as mojibake or Python shows lone surrogates like \udc80/\udc94; (2) Python fails to parse stdin JSON or a file containing non-ASCII — json.decoder.JSONDecodeError "Expecting comma delimiter", UnicodeDecodeError "gbk codec can't decode", UnicodeEncodeError "gbk codec can't encode", or hookify/custom hooks error on Read responses / UserPromptSubmit prompts with Chinese; (3) python3 (but not python) fails with "Python was not found; run without arguments to install from the Microsoft Store". Covers bash command-string non-ASCII corruption, Python cp936/gbk locale encoding, and the Store python3 stub.
metadata:
  author: wuji00
---

# Windows Environment Quirks (Claude Code)

三类 Windows 命令执行层坑，都会静默搞坏 Claude Code 工具链。**根都不在你的业务逻辑里**——在 shell / 解释器 / 编码层。

## 何时用 + 路由

| 症状 | 走 |
|---|---|
| bash 命令串里中文/CJK/emoji 输出乱码；Python 显示 `\udc80`/`\udc94` lone surrogate | [P1 bash 非_ascii 乱码](#p1--bash-命令串非-ascii-乱码) |
| `json.load(sys.stdin)` → `JSONDecodeError: Expecting ',' delimiter`；`UnicodeDecodeError/EncodeError: 'gbk' codec can't ...`；hookify hook 处理含中文 Read 响应报错；Python 输出中文乱码 | [P2 Python gbk 编码](#p2--python-cp936gbk-编码) |
| `python3 --version` 报 "Python was not found; run without arguments to install from the Microsoft Store…"，`python` 正常 | [P3 python3 store stub](#p3--python3-解析到-microsoft-store-stub) |

**不用：** Linux/macOS（默认 UTF-8，无此坑）；源文件本身的编码错（直接改文件编码）。

## 核心原理

中文 Windows 上，命令执行层 + Python locale 默认**不是 UTF-8**：
- bash 命令串里的非 ASCII 字节，在传到 shell 前就被破坏
- Python 3 的 `stdin`/`stdout`/`stderr`/`open()` 默认用系统区域编码（中文系统 = `gbk`/`cp936`）
- `python3` 被商店别名 stub 拦截

**永远用 ASCII 输出（hex codepoint）验证，别肉眼盯中文**——终端显示本身也会乱。

---

## P1 — bash 命令串非 ASCII 乱码

**症状：** `printf '简要回答'` → 乱码；中文 pipe 进 Python 出现 `\udc80`/`\udc94`。手敲 `简` 的转义也不可靠（组合时被转回原始中文）。

**根因：** 命令传输层在非 ASCII 字节到达 shell 前就破坏了。叠加 P2：Python `sys.stdin` 中文 Win 默认 cp936/GBK，UTF-8 字节 pipe 进去也乱。

**修：用整数码点构造文本，让命令 100% ASCII：**

```bash
python -c "import json; s=''.join(chr(c) for c in (0x7b80,0x8981,0x56de,0x7b54)); print(json.dumps({'x':s}, ensure_ascii=True))"
# -> ASCII JSON {"x": "简要回答"}，任何编码都能存活
```

hook payload：用 **Write** 工具写 UTF-8 文件（绕开 shell），再从纯 ASCII hook 命令 `cat` 它。

**回读验真（ASCII hex，别肉眼）：**

```bash
python -c "import json,sys; d=json.load(open(sys.argv[1])); print([hex(ord(c)) for c in d['x']])"
# 期望 ['0x7b80','0x8981','0x56de','0x7b54']
```

pipe 进 Python 时读 `sys.stdin.buffer.read()`（原始字节 → UTF-8），别读 `sys.stdin`。

---

## P2 — Python cp936/gbk 编码

**症状（任一命中）：**
- `JSONDecodeError: Expecting ',' delimiter` / `Expecting property name` —— payload 含中文/非 ASCII
- `UnicodeDecodeError: 'gbk' codec can't decode byte ...`
- `UnicodeEncodeError: 'gbk' codec can't encode character ...`
- Claude Code hook 报 `Hookify error: Expecting ',' delimiter`（PostToolUse 处理 Read 响应时）
- Python print 中文是乱码

**根因：** Windows Python 3 的 `stdin`/`stdout`/`open()` 默认系统区域编码（`gbk`/`cp936`），非 UTF-8。UTF-8 编码的中文字节被 gbk 错位解码。

**为什么 PostToolUse:Read 特别容易触发：** PreToolUse stdin 只含 `tool_input`（file_path，通常纯 ASCII）；PostToolUse 含 `tool_response`（**整个文件正文**）——中文一多 gbk 立刻翻车。所以纯英文文件不报、含中文必报。UserPromptSubmit 含中文 prompt 同理。

### 诊断（30 秒确认根因）

```bash
python -c "import sys,locale; print('stdin:', sys.stdin.encoding, '| preferred:', locale.getpreferredencoding())"
# 输出 gbk/cp936 → 命中。验证修复：
PYTHONUTF8=1 python -c "import sys; print(sys.stdin.encoding)"   # 应变 utf-8
```

### 三层修复（首选全局）

| 层级 | 方式 | 适用 | 持久化 |
|---|---|---|---|
| **全局（Claude Code）** | `settings.json` → `env` 加 `"PYTHONUTF8":"1"` | 所有 CC 启动的 Python 子进程（hook + Bash 里的 python） | 配置文件，**重启 CC** 生效 |
| **系统（Win 用户）** | `setx PYTHONUTF8 1` | 该用户所有新进程 | 注册表，新 shell 生效 |
| **脚本级** | 代码显式处理 | 单脚本、不能改环境 | 代码内 |

**全局（推荐，CC 场景）：**

```json
// ~/.claude/settings.json
{ "env": { "PYTHONUTF8": "1" } }
```

改完**重启 Claude Code**——env 只对新进程生效，已运行进程不重读。

**脚本级（不能改环境时）：**

```python
import json, sys
# ❌ sys.stdin 默认 gbk，中文解坏
# data = json.load(sys.stdin)
# ✅ 读原始字节再 UTF-8 解码
data = json.loads(sys.stdin.buffer.read().decode('utf-8'))

sys.stdout.reconfigure(encoding='utf-8')          # stdout 输出中文（3.7+）
with open(path, 'r', encoding='utf-8') as f: ...  # 读文件显式指定
```

---

## P3 — python3 解析到 Microsoft Store stub

**症状：** `python3 --version` 打印 *"Python was not found; run without arguments to install from the Microsoft Store…"*，`python --version` 正常。

**根因：** Win 上真 Python 只装成 `python.exe`，没有 `python3.exe`。商店的"应用执行别名"往 `%LOCALAPPDATA%\Microsoft\WindowsApps` 丢了个 stub `python3`，任何裸调 `python3` 的工具（如 **hookify** 插件 hook）都撞 stub 失败。`python` 和 `python3` 在同一台机上解析不同。

**诊断：**

```bash
which python3    # stub -> .../Microsoft/WindowsApps/python3 ；真 -> .../python3.exe
which python     # 能用的解释器
```

**修：把能用的 `python.exe` 复制成 `python3.exe`，放在 PATH 上、WindowsApps 之前的目录里（venv 目录最理想：PATH 靠前且含 python311.dll）：**

```bash
cp /e/code/python/env/python.exe /e/code/python/env/python3.exe
hash -r            # 清 bash 命令解析缓存
python3 --version  # -> Python 3.x.x（stub 报错消失）
```

可选加固：关商店别名 —— *Windows 设置 → 应用 → 高级应用设置 → 应用执行别名* → 关掉 python.exe / python3.exe。

**注意：** 重建 venv 会抹掉复制的 `python3.exe`，`python3` 再坏就重复制。有些插件自带探测回退不受影响（如 `security-guidance` 用 `sg-python.sh`：试 `python3`、失败穿 stub、退到 `python`/`py -3`）。

---

## Common Mistakes

| 错误 | 修法 |
|---|---|
| 肉眼盯中文输出"验真" | 终端显示也乱——用 hex codepoint（ASCII）验 |
| 把原始中文塞进 hook 的 `command` 串 | 中文存 UTF-8 文件（Write 工具），用 ASCII 命令 `cat` |
| 设了 `PYTHONUTF8=1` 没重启 CC | 当前会话 hook 仍跑旧环境，误判没修好 |
| 只写进 `.bashrc` | 只对 bash 子 shell 生效；Win 原生进程（CC 直启的 python hook）不读 `.bashrc`。CC 场景放 `settings.json` env，系统场景 `setx` |
| 用 `PYTHONIOENCODING=utf-8` 当等价替代 | 它只改 stdin/stdout/stderr，`PYTHONUTF8=1` 还顺带让 `open()` 默认 UTF-8，覆盖更全。优先 `PYTHONUTF8=1` |
| 改插件源码（`.claude/plugins/cache/` 下的 hookify） | 插件更新被覆盖；用环境层修复 |
| 假设 `python3` == `python` | 解析不同，永远先 `which python3` |
| 改插件 `hooks.json` 把 `python3`→`python` | 更新即丢；改解释器解析而非改配置 |
| 测插件 hook 不设 `CLAUDE_PLUGIN_ROOT` | 插件用它做 `sys.path`（`from core… import`），不设会报误导性的 "No module named 'core'" |

## Quick Reference

| 想做 | 代码 |
|---|---|
| bash 串里塞中文 | 用 `chr(0xXXXX)` 码点构造，`ensure_ascii=True` |
| 验中文未坏 | `[hex(ord(c)) for c in s]`（ASCII 输出） |
| pipe 进 Python 不踩坑 | `sys.stdin.buffer.read()` → `.decode('utf-8')` |
| 查 stdin 编码 | `python -c "import sys;print(sys.stdin.encoding)"` |
| 读 stdin JSON | `json.loads(sys.stdin.buffer.read().decode('utf-8'))` |
| stdout 输出中文 | `sys.stdout.reconfigure(encoding='utf-8')` |
| 一劳永逸（CC） | `settings.json` env `"PYTHONUTF8":"1"` + 重启 |
| 一劳永逸（系统） | `setx PYTHONUTF8 1` |
| python3 Store stub | 复制 `python.exe`→`python3.exe` 到 PATH 靠前目录；`hash -r` |
