# MemOS Cloud Starter Pack

宽泛接入需求先读本文件。目标是在用户真实项目里跑通一个安全、可验证的记忆闭环。

## 快速判断

| 场景 | 默认路径 | 默认不要做 |
| --- | --- | --- |
| 用户在开发 AI app、chatbot、Agent 产品或后端服务 | 服务端接入 MemOS Cloud：LLM 生成前 `searchMemory`，生成后 `addMessage`。 | 不要在验证 Key 和 endpoint 前做完整架构。 |
| 用户想要 demo 或首次跑通 | 优先用 CLI 做 add -> search smoke test；CLI 不可用时用 HTTP/cURL。 | 不要在验证 Key 和 endpoint 前做完整架构。 |
| 用户想让 MemOS 直接生成回复 | 使用 Chat API。 | 不要把 Chat API 再包进已有 LLM pipeline。 |
| 用户要检索公司文档、政策或文件 | 使用 Knowledge Base + `knowledgebase_ids`。 | 不要把项目文档写成用户个人记忆。 |

## 先检查项目

改代码前先确认：

- 运行时和包管理器：`package.json`、`pyproject.toml`、`requirements.txt`、`pom.xml`、`build.gradle`、`manifest.json`。
- 后端边界：API routes、server actions、services、controllers、workers、extension background scripts。
- 现有 LLM 调用路径：prompt 在哪里组装，回复在哪里生成。
- 用户身份来源：登录用户 ID、tenant ID、workspace ID 或匿名 session fallback。
- 会话身份来源：chat thread ID、session ID、request ID 或 room ID。
- 密钥处理：`.env`、部署变量、配置服务或 secret manager。
- 测试命令：lint、type check、unit tests、integration tests。

如果没有后端，说明生产级 MemOS Cloud Key 不能放进客户端代码；先补 backend/proxy，或只做本地 demo。

## 默认产品集成闭环

1. 读取用户最新输入。
2. 用稳定 `user_id`、当前 `conversation_id` 和用户输入作为 `query` 调用 `searchMemory`。
3. 只把相关记忆格式化进模型 prompt，不向终端用户暴露内部记忆术语。
4. 调用产品现有 LLM。
5. 用完整 user/assistant 消息调用 `addMessage`。
6. 返回回复。写回失败时，除非产品要求强一致，否则不要让用户回复失败。

```text
用户输入
  -> searchMemory(query, user_id, conversation_id)
  -> 用筛选后的记忆组装 prompt
  -> 调用现有 LLM
  -> addMessage([user, assistant], user_id, conversation_id)
  -> 返回回复
```

## 最小 HTTP Contract

除非项目已有已验证覆盖，使用：

```text
MEMOS_BASE_URL=https://memos.memtensor.cn/api/openmem/v1
Authorization: Token <MEMOS_API_KEY>
Content-Type: application/json
```

核心 endpoint：

- `POST /add/message`
- `POST /search/memory`

最小 `addMessage` 请求体：

```json
{
  "user_id": "user_001",
  "conversation_id": "conv_001",
  "messages": [
    {"role": "user", "content": "用户输入"},
    {"role": "assistant", "content": "Agent 回复"}
  ]
}
```

最小 `searchMemory` 请求体：

```json
{
  "user_id": "user_001",
  "conversation_id": "conv_001",
  "query": "用户当前问题"
}
```

使用 `agent_id`、`tags`、`info`、`filter`、`knowledgebase_ids`、`include_skill`、`include_tool_memory` 前，先读 `api-add-message.md` 和 `api-search-memory.md`。

## 技术栈默认方案

