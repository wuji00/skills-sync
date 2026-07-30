# MemOS Cloud Docs Index

This is the English task router. Choose the smallest resource set needed for the user's task. Do not load every resource by default.

## Pack Layers

| Pack | Scope | When to read |
| --- | --- | --- |
| [Starter Pack](starter-pack.md) | Fast path, project configuration, `addMessage` / `searchMemory`, FTS/verification, and core troubleshooting. | Broad integration, first-time success, product integration, or copy-paste prompt entry. |
| [Reference Pack](reference-pack.md) | API reference routing, Knowledge Base, Chat, Delete, and Feedback. | Full parameters, responses, API combinations, or KB-related interpretation. |
| [Advanced Pack](advanced-pack.md) | Multimodal, Tool Memory, Skill Memory, Filters, custom tags, and async nuance. | Explicit advanced feature requests or when Starter/Reference is insufficient. |

## Always Start Here

For broad or ambiguous requests, first read:

- [Starter Pack](starter-pack.md) — first-time integration path, FTS validation, project inspection, and safety guardrails.

Then choose one route below.

## Route Map

| User intent | Read first | Then read if needed | Expected output |
| --- | --- | --- | --- |
| "Integrate MemOS", "add long-term memory", Agent product, Vibe Coding | [starter-pack.md](starter-pack.md) | [reference-pack.md](reference-pack.md), [integration-guide.md](integration-guide.md) | Project-specific code that searches memory before LLM generation and writes the completed turn after reply generation. |
| First-time success / FTS / smoke test | [starter-pack.md](starter-pack.md) | [reference-pack.md](reference-pack.md) | CLI-first add -> search -> verify loop, plus failure triage. |
| Minimal Cloud API integration | [reference-pack.md](reference-pack.md) | [quick-start.md](quick-start.md), [api-add-message.md](api-add-message.md), [api-search-memory.md](api-search-memory.md) | Minimal HTTP or SDK calls with verified endpoint paths. |
| Use MemOS to generate replies | [reference-pack.md](reference-pack.md) | [api-chat.md](api-chat.md), [advanced-pack.md](advanced-pack.md) | Chat API usage; explain reduced control compared with addMessage + searchMemory. |
| Knowledge base or document retrieval | [reference-pack.md](reference-pack.md) | [features-knowledge-base.md](features-knowledge-base.md), [api-search-memory.md](api-search-memory.md), [api-add-feedback.md](api-add-feedback.md) | Knowledge-base creation/upload/retrieval plan or code; include `knowledgebase_ids`. |
| Memory filters, tags, metadata, Agent isolation | [advanced-pack.md](advanced-pack.md) | [features-filters.md](features-filters.md), [api-add-message.md](api-add-message.md), [api-search-memory.md](api-search-memory.md) | Filter and metadata examples matched to the user's schema. |
| Async writes or no search results right after write | [features-async-mode.md](features-async-mode.md) | [faq-and-limits.md](faq-and-limits.md), [api-add-message.md](api-add-message.md) | Sync vs async explanation and verification strategy. |
| Tool Memory / tool-call traces | [advanced-pack.md](advanced-pack.md) | [features-tool-memory.md](features-tool-memory.md), [api-add-message.md](api-add-message.md), [api-search-memory.md](api-search-memory.md) | Tool-call memory capture and retrieval pattern. |
| Skill memory or Skill upload | [advanced-pack.md](advanced-pack.md) | [features-skill.md](features-skill.md), [features-knowledge-base.md](features-knowledge-base.md), [api-search-memory.md](api-search-memory.md) | Skill file/package limits, upload path, and retrieval path. |
| Multimodal input | [advanced-pack.md](advanced-pack.md) | [features-multimodal.md](features-multimodal.md), [features-async-mode.md](features-async-mode.md), [faq-and-limits.md](faq-and-limits.md) | Multimodal write plan with async status caveats. |
| List/inspect a user's memories, or resolve memory_ids before delete | [reference-pack.md](reference-pack.md) | [api-get-memory.md](api-get-memory.md), [api-search-memory.md](api-search-memory.md) | Paginated fetch by `user_id` to obtain `id` values for later operations. |
| Delete memory | [reference-pack.md](reference-pack.md) | [api-delete-memory.md](api-delete-memory.md), [api-get-memory.md](api-get-memory.md), [api-search-memory.md](api-search-memory.md), [faq-and-limits.md](faq-and-limits.md) | Conservative deletion plan, confirmation boundary, and post-delete verification. |
| Rerank candidate documents | [reference-pack.md](reference-pack.md) | [api-rerank.md](api-rerank.md) | Reorder a set of candidate texts by relevance; not a replacement for searchMemory. |
| Feedback / correction | [reference-pack.md](reference-pack.md) | [api-add-feedback.md](api-add-feedback.md), [api-search-memory.md](api-search-memory.md), [features-knowledge-base.md](features-knowledge-base.md) | Feedback write path and verification plan. |
| Limits, errors, or no results | [faq-and-limits.md](faq-and-limits.md) | Relevant API or feature doc | Specific triage steps, not generic troubleshooting. |

## Route Selection Rules

- If the user asks to add memory to an app or Agent product, start with Product Integration.
- If the user asks for a demo or first success, use the FTS route before larger architecture work.
- If the user has an existing LLM pipeline, prefer `searchMemory` + prompt injection + `addMessage`. Use Chat API only for PoC or when the user wants MemOS to own generation.
- If docs disagree, prefer the specific API reference resource over broad guides and call out the inconsistency.

## Known Documentation Gaps

- Project configuration, Dashboard flow, project/app/agent/user concepts, and post-configuration verification need stronger product confirmation.
- Cloud vs Open Source boundaries must be handled explicitly; do not merge Cloud API code with local open-source server instructions unless the user asks for that route.
