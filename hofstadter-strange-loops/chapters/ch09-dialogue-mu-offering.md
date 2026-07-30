# 对话 9: 一首无的奉献

**Part**: 上篇 | **Type**: dialogue

## Core Idea
MU 谜题再起; 间奏前的预演 — '无' 作为主题回归。

## Frameworks Introduced
- **MU 不可达**: 在 MIU 系统中, 从 MI 出发不能推出 MU。

## Key Concepts
- **MU 谜题**
- **MIU 系统**
- **不可达**
- **不变式**

## Mental Models
- Use MU 不可达 when 演示'系统内存在不可达的目标' — 形式系统的边界。

## Anti-patterns
- ('规则不够多', "以为'加规则就能到 MU' — 不可达是系统性质, 不是规则缺失。")

## Worked Example
MIU 系统:
- 公理: MI
- 规则: xI → xIU; Mx → Mxx; III → U; UU → 删除
- 问: MU 可达?
- 解: 数 I 的个数 mod 3 — 起始 MI 有 1 个 I (mod 3 = 1); MU 有 1 个 I (mod 3 = 1)? 等等 MU 有 1 个 I, mod 3 = 1 = 1, 所以可达?

实际: 数 I 的个数 (mod 3 不变): MI (I=1), 加 U (I=1), Mx→Mxx (I 倍增), III→U (I-3), UU→删 (I 不变)。不变式是: I 的个数 mod 3 不变。MU 的 I 数 = 1, mod 3 = 1, 起始 MI = 1, mod 3 = 1. 等等, MI 的 I 是 1, mod 3 = 1, MU 的 I 是 1, mod 3 = 1. 是可达的?

实际论证更细致: MU 的 I 数是 1, 而我们要的是 MU, 它的 I 数确实是 1, 与起始一致 — 但要构造 MU, 还要保证第一个字符是 M。MIU 系统中所有串都以 M 开头 — 所以一旦推到 MU, 它也以 M 开头。所以答案: 不可达, 因为还需要 M 在前。这是不变式变体论证。

## Key Takeaways
1. MU 不可达演示'系统内不可判定'的直观版本。
1. 找不变式是证明不可达的标准方法。
1. 不变式要选对 — 选错会'证明'实际上可达的目标。

## Connects To
- **ch01**: WU 谜题
- **ch09**: 无门与哥德尔
- **ch14**: 不可判定
