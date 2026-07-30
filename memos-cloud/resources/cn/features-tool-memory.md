# Tool Memory

将工具调用的决策、参数、执行结果和使用轨迹沉淀为可检索的记忆，帮助 Agent 更稳定地选择和使用工具。

## 工作原理

1. **写入 Tool Calling 信息**：通过 `addMessage` 传入含 `tool_calls` 的 assistant 消息和含结果的 `tool` 消息
2. **MemOS 处理**：
   - **Tool Schema 记忆**：结构化管理工具描述信息
   - **Tool Trajectory 记忆**：提取工具使用轨迹（上下文→调用→参数→结果）

## 写入 Tool Calling 消息

```python
import json, requests

tool_schema = [{
    "name": "get_weather",
    "description": "获取指定位置的当前天气信息",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "城市名"}
        },
        "required": ["location"]
    }
}]

data = {
    "user_id": "user_001",
    "conversation_id": "conv_tool",
    "messages": [
        {
            "role": "system",
            "content": f"你是一个可以调用工具的助手。\n<tool_schema>\n{json.dumps(tool_schema, ensure_ascii=False)}\n</tool_schema>"
        },
        {"role": "user", "content": "北京现在天气怎么样？"},
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": json.dumps({"location": "北京"})
                    }
                }
            ]
        },
        {
            "role": "tool",
            "tool_call_id": "call_123",
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"location": "北京", "temperature": "7°C", "condition": "多云"})
                }
            ]
        }
    ]
}

res = requests.post(
    f"{BASE_URL}/add/message",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
```

## 检索 Tool Memory

在 searchMemory 中启用 `include_tool_memory`：

```python
data = {
    "user_id": "user_001",
    "conversation_id": "conv_new",
    "query": "北京适合穿什么衣服",
    "include_tool_memory": True,
    "tool_memory_limit_number": 10
}

res = requests.post(
    f"{BASE_URL}/search/memory",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
```

## 返回结构

```json
{
  "tool_memory_detail_list": [
    {
      "id": "uuid",
      "tool_type": "ToolSchemaMemory",
      "tool_value": {
        "name": "get_weather",
        "description": "获取指定位置的当前天气信息",
        "parameters": {"type": "object", "properties": {"location": {"type": "string"}}}
      },
      "relativity": 0.45
    },
    {
      "id": "uuid",
      "tool_type": "ToolTrajectoryMemory",
      "tool_value": "用户询问北京天气 -> 调用 get_weather(location='北京') -> 返回：7°C，多云",
      "tool_used_status": [
        {
          "used_tool": "get_weather",
          "success_rate": 1.0,
          "tool_experience": "get_weather 需要有效的 location 参数"
        }
      ],
      "experience": "遇到天气查询任务时，调用 get_weather 并传入正确的城市名",
      "relativity": 0.48
    }
  ]
}
```

## Tool Memory 类型

| 类型 | 说明 |
|------|------|
| ToolSchemaMemory | 工具的结构化描述（名称、参数、功能） |
| ToolTrajectoryMemory | 工具使用轨迹（上下文→调用→结果→经验） |

## 使用场景

- Agent 自动学习工具使用模式，减少重复试错
- 跨会话复用工具调用经验
- 帮助模型更准确地选择工具和填充参数
