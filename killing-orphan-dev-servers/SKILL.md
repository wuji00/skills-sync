---
name: killing-orphan-dev-servers
description: Use when a dev server won't start because its port is already in use — "Port 3000 is in use by process <PID>", EADDRINUSE, "Another next/vite dev server is already running" — typically after stopping/killing a previous server whose child process (next/vite/node) became orphaned. Common on Windows where killing pnpm/npm/npx doesn't propagate to the child; also covers git-bash's /PID path-mangling trap and the Unix equivalents.
---

# Killing Orphaned Dev Servers

## Overview

You "stopped" a dev server (TaskStop, Ctrl-C on the wrapper, closed the terminal) but the **port stays occupied**: a child process (`next` / `vite` / `node`) was orphaned and is still listening. **Kill the orphan by its PID** — don't kill the wrapper again (it's already dead).

## When to Use

Any of these after you thought you stopped a dev server:

- `Port 3000 is in use by process <PID>` / `✓ Ready on port 3001 instead`
- `EADDRINUSE: address already in use :::3000`
- `Another next dev server is already running` (Next.js prints the PID)
- `pnpm dev` / `npm run dev` / `npx ...` exits immediately with a port conflict
- `localhost:3000` still responds after you stopped the server

**When NOT to use:** the port is held by a different app you actually want (a DB, another project). Pick another port instead of killing.

## The Fix

The error usually names the PID — kill **that** PID (the child), not the wrapper:

```bash
# Windows — cmd / PowerShell:
taskkill /PID <PID> /F

# Windows — git bash / MSYS2 (MUST block /PID → path conversion, else it silently no-ops):
MSYS_NO_PATHCONV=1 taskkill /PID <PID> /F

# macOS / Linux:
kill -9 <PID>
```

No PID in the error? Find it by port:

```bash
# Windows
netstat -ano | findstr :3000          # last column = PID   (git bash: | grep :3000)

# macOS / Linux
lsof -i :3000                         # or:  ss -ltnp 'sport = :3000'
```

Then kill the PID it returns.

## Why It Happens

`pnpm dev` / `npm run dev` / `npx next dev` launch the real server as a **child process**. Killing the parent (the wrapper) frequently fails to kill the child:

- **Windows** has no process-group cleanup → child is orphaned, keeps the port. (Most common.)
- **Unix** usually reaps children via process groups, but detached / `&`-backgrounded servers can still orphan.

The orphan usually isn't *broken* — dev servers hot-reload, so it may still serve the latest code; it's just unmanaged and blocking the port.

## Common Mistakes

| Mistake | Fix |
|---|---|
| `taskkill /PID 1234` in git bash silently does nothing | Prefix `MSYS_NO_PATHCONV=1` — git bash mangles `/PID` into a Unix path |
| Killing the `pnpm`/`npm` wrapper PID again | The wrapper is already dead; kill the **child** PID the error gave you |
| Assuming the port freed after Ctrl-C / TaskStop | Verify with `netstat` / `lsof` before restarting |
| Need to kill nested children too | `taskkill /PID <pid> /T /F` (`/T` = include children) on Windows |

## Prevention

Applies to any wrapper→child server (`npm run dev`, `npx next dev`, `vite`). Before starting / after stopping one, verify the port with `netstat -ano | grep :<port>` (Windows) / `lsof -i:<port>` (Unix) — don't assume Ctrl-C/TaskStop freed it. On Windows, kill the child PID (or `taskkill /T /F`), not the wrapper.

## Origin

Empirically verified 2026-07-24 — `TaskStop` on `pnpm dev` left `next` (PID 34656) orphaned on :3000; `MSYS_NO_PATHCONV=1 taskkill /PID 34656 /F` cleared it. Full writeup: the project's `docs/pitfalls/dev-server-orphan-process.md`.
