# Agent 主循环模板（12-factor 风格）

语言无关伪代码，实现 F1/F3/F4/F5/F6/F7/F8/F9/F12。可直接改造成 Python/TS。

## 1. 数据结构：thread = 唯一状态源（F5/F12）

```python
class Thread:
    events: list[Event]   # 全部状态；可 JSON 序列化

class Event:
    type: str   # "slack_message" | "refund_order" | "refund_order_result"
                # | "request_human_input" | "human_response" | "error" | ...
    data: dict  # 该事件类型的 payload

def thread_to_prompt(thread: Thread) -> str:
    # F3：自定义 context 格式，事件 -> XML/YAML，追求密度
    return "\n\n".join(f"<{e.type}>\n{to_yaml(e.data)}\n</{e.type}>" for e in thread.events)
```

## 2. intent 联合类型（F1/F4）

```python
# LLM 的唯一输出：下一个 intent（structured output / tool call）
NextStep = RefundOrder | FetchOrder | RequestHumanInput | DoneForNow

def determine_next_step(thread: Thread) -> NextStep:
    prompt = PROMPT_TEMPLATE.render(thread=thread_to_prompt(thread))  # F2：模板是代码
    return llm.structured_call(prompt, schema=NextStep)
```

prompt 模板骨架（F2：独立文件，可 diff 可 eval）：

```jinja
You are a support agent. Decide the next step ONLY; deterministic code executes it.
Rules: refund > $500 requires prior human approval; never invent order ids.

Here's what's happened so far:
{{ thread }}

What's the next step? Output one of: {{ intent_schema }}
```

## 3. 主循环（F8/F9）

```python
MAX_CONSECUTIVE_ERRORS = 3

async def handle_next_step(thread: Thread):
    consecutive_errors = 0
    while True:
        next_step = determine_next_step(thread)
        thread.events.append(Event(type=next_step.intent, data=next_step))

        try:
            if next_step.intent == "request_human_input":      # F7
                await save_state(thread)
                await notify_human(next_step)                  # Slack/email/审批 UI
                return                                         # break：等 webhook
            elif next_step.intent == "done_for_now":
                await save_state(thread)
                return
            else:                                              # 同步工具
                result = await execute_tool(next_step)         # 确定性执行
                thread.events.append(Event(type=next_step.intent + "_result", data=result))
                consecutive_errors = 0
        except Exception as e:                                 # F9：错误进 context 自愈
            consecutive_errors += 1
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                await save_state(thread)
                await escalate_to_human(thread, e)             # 阈值后升级
                return
            thread.events.append(Event(type="error", data=format_error_compact(e)))
```

## 3b. 策略门：selection 与 execution 之间的审批断点（F6/F8）

LLM 已输出高危 intent 但业务规则要求审批时：**先落 intent 事件，再追加审批请求事件**，不要替换或丢弃。thread 里同时存在未执行的 `execute_refund` 和 `request_human_input` 是正确的——恢复后按序执行。

```python
        # 在 execute_tool 之前拦截（selection 已发生、execution 未发生）
        if is_high_risk(next_step) and not has_human_approval(thread):
            thread.events.append(Event(type="request_human_input", data=to_approval_request(next_step)))
            await save_state(thread)
            await notify_human(...)
            return                       # break：等 webhook
        # 有批准后，执行那个已落盘的 intent
        result = await execute_tool(next_step)
```

LLM 提议、代码裁决——硬性规则（金额阈值、合规）永远走确定性策略门，不靠 prompt 约束。

- `request_human_input` 必须带 `request_id` 并记录原 intent 的 `intent_id`；`human_response` 带回 `request_id`，策略门据此匹配——否则恢复后不知道批准的是哪个 intent
- `human_response` 的 payload 按业务自定义：可以带修正参数（如"批准，但换成 v1.2.4"），策略门校验时以 payload 里的修正值为准

## 4. webhook 恢复（F6/F7/F11）

```python
@app.post("/webhook")
async def webhook(req):
    thread = await load_state(req.thread_id)
    thread.events.append(Event(type="human_response", data=req.body))  # 人回复 = 事件
    await handle_next_step(thread)        # 从断点继续循环
    return {"status": "ok"}
```

- 拒绝/要求补充材料同样是 `human_response` 事件（`approved: false` / `needs_info: [...]`），LLM 读到后自行决定后续 intent（notify_customer / escalate / done）
- 审批超时与提醒：cron 定时产生 `approval_reminder` 事件进同一循环，不是 sleep 轮询

## 5. pre-fetch（F13）

```python
# 模型高概率要用的只读数据：直接预取进 thread，别让它自己花一轮去取
order = await fetch_order(req.order_id)
thread.events.append(Event(type="fetch_order_result", data=order))
await handle_next_step(thread)
```

触发源没有明确实体 id 时（如 cron），预取该触发源自身会产出的数据（待办列表、队列快照）；没有可预取的就跳过，不为预取而预取。

## 使用要点

- 设计时先写 `Event` 类型清单和 `NextStep` 联合类型——这两个文件就是架构本身
- 审批断点放 `execute_tool` 之前：selection 已发生、execution 未发生
- `format_error_compact`：错误摘要（类型 + 消息 + 关键字段），不是完整 traceback
- 已解决的 error 事件可在后续压缩 context 时移除（F3）
