---
name: output-driven-tasks
description: Use when writing the task instruction/prompt to hand to an AI or sub-agent (feature, bugfix, test, migration, docs, config) and the deliverable must be right the first time. Use when AI output is inconsistent, wrong-shaped, or the task needs repeated correction rounds; when acceptance criteria are vague ("make it work", "handle edge cases").
metadata:
  author: wuji00
---

# Output-Driven Tasks（输出驱动任务契约）

## Overview

派任务给 AI 之前，先写**输出契约**：把开放式"作文题"改写成"填空题"。契约 = 制品类型 + 输入/输出规格 + 副作用 + 验收标准 + 验证策略。AI 填内容，你定框框。（源自 ODD 方法论：先定义输出制品，再执行开发。）

## When to Use

- 给 AI / 子 agent 布置有交付物的开发任务：新功能、修 bug、写测试、写迁移、写文档、改配置
- AI 输出形状不对、质量不稳定、反复返工
- 任务验收标准含糊（"做完就行""处理好边界情况"）

**不用**：纯问答、探索性调研（无交付物）、闲聊。

**与既有 skill 的分工**：项目/功能级规格 → `spec-driven-development`；会话级上下文配置 → `context-engineering`；本 skill 只管**单次任务的输出契约**。

## Core Pattern

**作文题（bad）**："新增一个用户注册接口。"
**填空题（good）**：按下方契约模板写——字段、副作用、验收标准全部框死。

## Quick Reference：任务契约模板

```jsonc
{
  "artifact_type": "code / db / config / doc / test / ...", // 制品类型 → 决定验证策略
  "input_spec":  [{"name": "username", "type": "string", "required": true}],
  "output_spec": [{"name": "user_id", "type": "uuid"}],
  "side_effects": ["写入 users 表", "发送欢迎邮件（失败不阻塞）"], // 显式声明，防 AI 悄悄改动契约外的东西
  "preconditions":  ["users 表存在", "SMTP 已配置"],
  "postconditions": [],
  "acceptance_criteria": [
    "Given 邮箱 x@y.com 已存在 When 调用 POST /register Then 返回 409 + error_code=EMAIL_EXISTS"
  ],
  "test_strategy": "test"
}
```

## 验收标准写法：Given-When-Then，可机器验证

- 结构：**具体输入 → 具体行为 → 具体输出/状态断言**
- bad："功能正常""测试通过就行""处理好边界情况"
- good："Given 用户存在 When 用错误密码调用登录 Then 返回 401 且不更新 last_login_at"

## 验证策略对照

| 策略 | 适用制品 | 怎么验 |
|------|----------|--------|
| compile | 代码 | 编译 / 类型检查通过 |
| execute | 函数 / 脚本 | 真实运行冒烟 |
| test | 代码 | 测试套件全绿 |
| review | 文档 / 设计 / 配置 | 人工评审 + 检查清单 |
| effect | 行为制品（状态迁移、消息发出） | 执行前后状态对比 |

## 完整派活示例（注册接口，可直接照此形状）

```text
制品类型: code（FastAPI 路由 + 用户服务）
输入: {username: string≤32, email: string(邮箱格式), password: string≥8}
输出: 201 + {user_id: uuid}；重复邮箱 → 409 + {error_code: "EMAIL_EXISTS"}
副作用: 写入 users 表；发欢迎邮件（失败仅记日志，不阻塞）；审计日志新增一条
前置条件: users 表已迁移；密码哈希库已安装
验收标准:
  Given 邮箱 a@b.com 已注册 When POST /register {email: a@b.com, ...}
    Then 409 + EMAIL_EXISTS，不写库
  Given 合法新邮箱 When POST /register 合法参数
    Then 201 + user_id，users 表新增一行且密码为哈希
验证策略: test（pytest 覆盖上述场景）
```

## 上下文注入时机（配合 context-engineering）

分层给，别一次全塞：
1. 项目约定 / 技术栈（CLAUDE.md 级别）→ 2. 契约本体（任务规格 + 验收标准）→ 3. 依赖信息按需 → 4. 修正反馈（**只在返工时给**，别把上次的失败当新任务的默认上下文）

## Common Mistakes

1. 只写需求描述、不写契约 → AI 自由发挥，形状不可控
2. 无验收标准 → 无法判断完成；"汇报"不等于"验收"
3. 副作用不声明 → AI 改了契约外的文件 / 状态
4. 一次塞全部上下文 → 重点丢失；按上面时机分层注入
5. 验收标准用形容词（好 / 快 / 干净）→ 不可验证，必须是具体断言
