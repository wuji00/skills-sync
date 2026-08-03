---
name: evaluating-search-apis
description: Use when picking, comparing, or evaluating a web search API/tool to plug into an LLM agent, chatbot, or RAG system — e.g. "给 Agent 选搜索", "评估豆包搜索/Tavily/Brave/Serper", "搜索工具哪个适合 Agent", "联网搜索 API 对比", or deciding whether a search product's output is safe to feed straight into a model. Also use when a search returns results that look fine but the agent still hallucinates, cites stale policy, or trusts low-authority sources.
metadata:
  author: wuji00
---

# Evaluating Search APIs for Agents

## Core Principle

**A search built for humans ≠ a search built for agents.** Human search returns ten blue links; the human filters, clicks, judges. Agent search must hand back credibility, freshness, and structure already labeled — because the agent takes whatever it gets as ground truth.

Evaluate from "can the agent use this output directly and trust it?" — NOT from "can a human find info here?". The two diverge sharply.

If you catch yourself scoring recall/MRR/nDCG and calling it done, stop: those are human-search metrics. For an agent, **authority of sources ranks #1**, freshness #2 — a single stale or non-authoritative result propagates into a confident wrong answer.

## The Six Dimensions

Rank-ordered. Top three decide most outcomes; bottom three are depth/cost gates.

| # | Dimension | What to check | Why it ranks here |
|---|-----------|---------------|-------------------|
| 1 | **Source authority & credibility** | Official sources only? Are results tagged with an authority tier (e.g. "very authoritative")? Can you filter to whitelist domains? | Input wrong/untrusted → all downstream reasoning wrong. #1, non-negotiable. |
| 2 | **Freshness / recency** | How fast is breaking info indexed? Precision to day or minute? Time-range filter param (lock to today)? | Returning yesterday's news = returning a wrong answer. |
| 3 | **Vertical depth** | Chinese long-tail, professional domains (tax/law/med) retrievable? | Decides if it works on hard real queries at all. |
| 4 | **Multimodal** | Image search? Does each image carry structured metadata (size / shape / clarity / category)? | Agents picking logos/figures need machine-usable metadata, not raw pages. |
| 5 | **Call paradigm (agent-friendliness)** | Directed query, time control, multi-turn, full-text return (3000+ chars in one call so agent skips scraping), authority tier field? | Determines if you write glue code or just call it. |
| 6 | **Cost** | Price per call + free tier (e.g. 500/mo free)? | Decides if you dare scale. **Rank is not fixed** — see Adapt to Your Domain. |

## How to Actually Test — Two Tiers

### Tier A: Lightweight same-query bake-off (do this first, ~1 day)

Goal: separate "agent-search" from "human-search" fast, without a benchmark suite.

