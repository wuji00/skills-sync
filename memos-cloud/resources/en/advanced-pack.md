# Advanced Pack

Use this pack for advanced capabilities only when the user explicitly needs them or Starter/Reference cannot complete the task.

## When To Read

- Multimodal: images, files, screenshots, or document writes.
- Tool Memory: tool schemas, tool calls, tool results, and tool-use trajectories.
- Skill: generated Skills, uploaded Skill files, and Skill retrieval.
- Filters: complex filtering, tags, metadata, and Agent/app isolation.
- Async: multimodal processing, immediate search after write, or status polling.

## Routing

| Task | Read first | Then read |
| --- | --- | --- |
| Image/file/multimodal write | [features-multimodal.md](features-multimodal.md) | [features-async-mode.md](features-async-mode.md), [faq-and-limits.md](faq-and-limits.md) |
| Tool-call memory | [features-tool-memory.md](features-tool-memory.md) | [api-add-message.md](api-add-message.md), [api-search-memory.md](api-search-memory.md) |
| Skill memory or Skill upload | [features-skill.md](features-skill.md) | [features-knowledge-base.md](features-knowledge-base.md), [api-search-memory.md](api-search-memory.md) |
| Complex filters / tags / metadata | [features-filters.md](features-filters.md) | [api-add-message.md](api-add-message.md), [api-search-memory.md](api-search-memory.md) |
| Async handling and status triage | [features-async-mode.md](features-async-mode.md) | [faq-and-limits.md](faq-and-limits.md) |

## Advanced Boundaries

- Filters control candidate memory scope before retrieval; they are not an application authorization system. Multi-tenant isolation still belongs in the business permission layer.
- Tool Memory needs complete tool call and tool result context. Do not promise stable tool experience when the trace is incomplete.
- Skill file upload depends on Knowledge Base. Confirm the KB exists and is associated with the project first.
- Multimodal processing may be async by default. Do not treat an immediate search miss as failure.
- Advanced feature code must still keep API keys server-side.

## Output Requirements

- Explain why Advanced Pack is needed instead of Starter/Reference alone.
- Use the smallest parameter set required; do not enable every advanced switch at once.
- Include verification, especially for async, multimodal, Tool Memory, and Skill retrieval.
