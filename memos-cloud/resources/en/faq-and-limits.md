# FAQ And Limits

## Resource Limits

### API Limits

| API | Single input limit | Output limit |
| --- | --- | --- |
| addMessage | 40,000 tokens | - |
| searchMemory | 40,000 tokens | 25 fact memories, 25 preferences, 25 Tool memories, 25 Skills |
| Chat | 8,000 tokens | 25 fact memories and 25 preferences |

### Rate Limits

- Total tokens per minute: up to 400,000.
- Suggested QPS: 50 or lower. This is guidance; high concurrency may still be affected by platform capacity.

### Document Upload Limits

- Supported types: PDF, DOCX, DOC, TXT, JSON, MD, XML.
- Single file: up to 100 MB and up to 500 pages for knowledge-base uploads.
- Single upload request: up to 20 files.
- Skill `.md`: up to 100 KB.
- Skill `.zip`: up to 20 MB and up to 200 extracted files.

### Quota Notes

- Free quota is counted by developer account; all projects under the same account share it.
- Failed requests caused by auth errors, parameter errors, or limit errors do not consume quota.
- Requests over the per-call limit return an error and do not consume quota.

## FAQ

### How is MemOS different from standard RAG?

| Dimension | RAG | MemOS |
| --- | --- | --- |
| Result shape | Raw text chunks | Refined memory units that use fewer tokens |
| Retrieval scope | Broad corpus scan | Layered scheduling and faster targeted hits |
| Personalization | Usually none | Extracts user preferences automatically |
| Evolution | Static | Updates through feedback and conversation |

RAG provides external knowledge. MemOS provides internal memory. They can be used together.

### What are the core MemOS Cloud APIs?

- `addMessage`: writes raw information and extracts memory.
- `searchMemory`: retrieves relevant memory.

### Will memory grow without bound?

MemOS manages memory lifecycle through merge, compression, and archival mechanisms. Low-value memory can be downgraded while high-value memory is merged or stabilized.

### Does memory affect inference latency?

Memory scheduling runs asynchronously. Memory retrieval usually returns within roughly 600 ms.

### Does MemOS support private deployment?

Yes. MemOS offers both a **Cloud** service and an **Open Source** self-hosted option. This skill covers Cloud API integration only. Do not mix Cloud API calls with open-source/local-deploy, MCP, Dashboard, or CLI install steps in one block unless the user explicitly asks for that route.

### Cloud vs Open Source: which one?

| Option | Best for | Notes |
| --- | --- | --- |
| Cloud | Fast integration, no storage maintenance | Calls `https://memos.memtensor.cn/api/openmem/v1` with an API key; this skill defaults here. |
| Open Source self-host | Custom LLM/backend, deep customization | Self-hosted server; base URL points to your own deployment. |

Use a self-host base URL only when the user has confirmed that route; otherwise use the Cloud default.

### Can MemOS work with existing RAG or knowledge graphs?

Yes. MemOS memory units can be combined with vector retrieval or external knowledge graphs.

### How long after addMessage can memory be searched?

- Async mode: usually seconds to tens of seconds.
- Sync mode: searchable after the API returns.
- Multimodal input: file/image processing takes longer; use `get/status` when available.

## Troubleshooting

### Error Code Quick Reference

| Code | Meaning | Fix |
|------|---------|-----|
| **Parameter Errors** | | |
| 40000 | Bad request parameters | Check param names, types, and format. |
| 40001 | Resource not found | Verify memory_id or resource ID. |
| 40002 | Required field is empty | Fill in missing required fields (user_id, messages, etc.). |
| 40003 | Parameter is empty | Check list/object is not empty. |
| 40010 | User ID too long | user_id must be ≤ 100 characters. |
| 40011 | Conversation ID too long | conversation_id must be ≤ 100 characters. |
| 40020 | Invalid project ID | Verify Project ID format. |
| **Auth Errors** | | |
| 40100 / 40130 | API Key required | Add `Authorization: Token YOUR_KEY` header. |
| 40132 | API Key invalid or expired | Check key status or regenerate on Dashboard. |
| **Quota / Rate Limit** | | |
| 40300 | API call limit exceeded | Request more quota or upgrade plan. |
| 40301 | Request token limit exceeded | Reduce input content. |
| 40302 | Response token limit exceeded | Shorten expected output. |
| 40303 | Single conversation length exceeded | Trim single input/output. |
| 40304 | Account total API calls exhausted | Request more quota. |
| 40305 | Input exceeds per-call token limit | Split messages into batches. |
| 40306 | Memory delete auth failed | Confirm permission to delete. |
| 40307 | Memory to delete not found | Use getMemory to confirm memory_id first. |
| 40308 | User for memory delete not found | Verify user_id. |
| **System / Service** | | |
| 50000 | Internal system error | Retry later or contact support. |
| 50004 | Memory service unavailable | Retry memory write/get later. |
| 50005 | Search service unavailable | Retry searchMemory later. |
| 50143 | addMemory failed | Algorithm error; retry later. |
| 50144 | addMessage failed | Save failed; retry later. |
| **Knowledge Base** | | |
| 50103 | File count exceeded | Max 20 files per request. |
| 50104 | Single file too large | Max 100 MB per file. |
| 50105 | Total size exceeded | Max 300 MB per request. |
| 50120 | Knowledge base not found | Verify knowledgebase ID. |
| 50123 | Knowledge base not linked to project | Ensure KB is authorized for the current project. |

### Common Scenarios

| Scenario | Likely cause | Fix |
| --- | --- | --- |
| `401 Unauthorized` | Invalid or expired API key | Check `Authorization: Token YOUR_KEY`; key starts with `mpg-`. |
| Parameter error | Missing required fields | Ensure `user_id`, `conversation_id`, and required payload fields are present. |
| Limit error (40305) | Request exceeds token or file limits | Split messages or files into batches. |
| No search result after write | Memory has not finished processing | Wait and retry, or use sync mode if supported and required. |
| File processing failed | File size/page/type limit exceeded | Adjust file to documented limits and retry. |
