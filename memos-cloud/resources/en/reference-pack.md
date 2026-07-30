# Reference Pack

Use this pack for fuller API and KB decisions. Do not load it by default during the Starter Pack path.

## When To Read

- The user needs full API parameters, response shape, error boundaries, or SDK/HTTP comparison.
- The user needs Knowledge Base, document retrieval, or Skill file upload.
- The user needs Chat, Delete Memory, Add Feedback, or deeper troubleshooting.

## API Reference Routing

| Task | Read |
| --- | --- |
| Write conversations or user information | [api-add-message.md](api-add-message.md) |
| Search fact/preference/Skill/Tool/KB memories | [api-search-memory.md](api-search-memory.md) |
| List/paginate a user's memories, or resolve `memory_ids` before delete | [api-get-memory.md](api-get-memory.md) |
| Let MemOS generate replies | [api-chat.md](api-chat.md) |
| Delete memories | [api-delete-memory.md](api-delete-memory.md) |
| Correct or update through natural language | [api-add-feedback.md](api-add-feedback.md) |
| Rerank candidate documents by relevance | [api-rerank.md](api-rerank.md) |
| Limits, errors, or no results | [faq-and-limits.md](faq-and-limits.md) |

Core Cloud endpoints must match OpenAPI/API reference:

- `POST /add/message`
- `POST /search/memory`
- `POST /get/memory`
- `POST /chat`
- `POST /delete/memory`
- `POST /add/feedback`
- `POST /rerank`

If you see `/messages/` or bare `/search/`, treat it as stale documentation and do not generate code for it.

## Knowledge Base Routing

Read [features-knowledge-base.md](features-knowledge-base.md), then read as needed:

- [api-search-memory.md](api-search-memory.md): search with `knowledgebase_ids`.
- [api-add-feedback.md](api-add-feedback.md): correct knowledge-base memories with `allow_knowledgebase_ids`.
- [features-skill.md](features-skill.md): upload Skill files; this belongs to Advanced Pack.

Before writing KB code, confirm:

- The knowledge base exists and is associated with the current project.
- `knowledgebase_ids` belong to the project of the current API key.
- Document processing is complete; read async/status guidance when needed.

## Output Requirements

- State the endpoint and request fields used.
- Explain where `user_id`, `conversation_id`, `knowledgebase_ids`, and `filter` come from.
- Include verification steps for delete and feedback operations.
- If local docs conflict with API reference, prefer OpenAPI/API reference and call out the inconsistency.
