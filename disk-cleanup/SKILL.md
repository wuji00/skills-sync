---
name: disk-cleanup
description: Use when user wants to clean up C drive disk space, free up storage, or analyze disk usage on Windows
---

# Disk Cleanup

C 盘空间清理技能，针对 Windows 开发环境。

## 核心原则

- **所有 PowerShell 命令必须写入 `.ps1` 临时文件后再执行**，严禁直接在 Bash 中拼接复杂 PowerShell 命令（`$` 变量、引号、管道等极易被 bash 转义破坏）。
- 优先扫描再清理，让用户知情。
- 区分「可直接执行」「需确认」「不能动」三类操作。

## 扫描流程

1. 用 PowerShell 脚本扫描顶层目录大小（>100MB 才显示）
2. 对大户目录（AppData、Windows、Program Files）逐层下钻
3. 检查临时文件、回收站、更新缓存等常见空间浪费
4. 汇总报告，标注每项能否清理

扫描脚本模板（写入临时 `.ps1` 文件再执行）：

```powershell
$threshold = 100MB
$dirs = Get-ChildItem 'TARGET_PATH' -Directory -Force -ErrorAction SilentlyContinue
$results = @()
foreach ($d in $dirs) {
    $size = (Get-ChildItem $d.FullName -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
    if ($size -gt $threshold) {
        $results += [PSCustomObject]@{Name=$d.Name; SizeGB=[math]::Round($size/1GB,2)}
    }
}
$results | Sort-Object SizeGB -Descending | Format-Table -AutoSize
```

## 安全清理项（可直接执行）

| 项目 | 命令/路径 | 典型释放 |
|------|-----------|----------|
| uv 缓存 | `uv cache clean` | 1-7 GB |
| Go 编译缓存 | `go clean -cache` | 0.3-2 GB |
| pip 缓存 | `pip cache purge` | 0.5-3 GB |
| npm 缓存 | `npm cache clean --force` | 0.5-2 GB |
| **pnpm 缓存** | 删 `AppData\Local\pnpm-cache` + 运行 `pnpm store prune` | 0.2-2 GB |
| **VS Code 缓存** | 删除 `Code\CachedExtensionVSIXs`、`Code\WebStorage`、`Code\Crashpad`、`Code\CachedData` | 0.5-3 GB |
| **WeGame 缓存** | 删除 `AppData\Roaming\Tencent\WeGame\qbcore*`、`qblink_update_x64` | 0.3-1 GB |
| 软件更新包 | 删除 `AppData\Local\*-updater\` 中的 installer.exe / pending / .zip / .nupkg | 1-3 GB |
| NVIDIA 着色器缓存 | 删除 `AppData\LocalLow\NVIDIA\` 内容 | 1-3 GB |
| Windows 更新下载缓存 | 删 `C:\Windows\SoftwareDistribution\Download\*` | 0.5-2 GB |
| Chrome 缓存 | `Chrome 设置 → 隐私和安全 → 清除浏览数据` 或删 `User Data\Default\Cache` | 0.3-1 GB |
| 用户 Temp | 删 `%TEMP%` 中 7 天以上文件 | 0.1-1 GB |

### Electron 应用残留（重点！）

很多 AI IDE / 工具卸载后不会清理 `AppData\Roaming`，是 C 盘空间的隐形黑洞。典型受害者：

- ** Windsurf / Trae / Kiro / Cursor / Qoder** 等
- 检查方法：看本地 `AppData\Local\Programs\xxx` 是否还存在
- 若主程序已不存在，可直接删除对应的 Roaming 目录
- 重点关注子目录：`CachedExtensionVSIXs`、`SharedClientCache`、`WebStorage`

## 需用户确认的清理项

| 项目 | 路径 | 操作建议 |
|------|------|----------|
| 飞书缓存 | `AppData\Roaming\LarkShell\` | 在飞书设置中清理，不直接删 |
| **微信聊天文件** | `C:\Users\<user>\xwechat_files` | **迁移方案**：`robocopy` 复制到 D 盘，退出微信后删 C 盘原目录，再建 junction 回源路径 |
| Chrome 缓存 | `AppData\Local\Google\` | Chrome 设置→清理浏览数据 |
| **AI IDE 冗余** | Kiro/Windsurf/Cursor/Trae/Qoder 等 | 检查本地安装 + Roaming 残留；建议只保留 1-2 个 |
| **JetBrains 旧版本** | `AppData\Local\JetBrains\IntelliJIdea20xx.x` | 旧版本 IDE 和 Toolbox 下载缓存可安全删除 |
| Docker | `Program Files\Docker\` + WSL 镜像 | 不用可卸载；WSL 发行版用 `wsl --unregister docker-desktop` |
| Windows 组件清理 | `Dism /Online /Cleanup-Image /StartComponentCleanup` | 需管理员权限，清理后无法回滚旧补丁 |

### 微信 `xwechat_files` 迁移

> ⚠️ 不要用"robocopy 后直接删源"的朴素脚本——目标若有旧残留，文件数不一致时删源会丢数据。
> 完整带**独立文件数校验**的迁移方案见 Skill **`windows-file-migration`**（含可复用校验脚本 + junction 回链）。

## 不能动的目录

- `Windows\System32` — 系统核心
- `Windows\Installer` — 安装修补所需
- `Windows\WinSxS` — 不可手动删除，可用 Dism 清理
- `ProgramData` — 应用程序运行时数据

## 实战技巧

1. **Electron Updater 垃圾**：`AppData\Local\` 下任何带 `-updater` 的目录都值得检查，常藏数百 MB 到数 GB 的安装包。
2. **JetBrains 多版本并存**：Toolbox 会在 Local 和 Roaming 各留一份旧版本缓存，卸载旧 IDE 后手动删除可释放数 GB。
3. **Dism 执行方式**：由于 bash 找不到 `Dism.exe`，应通过 PowerShell 调用：
   ```powershell
   Start-Process -FilePath 'Dism.exe' -ArgumentList '/Online','/Cleanup-Image','/StartComponentCleanup' -Verb RunAs -Wait
   ```
4. **微信必须完全退出**：迁移 `xwechat_files` 前，务必在任务管理器结束所有 `WeChat.exe` 和 `xwechat.exe` 进程，否则 `.mmap`、`.db` 文件被锁定无法移动。
