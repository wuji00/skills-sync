---
name: appsec-scanning
description: Use when running security checks before merge/release, gating CI on vulnerabilities, scanning a new dependency or container image, or auditing a repo for known CVEs, secret leaks, or code-level flaws. Triggers include "security scan", "vulnerability scan", "is this safe to ship", SAST, DAST, dependency audit, CVE check, pre-release security gate, "scan this image".
---

# AppSec Scanning Pipeline

## Overview
Three open-source scanners forming one AppSec pipeline, run in order. **Cross-language** — work on any stack. They catch **disjoint** bug classes, so run all three.

1. **Semgrep** — SAST: scan **source** for code-level flaws (injection, broken auth, hardcoded secrets)
2. **OWASP ZAP** — DAST: scan the **running app** for runtime/web vulns (XSS, misconfig, headers)
3. **Trivy** — dependency + container image + IaC: known CVEs in libs/images/configs

SAST reads code, DAST hits the live server, Trivy checks what you shipped.

## When to Use
- Pre-merge / pre-release security gate
- Periodic security sweep
- New dependency added (Trivy)
- Container image before push (Trivy)
- "Is this safe to ship?"

## Pipeline (run in this order)

### 1. SAST — Semgrep (on source)
```bash
# p/default = maintained baseline; add focused packs
semgrep ci --config p/default --config p/owasp --config p/secrets
# JSON output for CI parsing
semgrep ci --config p/default --json --output results.json
```
- Fast, no build needed
- Custom rules: `--config custom-rules.yml`
- **Exclude paths** (generated code, vendor, dist): `--exclude "dist,build,vendor"` or a `.semgrepignore` file (gitignore-style)
- Suppress a false positive inline with `# nosemgrep` **+ a comment explaining why**

### 2. DAST — OWASP ZAP (on running app)
Point at a running **staging** instance. Never active-scan prod without explicit authorization.

Quick passive scan (still works in 2.x):
```bash
zap-baseline.py -t https://staging.example.com -J report_json
```

**Authenticated scanning** (login-gated apps — the common case) uses the **Automation Framework** with a context + login:
```yaml
# zap.yaml → run: zap.sh -cmd -autorun zap.yaml
env:
  contexts:
    - name: app
      urls: ["https://staging.example.com"]
      includePaths: ["https://staging.example.com/.*"]
      authentication:
        method: 'form'                       # or 'http', 'script'
        loginRequestUrl: 'https://staging.example.com/login'
        loginRequestBody: 'user={%env:USER%}&pass={%env:PASS%}'
      sessionManagement: { method: 'cookie' }
      verification: { loggedInRegex: 'logout', loggedOutRegex: 'login' }
jobs:
  - type: spider                # crawl authenticated surface first
    parameters: { context: app }
  - type: activeScan            # sends payloads — staging only
    parameters: { context: app }
  - type: report
    parameters: { template: 'traditional-html', reportFile: 'zap-report' }
```
Without authentication ZAP only sees the unauthenticated surface. Tune `loggedInRegex`/`loggedOutRegex` to a string present only when logged in/out.

### 3. Dependency + Container + IaC — Trivy
```bash
trivy fs .                          # source deps — needs lockfiles: package-lock.json / Poetry.lock / go.sum / Gemfile.lock
trivy image myapp:latest            # container image — separate command
trivy fs --scanners misconfig .     # IaC/misconfig (Dockerfile, k8s, TF); 'iac' folded into 'misconfig' ≥0.37
# Gate: fail only on FIXABLE HIGH/CRITICAL
trivy fs . --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1
```
**Suppress one accepted CVE** (not all of them): put the CVE-ID on its own line in `.trivyignore`, then `trivy fs . --ignorefile .trivyignore`. Add a comment + ticket next to each line.

## CI Integration (GitHub Actions)
Chain SAST → dep scan in one job; each fails on its own gate. ZAP runs as a separate job once staging is deployed.
```yaml
  static-and-deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install semgrep && semgrep ci --config p/default --error   # --error = fail on findings
      - name: Install Trivy
        run: curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh
      - run: ./bin/trivy fs . --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1
      - run: ./bin/trivy image app:latest --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1

  zap-dast:                       # only when staging is live
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - run: docker run -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t "$STAGING_URL" -J zap-report
        env: { STAGING_URL: ${{ secrets.STAGING_URL }} }
```
`semgrep --error` and Trivy `--exit-code 1` make findings fail the step automatically.

## CI Gate Logic
Fail the build on **fixable** HIGH/CRITICAL. Track the rest.

| Severity | Default action |
|----------|----------------|
| CRITICAL (fixable) | block |
| HIGH (fixable) | block |
| MEDIUM / LOW | track, don't block |
| Unfixed (no patch exists) | accept risk + document |

Document every accepted risk in `.trivyignore` / `.zapignore` / `# nosemgrep` with a comment and a ticket. **Never silently disable** a finding — silent suppression is untracked security debt.

## Common Mistakes
- **Active-scan production**: ZAP active sends attack payloads. Staging-only, with authorization.
- **Block on all severities**: noise drowns signal. Gate on fixable HIGH/CRITICAL.
- **`--ignore-unfixed` used carelessly**: forgetting it = wall of unfixable CVEs blocks everything; always-on = hides real risk on patched-but-deployed-old images. Decide deliberately.
- **Scan a stale base image**: rebuild first, or scan the actual image you'll ship, not old cached layers.
- **Silent suppression**: `# nosemgrep` / ignore files without a comment + ticket.
- **SAST-only or DAST-only**: they catch different bug classes. The pipeline is all three.

## Quick Reference
| Tool | Scope | Command | Gate signal |
|------|-------|---------|-------------|
| Semgrep | source (SAST) | `semgrep ci --config p/default` | non-zero exit on policy |
| ZAP | running app (DAST) | `zap-baseline.py -t URL -J report` | report severity |
| Trivy | deps/image/IaC | `trivy fs . --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1` | exit 1 |

Docs: https://semgrep.dev/docs/ · https://www.zaproxy.org/docs/ · https://aquasecurity.github.io/trivy/
