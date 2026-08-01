---
name: safe-state-restore
description: Use when 写会「修改文件→执行→恢复」的脚本（手动变异测试、临时替换配置、批量改写），或脚本在 Windows 控制台打印 ¥/✓ 等非 ASCII 字符时抛 UnicodeEncodeError / 报 GBK 编码错，或修改文件后 git 出现莫名 CRLF/行尾污染。也适用于任何「改状态后必须还原现场」的自动化。
---

# Safe State Restore

## Overview

改文件状态的脚本，**恢复必须是不可失败的**：任何异常（打印崩溃、pytest 崩溃、被 Ctrl+C 中断）都不能阻止还原现场。同时 Windows 有两个暗坑：控制台 GBK 打印崩溃、text 模式写文件污染行尾。

## 核心原则

1. **恢复进 `finally`，且恢复用字节级读写**（`read_bytes`/`write_bytes`）——text 模式会把 LF 写成 CRLF，看似恢复了，`git diff` 也可能为空，但文件已被污染。
2. **打印不能成为崩溃点**：Windows 中文控制台 stdout 是 GBK（cp936），`¥`（U+00A5）等字符直接 `print` 抛 `UnicodeEncodeError`，会中断「打印→恢复」序列。
3. **恢复正确性用机器验证**：`git diff --exit-code` 必须为空。注意其盲区：行尾差异可能被 git 归一化掩盖——加一道 `git status` 确认无 `M` 后缀。

## Core Pattern

```python
# ❌ 坏的：恢复是普通语句，任何一行 print 崩溃/异常都会跳过恢复
SOURCE.write_text(mutated)      # text 模式: LF→CRLF, 污染行尾
run_pytest()
print(f"KILLED {name}")         # GBK 打不出 ¥ → UnicodeEncodeError → 恢复没执行
SOURCE.write_text(original)     # 永远不会走到

# ✅ 好的：finally + 字节级读写 + 安全打印
def safe_print(text: str) -> None:
    """Windows GBK 控制台打不出的字符降级为替换符，打印永不崩溃。"""
    try:
        print(text)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "utf-8"
        print(text.encode(enc, errors="replace").decode(enc))

original = SOURCE.read_bytes()          # 字节级：不改行尾
for name, find, replace in MUTANTS:
    SOURCE.write_bytes(original.replace(find, replace))
    try:
        killed, output = run_pytest()
        safe_print(f"{'KILLED' if killed else 'SURVIVED'} {name}")
    finally:
        SOURCE.write_bytes(original)     # 无论发生什么都还原
# 循环外再断言一次 + 检查 git 状态，机器验证还原
assert SOURCE.read_bytes() == original
```

## Quick Reference

| 风险 | 症状 | 解法 |
|------|------|------|
| 控制台打印崩溃 | `UnicodeEncodeError: 'gbk' codec can't encode` | `safe_print`（编码降级）或脚本开头 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` |
| 恢复被跳过 | 异常后工作区残留变异 | 恢复进 `finally`；脚本顶层 `except` 也强制恢复 |
| 行尾污染 | `git diff` 空但 `git status` 报 `M` | 字节级 `read_bytes`/`write_bytes`，不用 text 模式 |
| diff 盲区 | 假「已还原」 | `git diff --exit-code` + `git status` 双查；`git checkout -- file` 兜底重来 |
| pyc 缓存 | 恢复后重跑测试导入旧字节码（如 `add(2,3)==2`，变异假残留） | 跑测试用 `python -B -m pytest`（禁字节码缓存）或每次跑前 `shutil.rmtree(__pycache__)` |

## Common Mistakes

| 借口 | 现实 |
|------|------|
| 「恢复写在 print 后面没关系」 | 打印崩溃 = 恢复没执行 = 污染工作区，后续一切测试跑在变异代码上 |
| 「用 text 模式写回原样就行」 | 换行符已被改写；`git diff` 可能为空但文件字节已变 |
| 「git diff 为空就还原了」 | CRLF 差异可能被 git 归一化吞掉，加 `git status` 确认 |
| 「文件还原了测试就准」 | pyc 秒级 mtime 缓存会让恢复后第一次运行仍加载变异字节码——`-B` 或清 `__pycache__` |

## 适用范围

- 手动变异测试脚本（mutate.py 形态：注入 bug → 跑测试 → 记录 → 还原）
- 临时配置替换/批量改写后需要还原的自动化
- Windows 下任何打印中文/特殊符号到控制台的脚本

**不适用**：一次性的、不修改文件状态的脚本无需此模式；不要为「永远不会打印」的脚本加 safe_print。
