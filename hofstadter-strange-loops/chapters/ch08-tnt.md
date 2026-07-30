# 第八章: 印符数论 (TNT)

**Part**: 上篇 | **Type**: chapter

## Core Idea
把自然数 + 加乘 + 命题形式化为字符串; 让系统'说话'。

## Frameworks Introduced
- **印符数论 (Typographical Number Theory)**: 用符号串表达自然数 + 加乘 + 算术命题。
- **自编码 (Self-Encoding)**: 把句法操作当作数论对象 — 让系统能'说到自己'。

## Key Concepts
- **印符数论**
- **TNT**
- **自编码**
- **Gödel 编码**
- **符号串**
- **自然数形式化**

## Mental Models
- Use TNT 当通用模板 when 让任何形式系统表达算术。
- Use 自编码 when 任何自指 / 元层需求。

## Anti-patterns
- ('字符串当数字', "以为'SSS0' 等于 '3' — 这是约定, 不是物本身。")
- ('编码冲突', '两不同串编到同一数 — 编码必须 inject。')

## Worked Example
TNT 数字编码:
- 0: '0'
- n+1: 'Sn0'

例: 3 = 'SSS0'

加法定义: 'aSb0Sa0' 表达 a + b = a (此为简记, 实际是 'a + b = a' 的形式化)。

Gödel 编码 (简化):
- 符号 '0' → 2
- 符号 'S' → 3
- 符号 '=' → 5
- 符号 '+' → 7
- 符号 'aSb0Sa0' → 2^0 × 3^5 × 5^7 × 7^1 × 11^3 × ...

每个句 → 唯一自然数。这让 TNT 能'看到'自己的句。

## Key Takeaways
1. TNT 是自指系统的最小可用框架 — 比 WJU 强, 但仍不完备。
1. Gödel 编码是自指的前提 — 没有它, 系统看不到自己。
1. 编码必须 inject (不同串 → 不同数) — 否则系统混淆自己。

## Connects To
- **ch09**: 哥德尔句
- **ch13**: BlooP
- **ch14**: 不可判定性
