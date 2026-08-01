---
name: load-testing-k6
description: Use when validating API or service performance under load — capacity planning, SLO/breakpoint checks, pre-release stress/soak tests, or diagnosing latency/throughput limits. Triggers include "load test", "stress test", "soak test", "how many concurrent users can it handle", p95/p99 latency targets, "will it survive launch", throughput/RPS limits.
---

# Load Testing with k6

## Overview
k6 = code-first load tester (JS scripts) that hits HTTP/gRPC/WebSocket. **Cross-language** — backend language irrelevant; only the endpoint matters. CI-friendly, threshold-gated: perf becomes a pass/fail signal, not a report you eyeball.

For single-function micro-benchmarks use the language's native bench (pytest-benchmark, Benchmark.js). For frontend Core Web Vitals use `browser-testing-with-devtools` / Lighthouse. k6 measures **server/system** behavior under load.

## When to Use
- **Pre-release**: "will it survive N concurrent users?"
- **SLO validation**: p95 < 200ms, error rate < 0.1% under target load
- **Capacity planning**: find the breaking point
- **Regression**: catch perf regressions in CI
- **Soak**: detect memory leaks / degradation over hours

## Test Type → Stage Config
| Type | Goal | Stage shape |
|------|------|-------------|
| Load | Sustained normal peak | ramp to target VUs, hold, ramp down |
| Stress | Beyond peak, find limits | ramp past expected until it breaks |
| Soak | Long-run leaks | moderate VUs for hours |
| Spike | Sudden burst | instant jump to high VUs |
| Breakpoint | Find max throughput | ramp until error rate spikes |

## Core Script Anatomy
```js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 50 },   // ramp-up
    { duration: '1m',  target: 50 },   // hold
    { duration: '10s', target: 0 },    // ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'],   // 95% of requests under 200ms
    http_req_failed:   ['rate<0.01'],   // <1% errors
  },
};

export default function () {
  const res = http.get('https://staging.example.com/api/score', {
    headers: { Authorization: `Bearer ${__ENV.TOKEN}` },
  });
  check(res, { 'status 200': r => r.status === 200 });
  sleep(1);   // think time — realistic, prevents unrealistic hammering
}
```

## Auth, RPS & POST (beyond the basics)

**Authenticated multi-step flow** — log in once in `setup()`, share the token across all VUs/iterations:
```js
import http from 'k6/http';

export function setup() {
  const r = http.post('https://staging.example.com/login',
    JSON.stringify({ user: __ENV.USER, pass: __ENV.PASS }),
    { headers: { 'Content-Type': 'application/json' } });
  return { token: r.json('token') };          // return value → passed into default fn
}

export default function (data) {
  http.get('https://staging.example.com/api/me', {
    headers: { Authorization: `Bearer ${data.token}` },
  });
}
```
Per-user creds: generate them in `setup()` into an array, index by `exec.scenario.iterationInTest`.

**Fixed RPS (throughput, not VUs)** — `constant-arrival-rate` holds a target request rate:
```js
export const options = {
  scenarios: {
    steady: {
      executor: 'constant-arrival-rate',
      rate: 500, timeUnit: '1s',     // 500 RPS
      duration: '2m',
      preAllocatedVUs: 100,          // pool size; raise if you see dropped_iterations
      maxVUs: 500,
    },
  },
};
```
If `dropped_iterations > 0`, raise `preAllocatedVUs` — k6 couldn't spin VUs fast enough to hold the rate.

**POST JSON with a unique body per iteration:**
```js
let n = 0;
export default function () {
  http.post('https://staging.example.com/items',
    JSON.stringify({ name: `item-${++n}` }),
    { headers: { 'Content-Type': 'application/json' } });
}
```
For large datasets, load fixtures once via `SharedArray` from a JSON file (read once, shared across VUs).

## Thresholds = the Gate
Thresholds are assertions over the whole run. k6 exits **non-zero** if any breach → CI fails the build. This is the entire point of putting load testing in CI.

Common thresholds:
```js
thresholds: {
  http_req_duration: ['p(95)<200', 'p(99)<500'],  // p(N) = Nth-percentile latency, in ms
  http_req_failed:   ['rate<0.01'],                 // rate is 0..1 → 0.005 = 0.5%
  iterations:        ['count>1000'],
}
```

## CI Integration
k6 exits non-zero when any threshold breaches — that exit code IS the gate.
```bash
k6 run --quiet script.js     # exit 1 on threshold breach → fails the step
```
GitHub Actions (step fails automatically on non-zero exit):
```yaml
- name: Load test
  run: k6 run --quiet tests/load.js
  env:
    TOKEN: ${{ secrets.STAGING_TOKEN }}
```
Export machine-readable results with `--out json=results.json` for dashboards.

**Built-in metrics to gate/read:** `vus`, `iterations`, `http_reqs`, `http_req_duration`, `http_req_failed`, `dropped_iterations`, `checks`. The end-of-run stdout summary prints p(90)/p(95)/p(99) and error rate — the numbers to compare run-over-run.

- Test a **staging-like** env, not prod (unless prod-capacity is the explicit goal)
- Run from **outside** the app host — measure the network path, not loopback
- Parametrize secrets via `k6 run -e TOKEN=$TOKEN`, read as `__ENV.TOKEN`
- For >single-machine load: k6 Cloud, or k6 operator on k8s

## Common Mistakes
- **No think time** (`sleep`): unrealistic RPS, overstates capacity
- **Instant ramp**: shock-tests infra, not steady-state behavior
- **Test from localhost**: misses reverse-proxy/CDN/network; inflates capacity numbers
- **No thresholds**: k6 runs, you eyeball a number, nothing gates — pointless in CI
- **Single endpoint only**: real load hits mixed routes; use `scenarios` with execution weights
- **Ignore errors to chase RPS**: a server returning 500s "handles" load by failing — error rate gates prevent this lie

## Quick Reference
| Need | Command |
|------|---------|
| Run script | `k6 run script.js` |
| CLI override VUs/duration | `k6 run --vus 100 --duration 1m script.js` |
| Pass env var | `k6 run -e TOKEN=xxx script.js` → `__ENV.TOKEN` |
| CI gate (quiet) | `k6 run --quiet script.js` |
| Multi-scenario / weights | define `options.scenarios` |

Official syntax & flags: https://k6.io/docs/
