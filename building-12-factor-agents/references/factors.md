# 12 因子详解

每因子：核心主张 / 违反症状 / 检查点。原文：https://github.com/humanlayer/12-factor-agents

## Factor 1: Natural Language to Tool Calls

**主张**：agent 最基本的原子模式——LLM 把自然语言翻译成结构化 tool call（JSON），确定性代码接收并执行。

**违反症状**：LLM 只产出自由文本，代码再用正则/NLP 二次解析；或 LLM 只做"提取节点"，从不在循环里决定下一步。

**检查点**：能否指出系统里"自然语言 → 结构化 intent"发生的精确位置？intent 有没有类型定义？

## Factor 2: Own Your Prompts

**主张**：prompt 是应用逻辑与 LLM 之间的主接口，必须是一等代码。不要用框架黑盒（`Agent(role=..., goal=..., personality=...)`）代管。

**收益**：完全控制 token；可对 prompt 写测试/eval；快速迭代；可用 role hacking 等非标技巧。

**违反症状**：改 prompt 需要读框架源码；无法回答"模型此刻看到的确切 token 是什么"。

**检查点**：prompt 是否在独立模板文件、纳入版本管理、有 eval？

## Factor 3: Own Your Context Window

**主张**：给 LLM 的输入永远是"到目前为止发生了什么，下一步是什么"。不必用标准 messages 格式——可把整个历史序列化成单条 user 消息里的 XML/YAML 事件流，追求信息密度和 token 效率。

**违反症状**：全量历史无压缩塞入；RAG/记忆/工具结果格式不受控；敏感数据无过滤直送模型。

**检查点**：存在一个 `thread_to_prompt(thread)` 类的函数，context 构建可单测。已解决的错误可以从 context 里移除。

**事件类型治理**（状态/事件类型太多时）：约定优于类型——结果事件统一 `X_result` 后缀，error/human/trigger 等通用事件定义一次全体 agent 复用；严格类型只上在 LLM 出口（`NextStep` 联合类型，它是模型契约）；存储层 `Event(type: str, data: dict)` 即可，需要事件版本迁移时再上 registry，别提前建。

## Factor 4: Tools Are Just Structured Outputs

**主张**：tool call 本质是 LLM 输出的一段 JSON，描述"想让确定性代码做什么"。代码不必死板执行同名函数——可以汇总、拒绝、改写、转人工。

```python
class CreateIssue:
    intent: "create_issue"
    issue: Issue

class SearchIssues:
    intent: "search_issues"
    query: str
```

**违反症状**：tool 与函数一一硬绑；模型输出无法被代码拦截审查。

**检查点**：所有 intent 组成一个联合类型（union），switch 分发，default 分支处理未知 intent。

## Factor 5: Unify Execution State and Business State

**主张**：执行状态（当前步骤、等待状态、重试次数）只是"已发生事件"的元数据，尽量从 thread 推断，不为它建第二套存储。

**收益**：单一事实源、可序列化、可从任意点恢复、可 fork、可直接渲染成人可读 UI。

**违反症状**：`status` 字段与 `history` 各自维护、可能不一致；恢复逻辑要拼接多处状态。

**检查点**：问"当前进行到哪一步"时，答案能否纯从事件列表推出？秘密（session id、密码上下文）允许外置，但要最小化。

## Factor 6: Launch/Pause/Resume with Simple APIs

**主张**：agent 是程序，要有简单的 launch/pause/resume/stop API。长操作（人工审批、外部 pipeline）时 pause 落盘；webhook 到来时从断点 resume，不与 orchestrator 深耦合。

**关键细节**：pause 必须能发生在 **tool selection 与 tool execution 之间**——否则无法在执行前审查高危 tool call。

**违反症状**：`while...sleep` 阻塞等外部事件；进程中断后从头重跑。

## Factor 7: Contact Humans with Tool Calls

**主张**：`request_human_input` 是一个 intent（带 question/context/options），人类回复 `human_response` 是一个事件。LLM 始终输出 JSON 声明意图，而不是赌第一个 token 是文本还是 tool call。

