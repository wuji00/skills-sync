---
name: requirements-analysis
description: Use when starting a new feature or project and requirements are unclear, vague, ambiguous, or only exist as an idea — before writing code or a spec. Also when business/user/system needs are conflated, acceptance criteria are missing, or a PRD is needed. Triggers include "做个X", "build X", "需求不清楚", PRD, 用户故事, 验收标准, 非功能需求, 业务需求.
metadata:
  author: wuji00
---

# Requirements Analysis 需求分析

## Overview

需求分三层：**业务需求（为什么）→ 用户需求（要什么）→ 系统需求（做什么）**。从上到下逐步细化。跳层——直接从业务目标跳到代码——是需求失控的根因。

本 skill 覆盖三层分解 + PRD 骨架 + Given-When-Then 验收标准 + 非功能需求清单。工程实现 spec 见 `spec-driven-development`（互补，本 skill 在它之前）。

## When to Use

**用：**
- 新功能/项目，需求只有一句话或一个想法
- 业务方给的是目标（"提升转化率"）但没说具体做什么
- 写 PRD / 用户故事 / 验收标准前
- 不确定边界、异常路径、权限矩阵时

**不用：**
- 需求已冻结、有完整 PRD → 直接 `spec-driven-development` / 编码
- 纯 bug 修复（需求明确：复现 → 修）→ `systematic-debugging`
- 一次性脚本、改动 < 几行

## Core Pattern: 三层分解

每个需求三层各写一句，缺层就追问：

| 层 | 回答 | 形式 | 例 |
|----|------|------|----|
| 业务需求 Business | 为什么做 | 目标 + **可量化指标** | "下单转化率 +15%" |
| 用户需求 User | 用户要什么 | 用户故事：作为[角色]，我想要[功能]，以便[价值] | "作为注册用户，我想用手机号找回密码，以便忘记密码时能重新登录" |
| 系统需求 System | 系统做什么 | 功能需求 + 非功能需求 | "输入手机号后 60s 内发 6 位短信验证码" |

**自检**：业务层没指标 → 问商业价值；用户层没"以便[价值]" → 问真实动机；系统层直接写代码 → 退回上层。

## PRD 骨架

主交付物。下列槽位缺一个就回头补：

1. 项目背景与目标（业务需求）
2. 业务范围与边界（**做什么 + 不做什么**）
3. 功能列表与描述
4. 用户故事 / Use Case
5. **验收标准**（每个故事配，见下）
6. **非功能需求**（见下）
7. 数据需求（报表、统计口径）
8. 依赖与约束

## 验收标准（Acceptance Criteria）

用 **Given-When-Then**，禁用模糊词（"快"、"友好"、"稳定"、"高性能"）：

```
Given 用户在登录页且输入了正确手机号 + 密码
When  点击登录
Then  跳转首页，Session 有效期 7 天
```

每个用户故事至少 1 条正常 AC + 1 条异常 AC（错误手机号、密码错、账号锁定……）。

## 非功能需求清单（NFR）

**最易遗漏，往往上线后才暴露。** 每条需求过一遍，不适用就显式写"不适用 + 原因"，不要静默跳过：

- **性能**：响应时间、并发量、吞吐
- **可用性**：SLA（99.9%？）、允许 downtime
- **安全**：认证授权、数据加密、审计日志
- **兼容**：浏览器/OS/分辨率
- **可维护**：日志、监控、文档
- **可扩展**：2 年数据量增长预期
- **合规**：GDPR、等保、行业监管

## 边界与异常（必问）

- 异常场景：网络超时、第三方不可用 → 怎么降级
- 边界值：最大/最小、空值、重复提交
- 权限矩阵：谁能在什么状态下做什么操作

## Common Mistakes

| 错误 | 后果 | 修正 |
|------|------|------|
| 跳过业务层直接写功能 | 做了用户不要的东西 | 先写可量化业务指标 |
| NFR 全省 | 上线崩（慢/不安全/不可用） | 过 NFR 清单，不适用的也写明 |
| AC 用"快/友好/稳定" | 无法验收、测试无依据 | Given-When-Then + 具体数值 |
| 只写正常路径 | 异常无人处理 | 每个故事加异常 AC |
| 只写"做什么"没写"不做什么" | 范围蔓延 | PRD 明确"不做"清单 |
| 静默跳过不适用的 NFR | 评审时无法判断是否考虑过 | 显式标"不适用 + 原因" |
