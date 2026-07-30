# MemOS Cloud 文档路由

本文件是中文任务路由入口。先选择最小文档集合，不要默认读取所有资源。

## Pack 分层

| Pack | 范围 | 何时读取 |
| --- | --- | --- |
| [Starter Pack](starter-pack.md) | 快速路径、项目配置、`addMessage` / `searchMemory`、FTS/验证、核心排错。 | 宽泛接入、首次体验、产品集成、复制 prompt 后的第一步。 |
| [Reference Pack](reference-pack.md) | API reference、Knowledge Base、Chat、Delete、Feedback。 | 需要完整参数、响应、API 组合或 KB 相关判断时。 |
| [Advanced Pack](advanced-pack.md) | 多模态、Tool Memory、Skill、Filters、自定义标签、异步细节。 | 用户明确要高级能力，或 Starter/Reference 不足以完成任务时。 |

## 总是先读

宽泛或模糊需求先读：

- [Starter Pack](starter-pack.md)：首次接入、FTS 验证、项目检查、安全边界和交付清单。

然后按任务进入下列路由。

## 任务路由

| 用户意图 | 先读 | 需要时再读 | 预期输出 |
| --- | --- | --- | --- |
| "帮我的产品/Agent 接入 MemOS"、长期记忆、Vibe Coding | [starter-pack.md](starter-pack.md) | [reference-pack.md](reference-pack.md), [integration-guide.md](integration-guide.md) | 贴合项目技术栈的代码：生成前检索记忆，回复后写回本轮对话。 |
| 首次体验 / FTS / smoke test | [starter-pack.md](starter-pack.md) | [reference-pack.md](reference-pack.md) | CLI 优先的 add -> search -> verify 闭环和失败排查。 |
| Cloud API 最小接入 | [reference-pack.md](reference-pack.md) | [quick-start.md](quick-start.md), [api-add-message.md](api-add-message.md), [api-search-memory.md](api-search-memory.md) | 使用已验证 endpoint 的最小 HTTP 或 SDK 调用。 |
| 让 MemOS 直接生成回复 | [reference-pack.md](reference-pack.md) | [api-chat.md](api-chat.md), [advanced-pack.md](advanced-pack.md) | Chat API 用法，并说明控制力低于 addMessage + searchMemory。 |
| 知识库 / 文档检索 | [reference-pack.md](reference-pack.md) | [features-knowledge-base.md](features-knowledge-base.md), [api-search-memory.md](api-search-memory.md), [api-add-feedback.md](api-add-feedback.md) | 知识库创建、上传、检索方案或代码，包含 `knowledgebase_ids`。 |
| Filter、标签、元数据、Agent 隔离 | [advanced-pack.md](advanced-pack.md) | [features-filters.md](features-filters.md), [api-add-message.md](api-add-message.md), [api-search-memory.md](api-search-memory.md) | 匹配用户业务 schema 的 filter/metadata 示例。 |
| 异步写入、写入后搜不到 | [features-async-mode.md](features-async-mode.md) | [faq-and-limits.md](faq-and-limits.md), [api-add-message.md](api-add-message.md) | sync/async 解释和验证策略。 |
| Tool Memory / tool-call traces | [advanced-pack.md](advanced-pack.md) | [features-tool-memory.md](features-tool-memory.md), [api-add-message.md](api-add-message.md), [api-search-memory.md](api-search-memory.md) | 工具调用记忆的写入和召回模式。 |
| Skill 记忆或 Skill 上传 | [advanced-pack.md](advanced-pack.md) | [features-skill.md](features-skill.md), [features-knowledge-base.md](features-knowledge-base.md), [api-search-memory.md](api-search-memory.md) | Skill 文件/包的限制、上传和检索路径。 |
| 多模态输入 | [advanced-pack.md](advanced-pack.md) | [features-multimodal.md](features-multimodal.md), [features-async-mode.md](features-async-mode.md), [faq-and-limits.md](faq-and-limits.md) | 多模态写入方案和异步状态说明。 |
| 查看 / 列出用户记忆、删除前定位 memory_ids | [reference-pack.md](reference-pack.md) | [api-get-memory.md](api-get-memory.md), [api-search-memory.md](api-search-memory.md) | 按 `user_id` 分页拉取记忆，拿到 `id` 供后续操作。 |
| 删除记忆 | [reference-pack.md](reference-pack.md) | [api-delete-memory.md](api-delete-memory.md), [api-get-memory.md](api-get-memory.md), [api-search-memory.md](api-search-memory.md), [faq-and-limits.md](faq-and-limits.md) | 保守删除方案、确认边界和删除后验证。 |
| 候选文档重排 / rerank | [reference-pack.md](reference-pack.md) | [api-rerank.md](api-rerank.md) | 对一组候选文本按相关性重排；它不是 searchMemory 的替代。 |
| 反馈 / 纠错 | [reference-pack.md](reference-pack.md) | [api-add-feedback.md](api-add-feedback.md), [api-search-memory.md](api-search-memory.md), [features-knowledge-base.md](features-knowledge-base.md) | 反馈写入路径和验证方案。 |
| 限制、错误、无结果 | [faq-and-limits.md](faq-and-limits.md) | 相关 API 或 feature 文档 | 具体排查步骤，不写泛泛 troubleshooting。 |

## 选择规则

- 用户说"给我的 app/产品/Agent 产品加记忆"时，走产品集成。
- 用户要 demo、首次跑通或 FTS 时，先做 FTS 闭环，再做完整架构。
- 已有 LLM pipeline 时，默认使用 `searchMemory` + prompt injection + `addMessage`。只有用户想让 MemOS 负责生成回复时才用 Chat API。
- 文档冲突时，以具体 API reference 为准，并指出冲突。

## 文档缺口

- 项目配置、Dashboard 路径、project/app/agent/user 概念和配置后验证仍需产品确认。
- Cloud 与 Open Source 边界必须显式处理，不要把 Cloud API、本地部署、MCP、Dashboard 和 CLI 混用。