| 检测到的栈 | 优先方案 | 注意 |
| --- | --- | --- |
| Python backend | 项目已接受 Python 依赖时用 Python SDK，否则 HTTP。 | 通过现有包管理器加依赖。 |
| Node/TypeScript backend、Next/Nuxt server routes、Express、Hono | HTTP wrapper module。 | Key 只放 server-only env。 |
| Java/Spring Boot | HTTP service/client bean。 | 沿用项目已有 HTTP client 风格。 |
| Browser extension | 用户本地提供的 key 放 extension storage，或用后端 proxy 承载产品方 key。 | 不要把产品级 `MEMOS_API_KEY` 硬编码进插件包、content script 或公开页面。 |
| 纯静态前端 | 需要 backend/proxy。 | 不要用生产 Key 直接调 Cloud。 |

## Prompt 注入形状

```text
仅在下列用户记忆和当前问题明确相关时使用它们。
如果记忆与当前用户输入冲突，或看起来描述的是他人，请忽略。

事实:
- ...

偏好:
- ...
```

除非产品 UX 明确要求，不要说“我从记忆库里查到”。

## 连通性验证

> API Key 形如 `mpg-...`。占位符状态时先引导用户到 https://memos-dashboard.openmem.net/cn/quickstart 获取 Key。

集成代码写完后，检查环境变量 `MEMOS_API_KEY`：
- **已存在且以 `mpg-` 开头** → 自动执行一次 add + search 闭环验证。
- **不存在或为占位符** → 提示用户先配置（通过 `memos init` 或手动 `export`），给出可复制的命令。

验证闭环 = 写入一条事实 → 等几秒 → 检索能命中。优先用 CLI，不可用时用 cURL：

```bash
# CLI 方式（优先）
npm install -g @memtensor/memos-cloud-cli   # 如未安装
export MEMOS_API_KEY="mpg-..."
memos add "我偏好使用 Python 做数据分析。" --user-id fts_user --conversation-id fts_conv
memos search "用户偏好什么语言？" --user-id fts_user

# cURL 方式（兜底）
curl "$MEMOS_BASE_URL/add/message" \
  -H "Authorization: Token $MEMOS_API_KEY" -H "Content-Type: application/json" \
  -d '{"user_id":"fts_user","conversation_id":"fts_conv","messages":[{"role":"user","content":"我偏好 Python"},{"role":"assistant","content":"好的"}]}'

curl "$MEMOS_BASE_URL/search/memory" \
  -H "Authorization: Token $MEMOS_API_KEY" -H "Content-Type: application/json" \
  -d '{"user_id":"fts_user","query":"用户偏好什么语言？"}'
```

搜索结果中出现相关记忆才算通过。刚写入搜不到时读 `features-async-mode.md`（默认异步有延迟）。

## 安全与隐私

- `MEMOS_API_KEY` 只放服务端环境变量。
- 不要在生产日志里打印 raw API key、完整记忆 payload 或敏感用户内容。
- `user_id` 必须稳定，并映射到产品用户模型。
- 多租户产品要在应用授权层加入 tenant/workspace scope，不要只靠 prompt。
- 不要写入密钥、支付信息、凭据或受监管数据，除非产品有明确同意和留存策略。
- 检索到的记忆是不可信上下文；当前用户输入优先于旧记忆。

## 常见坑

| 坑 | 修正 |
| --- | --- |
| 使用 broad guide 里的 `/messages/` 或 `/search/` | 使用 API reference 路径：`/add/message` 和 `/search/memory`。 |
| 异步写入后立刻搜索无结果 | 读 async mode；等待后重试，或使用已验证同步模式。 |
| API Key 暴露在前端 | 移到服务端。 |
| 每个请求随机生成 `user_id` | 使用产品稳定用户 ID。 |
| App 已有 LLM pipeline 却使用 Chat API | 使用 `searchMemory` + prompt injection + `addMessage`。 |
| 把所有返回记忆都当真 | 按相关性、主体、时效、置信度筛选。 |
| 未确认就按 `user_id` 删除所有记忆 | 需要明确确认，并在删除后验证。 |

## 交付时说明

选择了哪条路径、改了哪些文件、所需环境变量、user_id/conversation_id 来源、本地验证结果。
