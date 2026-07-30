# 多模态消息

MemOS 支持文本、图片、文档等多类型输入，从多种媒体中提取信息并生成记忆。

## 支持的媒体类型

| 类型 | 格式 |
|------|------|
| 图片 | JPG, PNG 等常见格式 |
| 文档 | PDF, DOCX, DOC, TXT, JSON, MD, XML |

## 文件上传限制

- 单次请求最多 20 个文件
- 单个文件不超过 100 MB、200 页
- 多模态消息默认使用异步模式处理

## 上传图片

### 通过 URL

```python
import requests, json

data = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "这是我的行程截图"},
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/itinerary.png"}
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

### 通过 Base64

```python
import base64

with open("image.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

data = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                }
            ]
        }
    ]
}
```

## 上传文档

### 通过 URL

```python
data = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "file",
                    "file": {"file_data": "https://example.com/document.pdf"}
                }
            ]
        }
    ]
}
```

### 通过 Base64

```python
import base64

with open("document.pdf", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

data = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "file",
                    "file": {"file_data": b64}
                }
            ]
        }
    ]
}
```

## 混合内容示例

```python
data = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "这是我在学习 MemOS"},
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/screenshot.png"}
                },
                {
                    "type": "file",
                    "file": {"file_data": "https://example.com/notes.pdf"}
                }
            ]
        }
    ]
}
```

## 查询处理状态

文件记忆处理耗时较长，可通过 `get/status` 接口查询进度。
