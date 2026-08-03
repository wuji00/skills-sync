---
name: building-12-factor-agents
description: Use when 设计、搭建、评审或调试 LLM agent（智能体）项目——涉及 tool calling、人工审批/HITL、暂停/恢复、上下文工程、agent 状态管理、多渠道触发（Slack/cron/webhook）；或 agent 上下文爆炸、错误死循环、状态丢失、行为失控时定位架构根因。基于 12-Factor Agents 方法论。
metadata:
  author: wuji00
---

# Building 12-Factor Agents

## Overview

核心心智模型：**agent 是一个 stateless reducer**。

```
thread(事件列表) --+--> determine_next_step(thread) --> LLM 输出结构化 intent
                   |                                       |
                   +<------ 确定性代码执行 intent，append 结果事件 <--+
```

LLM 只负责"决定下一步"并输出 JSON（tool call = structured output）；代码控制"怎么执行"。状态 = 可序列化的事件列表，不是散落的字段。

## When to Use

- 设计新 agent：搭主循环、定状态模型、接人工审批、接多渠道触发
- 评审现有 agent：按"症状 → 因子"映射体检
- 调试：上下文爆炸、错误死循环、审批卡死、重启丢状态

**不适用**：纯问答 chatbot（无 tool call）、单次 LLM 调用（无循环）——用普通 prompt 工程即可。

**范围**：12 因子只管 agent 架构。通用生产工程——幂等键、事件去重、并发控制、tracing、注入防护——照常要做，不在本 skill 覆盖范围，评审时也不要跳过。

## 12 因子速查

| # | 因子 | 一句话主张 | 违反症状 |
|---|------|-----------|---------|
| 1 | NL → Tool Calls | LLM 把自然语言转成结构化 intent，代码执行 | LLM 只做文本提取/摘要，决策全在代码里 |
| 2 | Own Your Prompts | prompt 是一等代码：可见、可 diff、可测试 | prompt 藏在框架 `Agent(role=...)` 黑盒里 |
| 3 | Own Your Context Window | 自定义 context 格式（事件 → XML/YAML），控密度 | 全量历史每次都塞进 messages |
| 4 | Tools = Structured Outputs | tool call 只是 LLM 输出的 JSON，执行方式由代码定 | 一个 tool 死板对应一个函数，无 intent 联合类型 |
| 5 | Unify State | 执行状态从事件历史推断，单一事实源 | 状态散在 cache / DB / 框架 memory / 本地变量 |
| 6 | Launch/Pause/Resume | 简单 API 启停；webhook 从断点恢复 | `while sleep` 轮询等待；重启从头跑 |
| 7 | Contact Humans via Tools | `request_human_input` 是一种 intent，回复是事件 | 审批是外部系统旁路，LLM 感知不到人在环中 |
| 8 | Own Your Control Flow | 自己写循环：按 intent 决定 continue/break/升级 | `agent.run()` 一把梭，无法中断、无法审查 tool call |
| 9 | Compact Errors | 错误进 context 让 LLM 自愈；计数阈值后升级 | 错误只 retry + 告警；或 traceback 无限塞入 |
| 10 | Small Focused Agents | 每个 agent 3-10 步（最多 ~20），职责单一 | 一个 agent 挂 20 个工具干所有事 |
| 11 | Trigger From Anywhere | Slack/email/cron/webhook 统一转成事件触发 | 只有单一 chat 入口 |
| 12 | Stateless Reducer | agent = `(thread, event) → 新事件` 的 fold | 隐式全局状态、内存长驻会话 |
| 13 | (附录) Pre-fetch Context | 高概率要用的数据确定性预取，别浪费 round trip | prompt 里写"你可能需要调用 list_X" |

细节见 [references/factors.md](references/factors.md)；完整循环模板见 [references/agent-loop.md](references/agent-loop.md)。

## 设计新 agent：检查清单

1. **主循环**：`determine_next_step(thread) → intent 联合类型 → switch → append event → continue/break`
2. **状态**：thread 事件列表可 JSON 序列化，是唯一状态源；`status`/`current_step` 能从事件推断就不单独存
3. **prompt**：独立模板文件，纳入版本管理和 eval
4. **context**：事件序列化为自定义紧凑格式；高概率数据直接 pre-fetch 进 context
5. **人工**：`request_human_input` intent → 存 thread → break → webhook 收到回复 append `human_response` → 恢复循环。**禁止 sleep 轮询**。审批拒绝/要求补充材料同样是 `human_response` 事件，LLM 读到后自行决定后续
6. **策略门**：硬性业务规则（金额阈值、合规）用确定性代码拦截高危 intent 并转 `request_human_input`——LLM 提议、代码裁决，这是 F8 的正当用法，不是违反 F1
7. **错误**：`try/except` 后错误事件进 context 继续循环；`consecutive_errors >= 3` 才 break 升级人
8. **边界**：单 agent 超过 ~10 步就拆；高危操作在 tool selection 与 execution 之间插入审批断点
9. **入口**：所有触发源归一成统一 event 进入同一循环；审批超时/提醒用 cron 产生新事件，不是轮询

## 评审现有 agent：症状 → 因子

评审纪律：代码里看不到的信息（触发源、部署方式、框架内部语义），标注"无法确认"并列出需要补的上下文，不默认违反也不默认合规。

| 看到 | 违反 | 修法方向 |
|------|------|---------|
| `while True: sleep(30)` 等审批 | F6/F7 | 落盘 break + webhook 恢复；审批回复作为事件 |
| traceback 塞 memory 无限重试 | F9 | 错误摘要进 context + 连续错误计数阈值升级 |
| 状态散在 cache/DB/框架 memory | F5 | 统一到 thread；秘密类最小化外置 |
| 每次拉全量历史进 prompt | F3/F13 | 事件压缩/摘要；确定性 pre-fetch |
| `Agent(role=..., tools=[20个])` | F2/F8/F10 | prompt 收归代码；自写循环；拆小 agent |
| 框架自动循环到 done 不可见 | F1/F4/F8 | intent 联合类型 + 自写 switch |
| 错误只告警，LLM 见不到 | F9 | 短任务先让 LLM 读错误自愈 |
| 只有 chat 入口 | F11 | 触发源归一化为事件 |

## 常见借口（评审/设计时听到要反驳）

| 借口 | 现实 |
|------|------|
| "审批用定时轮询就够了" | 轮询浪费且粒度粗；webhook + 事件恢复精确且省资源，还能审批 tool call 本身 |
| "错误告警给运维就行" | 短任务 LLM 读错误自愈率很高；只在连续失败阈值后升级 |
| "执行状态和业务状态分开是最佳实践" | 那是传统基础设施遗留；thread 可推断执行状态。先统一，确有秘密再最小化分离 |
| "框架的 memory/loop 够用" | 够用——直到要调 prompt/上下文/控制流，那时已被锁死 |
| "工具多 = 能力强" | 上下文膨胀 = 迷失。拆小 agent，每个 3-10 步 |
| "LLM 只做提取，决策放代码更稳" | 稳但失去 agent 价值；intent 联合类型让 LLM 决策、代码控执行，两者兼得 |

## Red Flags（看到立刻停下来对照因子）

- 设计文档里没有"事件列表 / thread"这个角色
- 人工审批路径里出现 `sleep` / `poll` / `while`
- prompt 只存在于框架构造参数
- 单 agent 工具数 > 10
- 错误处理只有 retry + alert，没有进 LLM context
- 同时存在 `status` 字段和独立 `history` —— 先问：status 能否从事件推断？