**收益**：agent 可在 chat 界面之外运行（outer loop：cron/事件触发，关键节点找人）；支持多人协作；可扩展为 Agent→Agent。

**违反症状**：审批走旁路系统，thread 里看不到"问过人、人答了什么"。

## Factor 8: Own Your Control Flow

**主张**：自己写主循环，按 intent 决定 continue（同步步骤）/ break（异步等待）/ 升级。这样可以插入：结果缓存与摘要、LLM-as-judge、context 压缩、限流、durable sleep、以及在 tool selection 与 invocation 之间中断审批。

**策略门是正当用法**：硬性业务规则（金额阈值、合规）用确定性代码拦截高危 intent 并转 `request_human_input`。LLM 提议、代码裁决——这不是违反 F1，而是 F8 的核心价值。

**违反症状**：`agent.run()` 黑盒循环；无法回答"此刻它在执行第几步、为什么"。

## Factor 9: Compact Errors into Context Window

**主张**：工具失败时，把错误（压缩后的摘要，不一定是完整 traceback）作为事件进 context，LLM 大概率能读懂并修正下一次调用——这是自愈。用 `consecutive_errors` 计数，阈值（如 3）后 break、清 context、或升级给人。

**违反症状**：错误只走 retry+alert，LLM 永远不知道自己失败了；或错误无限累积直到 context 爆炸、agent 原地打转（spin out）。

**检查点**：有单工具/全局连续错误上限；已解决的错误可从 context 移除或重构表示。错误不必先确定性分类：进 context 后 LLM 自己会判断（参数无效 → 修参数或问人；超时 → 换方式重试）；只有明确不可恢复的错误才直接确定性升级。

## Factor 10: Small, Focused Agents

**主张**：agent 是更大的、主要确定性系统里的一块积木。每个 agent 只做一件事，3-10 步（最多 ~20）。context 越长 LLM 越容易迷失。

**违反症状**：单 agent 工具数 >10；一个 loop 里混合多个业务域。

**检查点**：能用一句话说清每个 agent 的职责；步数有预算。LLM 变强后可以逐步扩大 scope，但要有意识地扩。

**拆分信号**（满足其一就考虑拆）：步数预算超限；工具横跨多个业务域（客服 + 风控 + 库存）；context 里混入互不相关的事件流；intent 联合类型超过 ~15 个。接近上限（7-10 步）但职责单一、事件同域的可以不拆。

## Factor 11: Trigger From Anywhere

**主张**：用户在他们所在的渠道（Slack/email/sms）触发和接收回复；非人触发源（cron、告警、事件）同样是一等公民。前提：已做到 F6 + F7。

**违反症状**：agent 只能从一个自建 chat UI 访问；cron 触发要绕过主流程另写一套。

**检查点**：所有触发源归一化为统一 event 类型进入同一主循环。`thread_id` 按渠道命名空间生成（`slack:channel:ts` / `email:message-id` / `cron:job:run`）；同一客户跨渠道合并是业务决策。事件去重、幂等、并发乱序用存储层约束解决——通用事件溯源问题，不在因子范围。

**thread 路由规则**：按业务实体建 thread（如 `deploy:<tag>`、`refund:<order_id>`），一个实体一条事件流；周期提醒/超时类事件找到对应实体的 thread 追加，不新开 thread。

## Factor 12: Make Your Agent a Stateless Reducer

**主张**：形式化前面所有因子——agent 是 `(state, event) → state'` 的 fold/reducer。无隐式内存状态，纯由事件流驱动。

**检查点**：给定同一事件序列，重放能得到同一状态。

## Factor 13 (附录): Pre-fetch All the Context You Might Need

**主张**：如果模型高概率要调用某个只读工具（如 list_git_tags），不要浪费一个 round trip 让它自己去取——确定性代码直接预取，把结果放进 context，并把该 intent 从联合类型里删掉。

> 已经知道要用什么工具，就确定性地调用它，让模型专注难题：怎么用这些输出。

**检查点**：评审 prompt 里出现"你可能需要调用 X 来获取 Y"时，改成直接预取 Y。
