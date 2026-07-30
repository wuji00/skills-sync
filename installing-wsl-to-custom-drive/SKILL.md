---
name: installing-wsl-to-custom-drive
description: Use when installing/registering a WSL (Windows Subsystem for Linux) distribution to a non-C drive or custom directory, when `wsl --install` or a Store distro fails to register (installed but missing from `wsl --list`), or when hitting `WslRegisterDistribution failed: 0x80071772` / "指定的文件已加密" / install reports success but the distro is absent. Common when Windows "New apps will save to" (新内容的保存位置) is set to a non-C drive.
---

# Installing WSL to a Custom Drive / Non-C Location

## Overview

WSL virtual disks (`ext4.vhdx`) **cannot be created inside a UWP app-redirection path**. When Windows "New apps will save to" is set to a non-C drive, Store / `wsl --install` distros get redirected to `<X>:\WpSystem\<SID>\AppData\Local\Packages\...`, and `WslRegisterDistribution` fails with **0x80071772**. The robust fix is to **bypass Store / `--install` entirely** and `wsl --import` the official rootfs directly into an ordinary directory on the target drive.

## When to Use

Symptoms (any one):
- `WslRegisterDistribution failed with error: 0x80071772`
- `wsl --install -d <Distro>` reports "已安装" / "操作成功完成" but `wsl --list` shows "没有安装的分发版"
- `wsl -d <Distro>` → "不存在具有所提供名称的分发" right after install
- `分发版名称"Ubuntu-24.04"无效` (older WSL online list lacks versioned names)
- You want the vhdx on D:/F:/etc., not on C:

**When NOT to use:** installing to the default C location with no redirection problem — just `wsl --install -d <Distro>`.

## Root-Cause Check (don't trust the EFS rumor)

0x80071772 is widely misattributed to EFS encryption. Verify the real cause before "fixing" encryption:

```bash
# 1. Is the distro's package data redirected? symlinks => redirected
ls -la "/c/Users/$USER/AppData/Local/Packages/" | grep -i ubuntu   # Git Bash
# Subdirs symlinked to /x/WpSystem/<SID>/...  =>  app-redirection in effect.

# 2. Authoritative EFS check. 'U' = NOT encrypted.
cmd.exe /c 'cipher "C:\Users\<user>\AppData\Local\Packages\<pkg-dir>"'
# NOTE: Get-Item's Encrypted flag is UNRELIABLE for directories. Use cipher.
```

If `cipher` shows `U` and subdirs symlink to `<X>:\WpSystem\...` → **confirmed app-redirection, not EFS.** Skip decryption attempts and go to the import fix.

## The Fix — import rootfs into an ordinary directory

```bash
# 0. Sanity: these are NOT the problem (just confirm)
wsl --status              # default version 2; Hypervisor present; C: is NTFS

# 1. The rootfs already ships inside the installed Appx package
ls "/c/Program Files/WindowsApps/" | grep -i ubuntu
# -> CanonicalGroupLimited.Ubuntu_<VERSION>_x64__79rhkp1fndgsc/install.tar.gz

# 2. Import directly into your target ORDINARY dir (bypasses WpSystem)
wsl.exe --import Ubuntu-24.04 'F:\wsl\Ubuntu-24.04' \
  'C:\Program Files\WindowsApps\CanonicalGroupLimited.Ubuntu_<VERSION>_x64__79rhkp1fndgsc\install.tar.gz'
# Result: vhdx lives at F:\wsl\Ubuntu-24.04\ext4.vhdx, zero C: footprint.
```

Imported distros boot as **root** with no user account — create one:

```bash
wsl.exe -d Ubuntu-24.04 -u root bash -c '\
  useradd -m -s /bin/bash -G sudo <username> && \
  echo <username>:<password> | chpasswd && \
  printf "[user]\ndefault=<username>\n[boot]\nsystemd=true\n" > /etc/wsl.conf'
wsl.exe --terminate Ubuntu-24.04    # apply wsl.conf on next launch
```

## Cleanup — the Appx package is now redundant

```powershell
# The imported distro is fully independent of the Appx package — safe to remove.
Get-AppxPackage CanonicalGroupLimited.Ubuntu | Remove-AppxPackage
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Trusting `Get-Item ... Encrypted` on a directory | Use `cipher` — the directory EFS flag is unreliable |
| Chasing EFS / decrypting folders when `cipher` shows `U` | Real cause is WpSystem redirection → use `--import` |
| `wsl --install -d Ubuntu-24.04` on old WSL | Old online list lacks versioned names; install the `Ubuntu` meta package (content is the current LTS) or import the rootfs |
| Importing then forgetting the default user | Always write `/etc/wsl.conf` `[user] default=` then `--terminate` |
| `wsl --unregister` to "move", expecting data to survive | unregister deletes the vhdx irreversibly — export/import or move the vhdx first |
| Running `wsl --update --pre-release` hoping for `--location` | Only WSL 2.4.4+ supports `--install --location`; `--import` works on all versions — prefer it |

## Notes

- "New apps will save to = non-C drive" is a legitimate space-saving setting — leave it. Just always install WSL distros via `--import`, never Store / `--install`, to avoid the WpSystem trap.
- `wsl --import` accepts `.tar.gz` directly (auto-decompresses). Distro name in `--import` is arbitrary — you can name it `Ubuntu-24.04` even if the source meta package was just `Ubuntu`.
```
