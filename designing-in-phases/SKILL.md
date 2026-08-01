---
name: designing-in-phases
description: Use when designing any system, module, or feature before implementation — when starting outline/high-level design, detailed/module design, or about to write DB schemas (CREATE TABLE), API contracts, or Controller/Handler code. Symptoms that mean use this: design blends architecture and table schema in one flat doc, DB choice assumed or buried mid-DDL, implementation code appears inside the design doc, no visible gate between "what/which" decisions and "how exactly" definitions.
metadata:
  author: wuji00
---

# Designing in Phases

## Overview

**Core principle: each design decision belongs to exactly ONE phase. Never make it twice, never make it in the wrong phase.**

- Outline design decides **WHAT** and **WHICH** (which DB, which protocol, which architecture).
- Detailed design defines **HOW EXACTLY** (ER → DDL, API contract, algorithm, state machine).
- Implementation **EXECUTES** — runs the DDL, writes handlers to the contract. Zero new design.

A decision moved to a later phase is a defect. A decision relitigated in a later phase is a defect. A design doc that blends all three is the most common defect.

## When to Use

Use when starting any system / module / feature design, or about to write `CREATE TABLE`, API endpoints, or handler code.

Stop signals — you're about to violate a phase:
- About to write `CREATE TABLE` but DB choice + partition strategy not yet recorded as decided.
- About to write Controller/Handler code but no API contract doc exists.
- Writing runnable implementation code inside a "design" document.
- Architecture, table schema, and algorithm in the same section with no headings separating them.

**When NOT to use:** trivial single-file change, pure bugfix, one-off script, config tweak. YAGNI applies to ceremony too.

## The Phase Contract — what each phase IS

Each phase OUTPUTS a specific artifact. A phase is not "done" until its artifact exists and is recorded. Do not start the next phase until the current gate passes.

### Phase 1 — Outline Design / 概要设计 (system level)

**OUTPUT: an outline design doc with these sections, all DECIDED (not discussed):**

| # | Decision | Must be settled here |
|---|----------|----------------------|
| 1 | Architecture style | monolith / microservice / serverless — pick one, with one-line reason |
| 2 | Module / service split | named modules + one-sentence responsibility each |
| 3 | Tech stack | language, framework, middleware |
| 4 | Data flow + deployment topology | diagram + topology |
| 5 | Non-functional targets | perf, security, availability numbers |
| 6 | **Database selection + partition strategy** | MySQL / PostgreSQL / MongoDB + sharding/partition plan |
| 7 | **Inter-service comms + API style** | REST / gRPC / MQ + RESTful / RPC |

**GATE 1:** all 7 decided and written down. DB choice (row 6) and comms/API style (row 7) are the two most-skipped — verify them explicitly.

### Phase 2 — Detailed Design / 详细设计 (module level)

**OUTPUT, per module:**

1. ER diagram → logical model → **physical DDL (`CREATE TABLE`)** — including indexes, field types, constraints.
2. **API contract doc** — endpoint path, HTTP method, request/response structure, status codes, error codes, auth method.
3. Core business logic flow — flowchart or sequence diagram.
4. Key algorithm description — describe the algorithm; do NOT write the implementation.
5. State machine + event definitions.

**GATE 2:** DDL exists for every entity, contract exists for every endpoint. Until then, no Phase 3.

### Phase 3 — Implementation / 实现

- Run Phase 2's DDL against the database.
- Write Controller/Handler strictly to Phase 2's contract.
- **No new design decisions.** If implementation surfaces a missing decision, stop, go back to its phase, record it, then resume. Do not silently decide inline.

## Decision-Lock Table (memorize)

| Decision | Locked in |
|----------|-----------|
| DB vendor + partition strategy | Phase 1 |
| Comm protocol + API style | Phase 1 |
| Architecture style + module split | Phase 1 |
| ER → physical DDL, indexes, constraints | Phase 2 |
| API contract (path/method/shape/errors/auth) | Phase 2 |
| Algorithm logic, state machine, events | Phase 2 |
| Actual handler/controller code | Phase 3 |

If you're holding a pen to write something in row N and a row < N decision is unsettled → stop, settle it in its phase first.

## Templates (for Phase 2)

### CREATE TABLE skeleton

```sql
CREATE TABLE <entity> (
  id          <type>      PRIMARY KEY <autoinc?>,
  -- business columns with NOT NULL / defaults made explicit
  -- every FK gets an index
  created_at  <type>      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  <type>      NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- one comment per non-obvious column stating WHY, not what
```

Required per table: primary key, indexes for every FK and every hot lookup path, explicit NOT NULL/default, comment on non-obvious columns.

### API contract skeleton

```
<METHOD> <path>
Auth: <method>
Request:  { ... }   // field-by-field, with type + required + meaning
Response: { ... }   // success shape
Errors:
  <status> <CODE>  — <when>
  <status> <CODE>  — <when>
```

Required: method, path, auth, request shape, response shape, error codes with trigger conditions. No endpoint ships without all five.

## Rationalizations — and the reality

| Excuse | Reality |
|--------|---------|
| "It's one system, one blended doc is fine" | Blended doc hides which decisions are settled vs open. Gate gets skipped. |
| "DB choice is obvious, I'll assume MySQL" | "Obvious" = unrecorded = relitigated at DDL time. Write it in Phase 1. |
| "I'll write the engine code to clarify the design" | Code is Phase 3. Describe the algorithm in Phase 2; code it later. |
| "Phase gates are ceremony, this project is small" | Small projects skip phases by an explicit YAGNI call, not by drift. Say which phase you're folding and why. |
| "I already have the DDL in my head, skip the ER" | ER → logical → physical is the audit trail. Skipping it loses the why behind keys/types. |
| "Implementation will reveal the real design anyway" | Then implementation owns decisions it shouldn't. Go back, record, resume. |

## Red Flags — STOP and return to the right phase

- About to write `CREATE TABLE` but Gate 1 (esp. DB + partition) not recorded.
- About to write a handler but no contract doc for that endpoint.
- Runnable code inside a design doc.
- Architecture and table DDL in the same section.
- "以 X 为例" / "assume X" next to a DB, protocol, or stack choice — that choice belongs in Phase 1 as decided.

**All of these mean: stop, find the decision's home phase, settle it there, then continue.**

## Self-Check (run before declaring a phase done)

Before closing a phase, answer in one line each:
- Phase 1: "Which DB, which partition, which protocol, which API style?" — four concrete answers present?
- Phase 2: "Every entity has DDL? Every endpoint has a contract? Algorithm described (not coded)?"
- Phase 3: "Did I introduce any decision not in Phase 1 or 2?" — if yes, that's a defect; backfill it upstream.
