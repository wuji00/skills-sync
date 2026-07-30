# Advanced Pack

本 Pack 放高级能力。只有用户明确需要这些能力，或 Starter/Reference 不足以完成任务时读取。

## 何时读取

- 多模态：图片、文件、截图、文档写入。
- Tool Memory：工具 schema、tool call、tool result、工具使用轨迹。
- Skill：自动生成 Skill、上传 Skill 文件、检索 Skill。
- Filters：复杂过滤、标签、metadata、Agent/app 隔离。
- Async：多模态、写入后立即检索、状态轮询等细节。

## 路由

| 任务 | 先读 | 再读 |
| --- | --- | --- |
| 图片/文件/多模态写入 | [features-multimodal.md](features-multimodal.md) | [features-async-mode.md](features-async-mode.md), [faq-and-limits.md](faq-and-limits.md) |
| 工具调用记忆 | [features-tool-memory.md](features-tool-memory.md) | [api-add-message.md](api-add-message.md), [api-search-memory.md](api-search-memory.md) |
| Skill 记忆或 Skill 上传 | [features-skill.md](features-skill.md) | [features-knowledge-base.md](features-knowledge-base.md), [api-search-memory.md](api-search-memory.md) |
| 复杂 filter / tag / metadata | [features-filters.md](features-filters.md) | [api-add-message.md](api-add-message.md), [api-search-memory.md](api-search-memory.md) |
| 异步处理和状态排查 | [features-async-mode.md](features-async-mode.md) | [faq-and-limits.md](faq-and-limits.md) |

## 高级能力边界

- Filters 是检索前的候选范围控制，不是应用授权系统。多租户隔离必须由业务权限层保证。
- Tool Memory 需要完整 tool call 和 tool result，上下文不完整时不要承诺能沉淀稳定经验。
- Skill 文件上传依赖 Knowledge Base；先确认 KB 已创建并关联项目。
- 多模态默认可能异步处理；不要用刚写入立刻搜不到判断失败。
- 高级能力代码仍必须保持 API Key 服务端保存。

## 输出要求

- 说明为什么需要 Advanced Pack，而不是 Starter/Reference 即可。
- 给出最小参数集合，避免一次性打开所有高级开关。
- 包含验证方式，尤其是异步、多模态、Tool Memory 和 Skill 检索。
