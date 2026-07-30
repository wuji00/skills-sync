# Tool Memory

Tool Memory captures tool schemas, tool-call decisions, parameters, results, and trajectories so an Agent can reuse tool-use experience across turns and sessions.

## How It Works

1. Write tool-calling messages through `addMessage`, including assistant messages with `tool_calls` and `tool` role messages with results.
2. MemOS extracts:
   - Tool Schema Memory: structured tool descriptions.
   - Tool Trajectory Memory: context -> tool call -> parameters -> result -> experience.

## Write Tool Calling Messages

```python
import json
import requests

tool_schema = [{
    "name": "get_weather",
    "description": "Get current weather for a location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City name"}
        },
        "required": ["location"]
    }
}]

payload = {
    "user_id": "user_001",
    "conversation_id": "conv_tool",
    "messages": [
        {
            "role": "system",
            "content": f"You are an assistant that can call tools.\n<tool_schema>\n{json.dumps(tool_schema)}\n</tool_schema>"
        },
        {"role": "user", "content": "What is the weather in Beijing?"},
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": json.dumps({"location": "Beijing"})
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
                    "text": json.dumps({"location": "Beijing", "temperature": "7C", "condition": "cloudy"})
                }
            ]
        }
    ]
}

res = requests.post(
    f"{BASE_URL}/add/message",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
```

## Search Tool Memory

Enable `include_tool_memory` in `searchMemory`:

```python
payload = {
    "user_id": "user_001",
    "conversation_id": "conv_new",
    "query": "What should I wear in Beijing today?",
    "include_tool_memory": True,
    "tool_memory_limit_number": 10
}

res = requests.post(
    f"{BASE_URL}/search/memory",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=payload,
)
```

## Response Shape

```json
{
  "tool_memory_detail_list": [
    {
      "id": "uuid",
      "tool_type": "ToolSchemaMemory",
      "tool_value": {
        "name": "get_weather",
        "description": "Get current weather for a location.",
        "parameters": {"type": "object", "properties": {"location": {"type": "string"}}}
      },
      "relativity": 0.45
    },
    {
      "id": "uuid",
      "tool_type": "ToolTrajectoryMemory",
      "tool_value": "User asked weather in Beijing -> called get_weather(location='Beijing') -> returned 7C, cloudy",
      "tool_used_status": [
        {
          "used_tool": "get_weather",
          "success_rate": 1.0,
          "tool_experience": "get_weather requires a valid location parameter"
        }
      ],
      "experience": "For weather questions, call get_weather with a city name.",
      "relativity": 0.48
    }
  ]
}
```

## Tool Memory Types

| Type | Meaning |
| --- | --- |
| `ToolSchemaMemory` | Structured tool description: name, parameters, and function. |
| `ToolTrajectoryMemory` | Tool-use trajectory: context, call, result, and learned experience. |

## Use Cases

- Help Agents learn tool-use patterns.
- Reuse tool-call experience across sessions.
- Improve tool selection and parameter filling.