1. **Pick the 3 most discriminating dimensions for YOUR domain.** Authority (#1) and freshness (#2) are almost always included. The third is domain-chosen: **vertical depth (#3)** for text-heavy domains (compliance, finance, medicine, legal); **multimodal (#4)** only if the agent consumes images (content creation, figure-picking). Multimodal is NOT mandatory — forcing it into a finance/compliance eval is a category error.
2. **One real case per dimension**, same query string run on BOTH the candidate and a competitor:
   - Authority: a policy/compliance query → are all top-K official sources, each authority-tier-tagged?
   - Freshness: a breaking-news query with `TimeRange=today` → are all results today's, timestamped to the minute?
   - Multimodal: a logo/figure query → do images come back with size/clarity/category metadata?
3. **Side-by-side, same query, same moment.** No rewording between runs — control the variable. Mind timezone/locale: tools may default to different regions (豆包 → UTC+8, Tavily → US-East), so "today" can mean different things — pin an explicit `time_range` and sample multiple times, one shot is unreliable for noisy queries.
4. Read the raw response shape, not just the answers: are authority tier, publish date, source domain, full-text fields present?

This tier kills ~70% of unsuitable candidates. Vertical-depth (#3) and cost (#6) under heavy load need Tier B — don't conclude from Tier A alone.

### Tier B: Rigorous benchmark (only when 1–2 finalists remain)

For high-stakes domains (money, law, health, compliance). See `reference/benchmark-methodology.md` for the full golden-set + end-to-end + LLM-as-judge protocol. Summary:

- Build a **golden query set** (50–200 queries) with hand-labeled `authoritative_sources` and `stale_traps`.
- Gate by hard thresholds, not total score: `AuthorityRecall@10 ≥ 0.70`, `StaleRate ≤ 0.05`, `FactAccuracy ≥ 0.95`.
- **End-to-end is the only true test**: `query → search → top-K slices → your agent → final answer`, judged by a stronger model against the labeled answer points. Pre-end-to-end layers are just cheap pre-filters.

## Decision Rule

```
For each candidate:
  if AuthorityRecall@10 < 0.70  → reject
  if StaleRate > 0.05           → reject
  if FactAccuracy < 0.95        → reject
  if authoritative-source hit rate weak (中文场景) → reject
Survivors → rank by weighted end-to-end accuracy, citation precision, refusal quality, cost, latency.
```

The thresholds above are **starting points, not universal constants**. They have no paper-backed derivation — calibrate them yourself: run one or two tools you already trust over the golden set, take their median scores as your baseline, then set each gate at roughly `baseline × (1 − tolerated_drop)` where `tolerated_drop` reflects domain stakes (5% for money/law, looser elsewhere). For **multi-factor attribution queries** ("why did X move today?") there is no single ground truth: relax `FactAccuracy` to "matches any acceptable answer point" and judge partial credit, don't demand 0.95 on questions with N equivalent correct answers.

Do NOT sum a total score across dimensions — a tool that aces relevance but ships stale policy is disqualified, not "averaged".

## Adapt to Your Domain

The dimensions and examples in this skill are demonstrated on a Chinese tax/compliance scenario. **Do not copy them verbatim into another domain.** Re-derive three things:

1. **Re-rank dimensions by call frequency and stakes.** High-frequency agents (投研/资讯, thousands of calls/day) push **cost** up to #2–3. Image-free domains drop multimodal entirely.
2. **Grade authority on a tier ladder, not binary.** Define your domain's whitelist as tiers, e.g. finance: 交易所/证监会/上市公司公告 (official) > 巨潮/披露平台 (platform) > 财联社/Wind/券商研报 (licensed media) > 雪球/股吧 (UGC). Tag expected tier per query; gate on official-tier hit rate, not a flat "is it authoritative".
3. **Rebuild golden-set distribution + boundary cases per domain.** Time-sensitive share rises for news/投研 (~35%); falls for static reference. Boundary cases are domain-specific (finance: AH-share confusion, halted-stock, cross-market; legal: same-name statute disambiguation, repealed-vs-current). The tax examples in `reference/benchmark-methodology.md` show the *shape*, not your content.

For multi-factor queries, label `answer_points` as an **accept-set** ("any one of these counts as correct") and have the judge score partial credit — see the JSON note in the reference.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Score recall/MRR/nDCG and call the eval done | Those measure human search. Add authority recall + freshness + end-to-end answer correctness. |
| Pull `expected` from the agent's own output | Self-proving eval. Expected MUST come from hand-labeled answer points / official text (CLAUDE.md rule 8). |
| Sum dimensions into one score, accept the highest | Use hard gates + weighted ranking of survivors. One stale-policy path disqualifies. |
| Trust a single breaking-news timestamp | Check `source_domain` distribution — vendors may bias to own properties (头条/抖音号), which aren't authoritative. |
| Test only Tier A and publish a verdict | Vertical depth + cost-at-scale need load testing. State what you did NOT verify. |
| Expect exclusive content | General search finds the same things. Agent value is in the **return shape**: authority tier, time control, full-text, image metadata. Closed native data (抖音商城 etc.) is unreachable. |

## Known Boundaries (state these explicitly in any verdict)

- No search gets exclusive content general search can't find.
- Closed native data (抖音商城商品 etc.) is unreachable by any tool.
- Advantage is in **return shape**, not coverage: authority tiering, time control, full-text return, image metadata.
- **Web search ≠ structured data.** Real-time quotes, 龙虎榜, financials need structured APIs (Wind/Tushare/聚宽), not search. Decide whether the search tool composes with your structured sources — search ranking alone never covers this.
- **Routing is a valid architecture.** The skill rejects/ranks single tools, but production often routes: 豆包 (国内深度) + Tavily (海外/英文). If no single survivor covers all queries, design a multi-source router instead of forcing a tie-break.
- Chinese long-tail depth and cost-at-scale require long-running load tests — don't conclude without them.

## Red Flags — STOP

- Reaching for relevance/nDCG as the headline metric
- "The agent returned an answer, so the search is fine" — answer correctness needs independent expected
- Comparing queries with different wording across tools
- Concluding depth/cost from a handful of calls
- Treating "human can find it" as proof "agent can use it"
- A plausible single-cause answer on a multi-factor query ("光伏涨 because 硅料涨") that silently drops the main driver (policy) — check driver recall against the accept-set, not whether it sounds right
