# Multimodal Messages

MemOS supports text, images, and documents. It can extract information from multimodal input and generate memory.

## Supported Media

| Type | Formats |
| --- | --- |
| Images | JPG, PNG, and common image formats. |
| Documents | PDF, DOCX, DOC, TXT, JSON, MD, XML. |

## Upload Limits

- Up to 20 files per request.
- Single file up to 100 MB and up to 200 pages for multimodal messages.
- Multimodal messages use async processing by default.

## Upload Image

### URL

```python
import requests

payload = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "This is my itinerary screenshot."},
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
    json=payload,
)
```

### Base64

```python
import base64

with open("image.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

payload = {
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

## Upload Document

### URL

```python
payload = {
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

### Base64

```python
import base64

with open("document.pdf", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

payload = {
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

## Mixed Content

```python
payload = {
    "user_id": "user_001",
    "conversation_id": "conv_001",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "These are my MemOS notes."},
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

## Processing Status

File extraction can take longer than text writes. Use `get/status` when status polling is available, or wait before running `searchMemory`.
