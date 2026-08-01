---
name: lobehub-market-register
description: Use when `npx @lobehub/market-cli register` fails with HTTP 500 / registration_failed, or `skills install` fails with "No credentials found. Run lhm register first". Server-side bug; bypass register via the public /download endpoint.
metadata:
  author: wuji00
---

# LobeHub market-cli register 500 绕过

## 何时用

按 LobeHub 文档装 skill 时，第一步 `register` 就失败：

```bash
npx -y @lobehub/market-cli register --name "xxx" --source claude-code
# Request error: {"error":"registration_failed","error_description":"Failed to register client"}
# Assertion failed: !(handle->flags & UV_HANDLE_CLOSING), file src\win\async.c, line 76   (exit 127)
```

随后 `skills install <id>` 也失败：

```
No credentials found. Run `lhm register` first or set MARKET_CLIENT_ID and MARKET_CLIENT_SECRET.
```

## 根因（有依据）

**服务端 bug，不是客户端参数问题。** curl 复现 register：

```bash
curl -sS -i -X POST "https://market.lobehub.com/api/v1/clients/register" \
  -H "Content-Type: application/json" \
  -d '{"clientName":"any-name","clientType":"cli","source":"claude-code","version":"0.0.38"}'
# => HTTP/2 500  {"error":"registration_failed",...}
# => ratelimit-remaining: 4            (不是限流)
# => x-matched-path: /[[...route]]     (Vercel catch-all 路由抛未捕获异常)
```

- `register` → `sdk.auth.registerClient()` → `POST /v1/clients/register`
- `--source` 合法取值含 `claude-code`（帮助文本就举例它），**不是 source 的问题**
- 那条 `UV_HANDLE_CLOSING` 断言是进程出错后 libuv 在 Win 清理时的二次崩溃，**不是根因**，忽略

## 解决：绕过 register，直连公开 /download 端点

`skills install` 要求 register 的**唯一**原因是 `createSDK3()` 顶部的凭证门；而真正下载用的端点**公开免鉴权**：

```bash
# 验证：download 端点不要 auth 也返回正版 zip
curl -sS -D - -o skill.zip "https://market.lobehub.com/api/v1/skills/<identifier>/download"
# => HTTP/2 200, content-type: application/zip, 首字节 50 4b 03 04 (PK 魔数)
```

等价于文档安装（同源、同包、同布局，仅省市场账号）：

```bash
ZIP="C:/Users/<you>/AppData/Local/Temp/<id>.zip"
DEST="C:/Users/<you>/.claude/skills/<id>"      # claude-code 全局；项目级用项目 .claude/skills
curl -sS -L -o "$ZIP" "https://market.lobehub.com/api/v1/skills/<id>/download"
PYTHONUTF8=1 python -c "import zipfile,os; z=zipfile.ZipFile(r'$ZIP'); os.makedirs(r'$DEST',exist_ok=True); z.extractall(r'$DEST')"
```

> ⚠ lobehub CLI 的"全局"语义和 Claude Code 不一致：`--global` 装到 `~/.agents/skills/`（Claude Code 不扫描）。Claude Code 全局必须显式 `--dir ~/.claude/skills`，或像上面直接解压到 `~/.claude/skills/<id>/`。

## 取舍

- 等价安装，**不影响 skill 使用**
- 仅丢市场账号身份 → 不能 `skills rate` / `skills comment`。需要时等 register 服务端修复后补注册
- download 限流 `3;w=60`（每 60 秒 3 次），不要密集拉

## 预防 / 快速判断

装 lobehub skill 前先探 register 是否健康：

```bash
curl -sS -o /dev/null -w "%{http_code}\n" -X POST "https://market.lobehub.com/api/v1/clients/register" \
  -H "Content-Type: application/json" -d '{}'
# 500 → 服务端挂着，走 download 绕过；400/422 → 服务端正常，按文档 register
```

关键词：lobehub register 500、registration_failed、Failed to register client、No credentials found、MARKET_CLIENT_ID、UV_HANDLE_CLOSING、skills install 失败、market-cli。

相关：Win 上 `npx skills add` 的 symlink 问题见 [[windows-link-quirks]]。
