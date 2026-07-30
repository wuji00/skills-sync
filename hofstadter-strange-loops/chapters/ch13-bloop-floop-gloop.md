# 第十三章: BlooP 和 FlooP 和 GlooP

**Part**: 下篇 | **Type**: chapter

## Core Idea
三层可计算性: 可证终止 / 可能不终止 / 不可判定。

## Frameworks Introduced
- **BlooP (Bounded Loop)**: 只有 LOOP 循环的程序语言; 表达原始递归函数; 可证终止。
- **FlooP (Free Loop)**: 加 WHILE 循环; 可能不终止; 表达所有图灵可计算函数。
- **GlooP (Gödelian Loop)**: 含不可判定问题 (停机); 与图灵机等价。

## Key Concepts
- **BlooP**
- **FlooP**
- **GlooP**
- **原始递归**
- **图灵可计算**
- **停机问题**
- **图灵机**

## Mental Models
- Use BlooP / FlooP / GlooP when 演示可计算性的三个层级。
- Use 停机问题 when 演示'不可判定'的具体形式。

## Anti-patterns
- ('FlooP 当万能', '以为加规则就能解决一切 — 实际有不可判定问题 (停机)。')
- ("停机问题当'算法不够'", "以为'再聪明的算法能判定停机' — 实际'不可判定'是数学事实。")

## Worked Example
BlooP 程序 (例: 计算 n!):
```
DEFINE FACTORIAL N =
LOOP X TIMES N
  OUTPUT X * CURRENT_VALUE
END LOOP
```
可证终止: 每个循环边界已知。

FlooP 程序 (可能不终止):
```
DEFINE COLLATZ N =
WHILE N ≠ 1
  IF EVEN(N) THEN N = N/2 ELSE N = 3N+1
END WHILE
```
可能不终止: 哥德巴赫猜想 Collatz 形式 — 未证明。

GlooP / 停机问题: 给定程序 P 和输入 I, 问'P(I) 终止吗?' — 不可判定 (图灵 1936)。

证明: 假设有 HALT(P, I) 函数。构造对角线: HALT(P, P) = not HALT(P, P) — 矛盾。

## Key Takeaways
1. 可计算性有明确的三层 (BlooP / FlooP / GlooP), 不只是复杂度。
1. 停机问题不可判定 — 不是算法不足, 是数学事实。
1. 任何'形式系统内的判定问题'都有'不可判定'的可能。

## Connects To
- **ch05**: 递归
- **ch14**: 不可判定性
- **ch17**: 丘奇-图灵
