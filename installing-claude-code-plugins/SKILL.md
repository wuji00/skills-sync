---
name: installing-claude-code-plugins
description: Use when `claude plugin marketplace add` fails with EPERM rename error on Windows, when an installed plugin shows in `claude plugin list` but its slash command does not respond, or when the plugin cache directory is missing SKILL.md / hooks.json files after a sparse-checkout install.
---

# Installing Claude Code Plugins (Windows Workarounds)

## Overview

When the standard `claude plugin marketplace add` / `install` flow fails or installs an empty shell on Windows, the CLI cannot self-recover. This skill teaches two bypass strategies and one mandatory verification step that catches silent partial installs.

## When to Use

- `claude plugin marketplace add <owner/repo>` returns `EPERM rename ... temp_xxx -> <name>` on Windows.
- `claude plugin install <plugin>@<marketplace>` returns `EPERM rename ... temp_local_xxx -> cache/.../<version>` on Windows.
- `claude plugin list` shows plugin enabled, but `/<command>` produces no response.
- Cache dir at `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` is missing `skills/`, `hooks/`, or other directories.
- You used `--sparse .claude-plugin plugins` and the install succeeded — but the plugin doesn't actually work.

## Strategy 1: Use `update` if marketplace already exists

If the error indicates the marketplace **already exists** in `~/.claude/plugins/known_marketplaces.json`, skip `add` entirely:

```bash
claude plugin marketplace update <marketplace-name>
claude plugin install <plugin>@<marketplace> --scope user
```

**Why this works**: `update` performs the same clone + cache-refresh as `add`, but skips the rename step that triggers the Windows EPERM race condition. Baseline-tested: `claude-mem@thedotmack` upgraded 13.11.0 → 13.12.2 in one shot after `add` failed twice.

## Strategy 2: Manual clone + patch (first-install path)

If first install (no prior version in `known_marketplaces.json`):

```bash
# 1. Clone manually to the path the CLI expects
git clone https://github.com/<owner>/<repo>.git \
  ~/.claude/plugins/marketplaces/<repo>

# 2. Register in known_marketplaces.json (use any existing entry as template)
{
  "<repo>": {
    "source": { "source": "github", "repo": "<owner>/<repo>" },
    "installLocation": "C:\\Users\\<user>\\.claude\\plugins\\marketplaces\\<repo>",
    "lastUpdated": "<ISO timestamp>"
  }
}

# 3. Run install — CLI now reads from local marketplace
claude plugin install <plugin>@<repo>
```

## Strategy 3: Recover from mid-install EPERM

If `install` itself fails with EPERM during the cache rename (the clone succeeded, but copying `temp_local_xxx/ -> cache/<marketplace>/<plugin>/<version>/` was blocked by Windows):

```bash
# 1. Locate the orphaned temp dir
ls ~/.claude/plugins/cache/temp_local_*/  # note the actual temp name from the error

# 2. Manually copy it to the expected cache path
cp -r ~/.claude/plugins/cache/temp_local_<id>/. \
  ~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/

# 3. Delete the temp dir
rm -rf ~/.claude/plugins/cache/temp_local_<id>

# 4. Patch installed_plugins.json (CLI never registered it because install errored mid-flight)
{
  "plugins": {
    "<plugin>@<marketplace>": [
      {
        "scope": "user",
        "installPath": "C:\\Users\\<user>\\.claude\\plugins\\cache\\<marketplace>\\<plugin>\\<version>",
        "version": "<version>",
        "installedAt": "<ISO timestamp>",
        "lastUpdated": "<ISO timestamp>"
      }
    ]
  }
}

# 5. Run the verification (next section)
```

**Why this happens**: `install` does its own temp-dir + rename dance to copy files into the cache. Same Windows file-lock race as `add`. Discovered in REFACTOR test when the install step on a manually-patched marketplace hit the rename error.

## Mandatory Verification

After **every** plugin install — including Strategy 1, 2, and 3 — run:

```bash
find ~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/ \
  -name "SKILL.md" -o -name "hooks.json"
```

**Both must be present**. If only `plugin.json` exists, you have an empty shell — the slash command will silently fail.

If verification fails, **immediately** invoke Strategy 3 to repair.

## Common Mistakes

| Mistake | Why it fails | Fix |
|---|---|---|
| `--sparse .claude-plugin plugins` | `plugin.json` is at `.claude-plugin/`, but plugin **content** lives at `skills/` and `hooks/` | Always include `skills hooks` in sparse paths, or skip sparse entirely |
| Retrying `add` after EPERM | Windows file lock race condition; retry does not clear it | Switch to Strategy 1 (`update`) or Strategy 2 (manual clone) |
| Only patching `known_marketplaces.json` | `install` separately maintains `installed_plugins.json`; both are needed | After Strategy 3, patch **both** registry files |
| Trusting `claude plugin list` success | CLI success ≠ content complete (sparse-checkout or mid-install EPERM both report success or partial state) | Always run the `find` verification |
| Editing `known_marketplaces.json` with wrong schema | Install rejects the malformed entry | Copy an existing entry verbatim; only change `source`, `installLocation`, `lastUpdated` |

## When NOT to Use

- **macOS / Linux**: `marketplace add` works reliably; no workaround needed.
- **Non-plugin installs** (skills, hooks, MCP servers) — different commands apply.
- **Already-installed plugin needs update**: just `marketplace update <name>` + `install <plugin>@<marketplace>`.