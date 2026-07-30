---
name: windows-env-quirks
description: Use on Windows when a shell command or hook outputs mojibake or lone surrogates (\udc80/\udc94) for non-ASCII text like Chinese/CJK, or when `python3` fails with "Python was not found; run without arguments to install from the Microsoft Store" and/or a plugin's python3 hook errors. Covers the Microsoft Store python3 stub and bash command-string non-ASCII corruption.
---

# Windows Environment Quirks (Claude Code)

Two Windows-specific gotchas that silently break Claude Code tooling. Both live in the shell/command-execution layer — NOT in your logic.

## When to Use
- Non-ASCII (Chinese/CJK/emoji) typed into a **bash command** comes out as mojibake, or Python shows lone surrogates like `\udc80` / `\udc94`.
- `python3` (but not `python`) fails with **"Python was not found; run without arguments to install from the Microsoft Store…"**.
- A plugin hook that calls `python3` (e.g. **hookify**) errors with the Store message or "non-blocking status code".
- Any `python3 …` hits a stub instead of real Python.

**Not for:** non-Windows machines; encoding problems inside source files (fix the file's encoding directly).

## Core Principle
The Windows command-execution layer corrupts non-ASCII bytes in **command strings**, and a Microsoft Store alias intercepts `python3`. So: keep non-ASCII off the command line, and make `python3` resolve to real Python. **Always verify with ASCII output (hex codepoints) — never eyeball Chinese in the terminal, which also mangles.**

---

## Pitfall 1 — Non-ASCII corrupts in bash command strings

**Symptom:** `printf '简要回答'` → mojibake; Chinese piped into Python shows `\udc80`/`\udc94`. Hand-typing `简` escapes is also unreliable (they get converted back to raw Chinese at composition time).

**Cause:** the command-execution/transmission layer mangles non-ASCII bytes before they reach the shell. Separately, Python's `sys.stdin` on Chinese-Windows defaults to **cp936/GBK**, not UTF-8 — so piping UTF-8 bytes into Python mangles too.

**Fix — build the text from integer codepoints so the command stays 100% ASCII:**
```bash
python -c "import json; s=''.join(chr(c) for c in (0x7b80,0x8981,0x56de,0x7b54)); print(json.dumps({'x':s}, ensure_ascii=True))"
# -> ASCII JSON {"x": "简要回答"} that survives ANY encoding
```
For hook payloads: write a UTF-8 file with the **Write** tool (it bypasses the shell entirely) and `cat` it from a pure-ASCII hook command.

**Verify by reading codepoints back as hex (ASCII output):**
```bash
python -c "import json,sys; d=json.load(open(sys.argv[1])); print([hex(ord(c)) for c in d['x']])"
# expect ['0x7b80','0x8981','0x56de','0x7b54'] -- never trust a visual check of the Chinese
```
When piping into Python, read `sys.stdin.buffer.read()` (raw bytes → UTF-8), not `sys.stdin`.

---

## Pitfall 2 — `python3` resolves to the Microsoft Store stub

**Symptom:** `python3 --version` prints *"Python was not found; run without arguments to install from the Microsoft Store…"* while `python --version` works fine.

**Cause:** real Python on Windows installs as `python.exe` only — there is no `python3.exe`. The Store's "App execution alias" drops a stub `python3` into `%LOCALAPPDATA%\Microsoft\WindowsApps`, so any tool calling bare `python3` (e.g. the **hookify** plugin's hooks) hits the stub and fails. Note: `python` and `python3` resolve differently on the same machine.

**Diagnose:**
```bash
which python3    # stub -> .../Microsoft/WindowsApps/python3 ; real -> .../python3.exe
which python     # the working interpreter (e.g. /e/code/python/env/python)
```

**Fix — copy the working `python.exe` to `python3.exe` in a directory already on PATH *before* WindowsApps (the venv dir is ideal: it's on PATH early and holds `python311.dll`):**
```bash
cp /e/code/python/env/python.exe /e/code/python/env/python3.exe
hash -r            # clear bash's command-resolution cache
python3 --version  # -> Python 3.x.x  (stub error gone)
```
Optional hardening: disable the Store alias — *Windows Settings → Apps → Advanced app settings → App execution aliases* → off for python.exe and python3.exe.

**Note:** some plugins ship their own probe-and-fallback shim and are unaffected — e.g. `security-guidance` uses `sg-python.sh`, which tries `python3`, falls through the stub on failure, and uses `python` / `py -3`.

**Caveat:** recreating the venv wipes the copied `python3.exe` — re-copy if `python3` breaks again.

---

## Common Mistakes
| Mistake | Fix |
|---|---|
| Eyeballing Chinese output to "verify" it | Terminal display mangles too — verify via hex codepoints (ASCII) |
| Putting raw Chinese in a hook's `command` string | Store Chinese in a UTF-8 file (Write tool); `cat` via an ASCII command |
| Testing plugin hooks without `CLAUDE_PLUGIN_ROOT` | Plugins use it for `sys.path` (`from core… import`) — set it, else a misleading "No module named 'core'" |
| Assuming `python3` == `python` on Windows | They resolve differently — always `which python3` |
| Editing a plugin's `hooks.json` to swap `python3`→`python` | Lost on plugin update — fix interpreter resolution instead |

## Quick Reference
- Mojibake / `\udcXX` in command output → build text via `chr(0xXXXX)`; verify with `[hex(ord(c)) …]`; pipe via `sys.stdin.buffer`.
- "Python was not found" (Store) → copy `python.exe` → `python3.exe` in a PATH dir before WindowsApps; `hash -r`.
- Plugin hook that needs `sys.path` → set `CLAUDE_PLUGIN_ROOT` when testing.
