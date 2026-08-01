---
name: windows-file-migration
description: Use when migrating a large directory to another drive on Windows via robocopy + junction (WeChat xwechat_files / WeChat data, IDE caches, game files), especially when destination file count is greater than source, or before deleting source after robocopy. Covers robocopy merge-not-delete semantics, independent verification, and junction re-link.
metadata:
  author: wuji00
---

# Windows 大目录迁移（robocopy + junction 回链）

## 何时用

- 把 `C:\Users\<u>\xwechat_files`（微信）/ IDE 数据 / 大目录迁到 D 盘 + junction 回链
- robocopy 后**目标文件数 > 源**（校验失败）
- 删源目录前要确认数据真的一致

## 根因：robocopy 默认合并，不删目标多余文件

robocopy 默认**合并/覆盖**，不删目标里源中没有的文件（除非 `/MIR`）。若目标路径早有旧残留：

```
src:  12298 files          ← C 盘真实活跃数据
dest: 37881 files          ← D 盘目标含 4 月份旧残留，远大于源
ABORT: file count mismatch
```

dest = 旧残留 ∪ 新数据。**危险**：若脚本没独立校验、盲目信"robocopy 成功 = 一致"，会在数据不一致下删 C 盘源，junction 指向新旧混合/损坏目录。

robocopy 返回码 `<8` 即视为复制成功，但"成功"只代表复制无错，**不代表源=目标**。

## 解决：换干净新目标路径

路径名不影响微信——微信只认 C 盘原路径，junction 指哪它访问哪，目标目录叫什么无所谓。

```powershell
$dest = 'D:\WeChatData'   # 干净新路径，别复用可能含残留的旧目标
robocopy $src $dest /E /Z /XO /R:3 /W:5 /MT:8 /NFL /NDL
```

## 预防（必做）

1. **迁前探测目标路径是否已存在**。已存在且非空 → 换新路径或先清空（确认无用），绝不在不知情下让 robocopy 合并。
2. **脚本必须有独立校验，不能只看 robocopy 返回码**。用 `(Get-ChildItem -Recurse -File).Count` 对比文件数 + 总字节数，**不一致必须中止且保留源**。
3. **删源前再确认 junction 已建好**（`Test-Path $src` 为真），否则源删了链接没建 = 数据丢失。删源与建链之间失败要有兜底。
4. **校验源不是 reparse point** 再开始：若源已是 junction（之前迁过），直接跳过。
5. **进程检查**：迁前确认目标程序（`xwechat.exe`/`WeChat.exe`/`WeChatAppEx.exe` 等）全退出，否则 `.db`/`.mmap` 被锁，复制到不一致状态。
6. `/MIR` 镜像模式可让目标严格等于源（自动删多余），但**破坏性**——仅确认目标旧数据确实无用时才用，否则优先"换干净新路径"这种零风险方案。

## 可复用脚本（带完整校验）

```powershell
$ErrorActionPreference = 'Stop'
$src  = 'C:\Users\18435\xwechat_files'
$dest = 'D:\WeChatData'   # 干净新路径

if (@(Get-Process xwechat,WeChat,WeChatAppEx -ErrorAction SilentlyContinue).Count) { throw "WeChat still running" }
if ((Get-Item $src -Force).Attributes -match 'ReparsePoint') { return }   # 已迁过

robocopy $src $dest /E /Z /XO /R:3 /W:5 /MT:8 /NFL /NDL /NJH /NJS
if ($LASTEXITCODE -ge 8) { throw "robocopy failed rc=$LASTEXITCODE" }

# 独立校验：文件数必须一致，否则中止保留源
$srcCount  = @(Get-ChildItem $src  -Recurse -File -Force -ErrorAction SilentlyContinue).Count
$destCount = @(Get-ChildItem $dest -Recurse -File -Force -ErrorAction SilentlyContinue).Count
if ($srcCount -ne $destCount) { throw "mismatch $srcCount vs $destCount, source kept" }

Remove-Item $src -Recurse -Force
cmd /c mklink /J "$src" "$dest" | Out-Null
if (-not (Test-Path $src)) { throw "junction failed, source already removed!" }
```

关键词：robocopy mismatch、file count mismatch、`/MIR`、reparse point、junction、`mklink /J`、xwechat_files 迁移、C 盘清理。
