---
name: learn-framework-via-skill
description: Use when starting to learn any new framework that has official source code, official docs, and the goal of writing runnable examples — including LangChain / LangGraph / Deep Agents and any equivalent framework. Codifies a six-step workflow: load skill → verify against source → write minimal example → run with traces → record pitfalls in four-section format → deepen with comparative experiments. Generic across frameworks; not LangChain-specific.
---

# learn-framework-via-skill

> **Origin**: extracted from `learn-demo/docs/playbooks/learn-langchain-skill-workflow.md` (2026-07-19 ~ 20). Validated across 60 runnable examples + 23 pitfall docs.
>
> **Scope**: works for any framework with official source code + official docs + runnable-example goal. The original use case was LangChain/LangGraph/Deep Agents; the principles generalize.

## When to Use

- Starting a new练手仓库 / sandbox project for a framework you don't yet know.
- Onboarding a new framework (e.g. crewai, autogen, haystack, semantic-kernel, llama-index) using the same rhythm you used for the previous one.
- Picking up an old framework after a long gap and want to refresh with examples + pitfalls, not just docs.

**Do NOT use** for:
- Pure reading/study without writing runnable code (skip steps 3-4).
- Production development on a framework you already know well (use framework-specific skills instead).

## Prerequisites

- A clean sandbox repo (suggest `uv init --bare` for Python; equivalent for other ecosystems).
- A `common/` directory for shared helpers — without it, every example will reinvent setup code.
- Read access to the framework's official source (`site-packages/...` or equivalent local install).
- Read access to the framework's official docs (context7 / MCP docs / official site).

## The Six Steps

### 1. Load skill, plan cadence

- Invoke the framework-specific skill (e.g. `Skill(skill="langchain-fundamentals")`) and read its full chapter structure.
- Convert each chapter into a `TodoWrite` entry — this creates a visible learning path.
- **Cadence rule**: finish one → digest/deepen → start the next. **Do not write all chapters in one pass.** Stage delivery; each stage ends with a real run.

### 2. Verify against source, then write code (CORE PRINCIPLE)

**Never write framework code from memory** — skills lag, versions differ, and docs drift.

Verification sources (in priority order):

1. **Read the installed package source** (`.venv/Lib/site-packages/...` or equivalent). Most authoritative. Use Grep + Read for signatures, parameter types, defaults, version-specific behavior.
2. **context7 / official docs** — for version-specific usage and concepts.
3. **Reference sibling repos** (e.g. `../<framework>-upstream/`) — see how the maintainers actually use the API.

Example verifications:
- "Can `create_agent` take a `ChatOpenAI` instance?" → Grep `def create_agent` and read the signature.
- "Real usage of `@wrap_tool_call`?" → Grep `@wrap_tool_call` in official examples.
- "Which structured-output method does provider X support?" → Write a probe script that tries all options with try/except.

**Expected output**: every API decision is traceable to source line, doc page, or upstream commit.

### 3. Write the minimal runnable example

- **Reuse `common/` helpers** (LLM factory, runtime setup, etc.). Don't reinvent. New general-purpose capabilities also go into `common/` — they pay off next time.
- **Match project code style**: path injection for cross-folder imports, module docstring (with run command + key points), `main() + if __name__ == "__main__"`.
- One example = one topic. Comments answer **"why this way"**, not **"what this does"**.
- When overriding framework callbacks / middleware: **subclass signatures obey parent contracts** (don't rename params — LSP violation). Discard unused params with `del`.

**Expected output**: each topic has one self-contained runnable script.

### 4. Run and verify (don't infer)

- Every example must `uv run python <file>` end-to-end.
- Verification must be **observable**, not just "no error":
  - **Trace print**: walk `result["messages"]` to see each step (HumanMessage → AIMessage(tool_calls) → ToolMessage → final AIMessage).
  - **Timing**: `time.perf_counter()` to prove latency actually happened (e.g. exponential backoff).
  - **With/without comparison**: e.g. logging shows nothing when HITL rejects → ironclad evidence of middleware layer ordering.

**Expected output**: only after the example really runs do you move to the next topic.

### 5. Hit a pitfall: reproduce → diagnose → record

Every bug becomes a four-section record in `docs/pitfalls/<name>.md`:

| Section | Content |
| --- | --- |
| 现象 (Symptom) | Exact error / wrong behavior + reproduction conditions |
| 根因 (Root cause) | Source line + why (with `file:line` link) |
| 解决方案 (Fix) | Code + principle |
| 预防措施 (Prevention) | How to avoid re-stepping on it |

Reproduction techniques:
- "Which API does the model support?" → write a **temporary probe script** with `try/except` for every option; delete after capturing results into the canonical example + pitfall.
- "Pyright warnings like 'import unused' / 'cannot access attribute'" → first judge: is this a **mid-snapshot artifact** (multiple Edits applying in flight) or a real issue? **A real run is the final arbiter.**

**Expected output**: one pitfall doc per bug. Future-you (and others) never re-step.

### 6. Digest phase: deepen + comparative experiments

After finishing a topic, proactively deepen (user-led):

- **Comparative experiments**: long vs short description, approve vs reject, before vs after parameter change. Comparison is more visceral than explanation.
- **"Can we run X?"** — when an advanced usage comes up (caching, backoff, HITL stacking), **implement + verify on the spot**, don't just describe.
- Each deepening point lands as runnable code — every compare-pair becomes its own demo.

**Expected output**: each topic's depth extends beyond what the skill documented. New helpers deposit back into `common/`.

## Quality Checkpoints

- [ ] Every API usage is traceable to source / docs / upstream.
- [ ] Every example has been run end-to-end (not just compiled).
- [ ] Every bug has a four-section pitfall doc in `docs/pitfalls/`.
- [ ] Every new general-purpose capability lives in `common/`.
- [ ] Digest phase produced comparative demos, not just written commentary.

## Common Pitfalls (meta — about the workflow itself)

- **Writing from memory**: skill says "use X param" but the installed version removed it → you didn't verify. Always grep the source.
- **"No error" = correct**: missing trace print means you don't know what actually ran. A clean exit with garbage output is still garbage.
- **Skipping verification**: copy skill verbatim, run, hope. First version mismatch breaks silently.
- **Pitfall not recorded**: "I'll remember" — you won't. Future-you (or another agent) will re-step.
- **Only-explain, no-deepen**: finished a topic at "what it does" level, never asked "what if I change X?". Knowledge stays shallow.

## Why This Works (Design Notes)

- **Skill as GPS, not autopilot**: skill gives direction; source/docs/upstream give ground truth. Verify every leg.
- **`common/` is a snowball**: each topic adds a new helper. Day 6's `common/` is 10× thicker than day 1's — invisible compound interest.
- **Four-section pitfall = anti-entropy**: by default, "I stepped on this" decays (memory fades, context clears). Forcing a structured doc **externalizes** the experience into git history: searchable, transferable, stackable.

## Source

- Original doc: `learn-demo/docs/playbooks/learn-langchain-skill-workflow.md`
- Validated by: 60 runnable examples (agents/ + langgraph/ + persistence/ + hitl/ + rag/ + deepagents/) + 23 pitfall docs
- Companion skill: `ecosystem-primer` (frame selection: which framework to learn in the first place)