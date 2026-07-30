# Reference Pack

本 Pack 放需要较完整 API 和 KB 判断的内容。不要在 Starter Pack 阶段默认读取本文件。

## 何时读取

- 用户需要完整 API 参数、响应结构、错误边界或 SDK/HTTP 对照。
- 用户要做 Knowledge Base / 文档检索 / Skill 文件上传。
- 用户要 Chat、Delete Memory、Add Feedback 或更完整排错。

## API Reference 路由

| 任务 | 读取 |
| --- | --- |
| 写入对话或用户信息 | [api-add-message.md](api-add-message.md) |
| 检索事实/偏好/Skill/Tool/KB 记忆 | [api-search-memory.md](api-search-memory.md) |
| 按用户列出/翻页记忆、删除前定位 `memory_ids` | [api-get-memory.md](api-get-memory.md) |
| 让 MemOS 直接生成回复 | [api-chat.md](api-chat.md) |
| 删除记忆 | [api-delete-memory.md](api-delete-memory.md) |
| 自然语言纠错/更新 | [api-add-feedback.md](api-add-feedback.md) |
| 候选文档相关性重排 | [api-rerank.md](api-rerank.md) |
| 限制、错误、无结果 | [faq-and-limits.md](faq-and-limits.md) |

核心 Cloud endpoint 必须与 OpenAPI/API reference 一致：

- `POST /add/message`
- `POST /search/memory`
- `POST /get/memory`
- `POST /chat`
- `POST /delete/memory`
- `POST /add/feedback`
- `POST /rerank`

如果看到 `/messages/` 或裸 `/search/`，按旧文档错误处理，不要生成对应代码。

## Knowledge Base 路由

读取 [features-knowledge-base.md](features-knowledge-base.md)，并按需再读：

- [api-search-memory.md](api-search-memory.md)：用 `knowledgebase_ids` 联合检索。
- [api-add-feedback.md](api-add-feedback.md)：用 `allow_knowledgebase_ids` 做知识库纠错。
- [features-skill.md](features-skill.md)：上传 Skill 文件时再读，属于 Advanced Pack。

KB 相关代码应先确认：

- 知识库是否已创建并关联当前项目。
- `knowledgebase_ids` 是否来自当前 API Key 所属项目。
- 文档处理是否完成；需要时读 async/status 相关说明。

## Reference Pack 输出要求

- 明确使用的 endpoint 和请求体字段。
- 说明 `user_id`、`conversation_id`、`knowledgebase_ids`、`filter` 的来源。
- 删除和反馈操作要包含验证步骤。
- 如果本地文档与 API reference 冲突，以 OpenAPI/API reference 为准，并指出冲突。
