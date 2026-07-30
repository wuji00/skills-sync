---
name: auto-proxy-fallback
description: |
  Use when network requests fail with timeout, connection refused, ECONNREFUSED,
  ETIMEDOUT, ENETUNREACH, or "unable to access" errors. Auto-detects local proxy
  ports (10808, 7890) and configures environment + tool-specific proxy settings.
argument-hint: "[optional: error message or failed command]"
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - AskUserQuestion
---

# Auto Proxy Fallback

Network requests fail when a local proxy (VPN/clash/v2ray) is running but environment
variables are not set. This skill detects proxy-related failures and configures proxy
settings automatically.

## When to Use

- Any `curl`, `git`, `npm`, `npx`, `pip` command fails with connection errors
- Error messages containing: `ECONNREFUSED`, `ETIMEDOUT`, `ENETUNREACH`, `Connection timed out`, `Could not resolve host`, `unable to access`
- `gh` (GitHub CLI) fails with authentication or connection errors
- Any "network unreachable" or "name resolution" error

## Quick Fix (Manual)

If you just need to fix it now:

```bash
# Probe ports and set proxy
for PORT in 10808 7890; do
  if curl -s --connect-timeout 2 http://127.0.0.1:$PORT >/dev/null 2>&1; then
    export HTTP_PROXY="http://127.0.0.1:$PORT"
    export HTTPS_PROXY="http://127.0.0.1:$PORT"
    export http_proxy="http://127.0.0.1:$PORT"
    export https_proxy="http://127.0.0.1:$PORT"
    echo "Proxy set to 127.0.0.1:$PORT"
    break
  fi
done
```

## Full Diagnostic & Fix Workflow

### Step 1: Identify the Failure

Check the error output from the failed command. Match against these patterns:

| Error Pattern | Likely Cause | Action |
|--------------|-------------|--------|
| `ECONNREFUSED` / `Connection refused` | Target server unreachable, possibly needs proxy | Probe proxy ports |
| `ETIMEDOUT` / `Connection timed out` | Network blocked by firewall/GFW | Set proxy |
| `ENETUNREACH` / `Network is unreachable` | No route to host, DNS issue | Set proxy + check DNS |
| `Could not resolve host` | DNS blocked/failed | Set proxy (proxy handles DNS) |
| `SSL certificate problem` | Proxy MITM or cert issue | Different issue, don't set proxy |
| `HTTP 403/407` | Auth required | Proxy auth needed |

### Step 2: Probe Local Proxy Ports

Test common proxy ports in order:

```bash
PROXY_PORT=""
for PORT in 10808 7890; do
  if curl -s --connect-timeout 2 http://127.0.0.1:$PORT >/dev/null 2>&1; then
    PROXY_PORT=$PORT
    echo "Found active proxy on port $PORT"
    break
  fi
done

if [ -z "$PROXY_PORT" ]; then
  echo "No local proxy detected on ports 10808 or 7890"
  echo "Ask user to start their proxy (Clash/V2Ray/Xray) or check port"
fi
```

### Step 3: Set Environment Variables

When a proxy port is found:

```bash
export HTTP_PROXY="http://127.0.0.1:$PROXY_PORT"
export HTTPS_PROXY="http://127.0.0.1:$PROXY_PORT"
export http_proxy="http://127.0.0.1:$PROXY_PORT"
export https_proxy="http://127.0.0.1:$PROXY_PORT"
export NO_PROXY="localhost,127.0.0.1,0.0.0.0,::1"
export no_proxy="localhost,127.0.0.1,0.0.0.0,::1"
```

**Why both uppercase and lowercase?** Some tools (curl, wget) read lowercase, others (Node.js, Python) read uppercase. Set both for maximum compatibility.

### Step 4: Configure Tool-Specific Proxy

Different tools read proxy from different places. Set as needed:

#### Git

```bash
git config --global http.proxy "http://127.0.0.1:$PROXY_PORT"
git config --global https.proxy "http://127.0.0.1:$PROXY_PORT"
```

To remove later:
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

#### npm

```bash
npm config set proxy "http://127.0.0.1:$PROXY_PORT"
npm config set https-proxy "http://127.0.0.1:$PROXY_PORT"
```

To remove later:
```bash
npm config delete proxy
npm config delete https-proxy
```

#### pip (Python)

```bash
export PIP_PROXY="http://127.0.0.1:$PROXY_PORT"
```

Or pass inline: `pip install --proxy http://127.0.0.1:$PROXY_PORT <package>`

### Step 5: Retry the Failed Command

Re-run the original failed command. If it still fails:

1. Check if proxy is actually working: `curl -s --connect-timeout 5 https://www.google.com -o /dev/null -w "%{http_code}"`
2. If returns `200`, proxy works - the issue is elsewhere
3. If returns `000` or error, proxy itself is not routing correctly - ask user

## Cleanup (After Session)

The `export` commands only affect the current shell session. When the session ends,
proxy settings are gone. No cleanup needed for environment variables.

For git/npm config changes (Step 4), those persist. Remove them when done:

```bash
# Remove git proxy
git config --global --unset http.proxy 2>/dev/null
git config --global --unset https.proxy 2>/dev/null

# Remove npm proxy
npm config delete proxy 2>/dev/null
npm config delete https-proxy 2>/dev/null
```

## Common Ports Reference

| Port | Common Software | Protocol |
|------|----------------|----------|
| 10808 | V2Ray / Xray | SOCKS5/HTTP |
| 10809 | V2Ray (HTTP) | HTTP |
| 7890 | Clash | HTTP |
| 7891 | Clash (SOCKS5) | SOCKS5 |
| 1080 | Generic SOCKS | SOCKS5 |
| 8080 | Generic HTTP proxy | HTTP |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Proxy port found but still can't connect | Proxy may not be routing - check proxy software is in "system proxy" or "TUN" mode |
| Works in browser but not CLI | Browser uses system proxy, CLI needs env vars - this skill fixes that |
| `git clone` still fails after setting env | Git needs its own config - run Step 4 git section |
| `npx` / `npm install` still fails | npm needs its own config - run Step 4 npm section |
| Port 10808 is SOCKS5 not HTTP | Try `socks5://127.0.0.1:10808` or use port 10809 (HTTP) |
