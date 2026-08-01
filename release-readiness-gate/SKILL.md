---
name: release-readiness-gate
description: Use when deciding whether a change is safe to ship to production — release/hotfix go/no-go, pre-release sign-off, or under pressure to deploy after functional tests pass. Triggers include "ready to ship", "go/no-go", "can we deploy", "ship it", "release checklist", "is it live yet", PM or lead pushing to deploy, "tests pass so ship it", "we'll hotfix later".
---

# Release Readiness Gate

## Overview
A ship decision is a **gate**, not a vibe. Default verdict = **NO-GO**. GO requires affirmative green on *every* required layer — functional, performance, security, ops. "Tests pass" alone is never GO. "We'll hotfix later" is not a gate.

## Core Rule
**No layer green = no ship.** A layer is green only when its explicit pass criterion below is met — not when it was merely "run". A *skipped* layer is a *red* layer.

## The Layers (all required for a full release)
| Layer | Green when… | Skill |
|-------|-------------|-------|
| Functional unit | full suite green | superpowers:test-driven-development |
| Functional integration | API/DB contract green | addy testing-patterns |
| E2E | critical paths green in a real browser | browser-testing-with-devtools |
| Perf load | k6 thresholds met on **current build** (e.g. p95<target, error rate<0.1%) | load-testing-k6 |
| Security SAST | Semgrep clean or every finding triaged | appsec-scanning |
| Security DAST | ZAP baseline clean against staging | appsec-scanning |
| Deps / secrets / image | 0 fixable HIGH/CRITICAL CVEs, no leaked secrets (Trivy + gitleaks) | appsec-scanning |
| Ops | rollback verified (migrations reversible, prior image tagged) + alerts/dashboards cover the new feature | — |

A load test older than the current build is **not green** — re-run on what you'll actually ship.

## Two Modes
**Full release gate** — run every layer. Order: functional → security (cheap, fails fast) → perf (needs staging deployed, slowest) → ops check.

**Emergency/hotfix gate** (tight window) — cheapest hard-blockers first: deps/secrets → boot + migrate → security scan → short load ramp → rollback dry-run. Same pass criteria, minimal duration. Still NO-GO until each is green.

## Rationalizations = Red Flags (stop — you're rationalizing)
| Excuse | Reality |
|--------|---------|
| "Unit tests pass, ship it" | Functional is ONE layer. Perf/security/ops untouched. |
| "We'll hotfix later" | Hotfix-later is a post-incident plan, not a gate. |
| "Load test was 3 months ago" | Stale load test = no data for this build = red. |
| "PM/lead is pinging, just deploy" | Deadline pressure doesn't change pass criteria. |
| "It's a small change" | Small change + new dep = new CVE surface. Scan it. |
| "We scanned last release" | Gate is per-release, not per-quarter. |

## Scoping & Escape Hatches (close these loopholes)
- **"Layer X is N/A"** — valid only with a stated reason (e.g. "no auth/UI → DAST N/A, but API fuzzing still required"). N/A by silence = skipped = red.
- **"It's an emergency, use the hotfix gate"** — emergency mode must name the incident/justification and who authorized it. You cannot self-declare emergency to skip layers on a routine release.
- **Risk-acceptance cap** — you may risk-accept down to HIGH with a named owner + ticket. **An exploitable CRITICAL cannot be risk-accepted** — fix it or slip the release. MEDIUM/LOW: track, don't block.

## GO requires
Every required layer green, **OR** each red explicitly documented and risk-accepted by a named owner with a ticket. A silent exception is silent debt.

## Common Mistakes
- **Equating "tests pass" with GO** — functional green ≠ release green
- **Skipping the layer that's hard to run** (usually E2E or DAST) — that's the one that catches prod-only bugs
- **Trusting stale perf data** — no load number from before the current build counts
- **No verified rollback** — a gate with no way back is a one-way door
