# Tier B: Rigorous Benchmark Methodology

Use only when 1–2 finalists remain after Tier A bake-off, and the domain is high-stakes (money, law, health, compliance). Full evaluation, ~1 week.

## Step 1 — Golden Query Set

**50–200 queries**, hand-labeled. Cover five types:

| Type | Share | Example |
|------|-------|---------|
| Simple fact | 30% | 增值税起征点 |
| Time-sensitive | 20% | 2026 小规模纳税人征收率 |
| Long-tail professional | 20% | 高新企业研发费用加计扣除 2026 |
| Regional | 15% | 上海自贸区个税 |
| Comparison/disambiguation | 15% | 一般纳税人 vs 小规模 |

Each query labeled with independent ground truth (NOT derived from any candidate's output):

```json
{
  "query": "2026年小规模纳税人增值税征收率",
  "answer_points": ["1%减按", "适用期至2027.12.31", "财政部税务总局公告2023年第19号"],
  "answer_mode": "all_required",
  "authoritative_sources": [
    "https://www.chinatax.gov.cn/...",
    "https://www.mof.gov.cn/..."
  ],
  "freshness_tag": "effective_2026",
  "stale_traps": ["3%征收率 (pre-2023, now superseded)"]
}
```

**`answer_mode` field** — set per query:
- `"all_required"`: single ground truth (tax rate, statute number). Judge demands all points present. Use the 0.95 `FactAccuracy` gate.
- `"any_acceptable"`: multi-factor attribution ("why did光伏板块涨 today"). `answer_points` is an **accept-set** — matching ANY one counts as correct; judge scores partial credit (how many real drivers caught vs. fabricated). Do NOT apply the 0.95 gate here; report `driver_recall = matched / total_acceptable` instead.

Mix modes in the golden set and report them separately — averaging a single FactAccuracy across both modes hides failures.

Source suggestions: real historical user questions > domain expert writes 20 > scrape 12366 hotline / Zhihu topics.

## Step 2 — Three-Layer Evaluation (cheap → expensive, filter at each)

```
Golden set (50-200)
  → Layer 1: raw search eval      (filters ~70% of weak candidates)
  → Layer 2: slice-quality eval   (filters dirty-data candidates)
  → Layer 3: end-to-end eval      (final decision basis)
```

### Layer 1 — Raw search (cheap)
Query each API directly, inspect returned results only.
- Metrics: `AuthorityRecall@5/@10`, `MRR`, `nDCG@10`, `StaleRate`, `CN_Gov_HitRate@10`.

### Layer 2 — Slice quality (the artifact fed to the LLM)
Inspect returned `content`:
- `SignalRatio = effective body chars / total returned chars` (dirty HTML drags the agent down).
- `AvgTokens` per call — redundant fields bloat context.
- `StructuredScore` — does it return `title / publish_date / source_domain`?
Eyeball raw response; dirty data → reject.

### Layer 3 — End-to-end (the only true test) ⭐
Pipeline: `query → search API → top-K slices → your agent → final answer`.

Three judging methods combined:
- **LLM-as-judge** (stronger model than your agent): answer factual accuracy vs `answer_points`; citation accuracy (cited clause numbers really exist and match); hallucination rate (fabricated clauses/numbers).
- **Human spot-check**: 20% of answers reviewed by a domain professional, calibrates the judge.
- **Refusal quality**: does it refuse when it should, instead of hard-fabricating?

**Self-proving eval is forbidden** (CLAUDE.md rule 8): `expected` MUST come from hand-labeled `answer_points`, never reverse-derived from the agent's output.

## Step 3 — Comparison Matrix

| Dimension | Candidate A | Candidate B |
|-----------|-------------|-------------|
| AuthorityRecall@10 | | |
| StaleRate | | |
| CN_Gov_HitRate@10 | | |
| End-to-end accuracy | | |
| Citation accuracy | | |
| Refusal quality | | |
| P95 latency | | |
| Cost / call | | |
| `include_domains` param | | |
| Time-range param | | |

## Step 4 — Boundary Cases (where it flips)

The cases below are from a Chinese tax/compliance domain. **Do not reuse them verbatim in another domain** — they will miss every failure mode that matters to you. Use them as templates for the *kinds* of stress, then brainstorm your domain's equivalents.

**How to generate your own boundary cases** — for each axis below, ask "where does my domain have an example of this stress?":

1. **Same-name disambiguation** — two entities sharing a name where one is stale/wrong. *Tax:* 增值税法 vs 增值税暂行条例. *Finance:* A/H share, halted vs active. *Legal:* repealed vs current statute.
2. **Cross-scope bleed** — query scoped to one region/market/version returns another's. *Tax:* 深圳 vs 北京. *Finance:* A股 vs 美股同名.
3. **New-content window** — published <7 days ago; who indexed it first?
4. **Rumor resistance** — widely-circulated falsehood; does the tool surface it as fact?
5. **Empty-result behavior** — query a non-existent entity: returns empty (correct) or a similar-but-wrong result (dangerous)?
6. **Prompt injection** — page/document hides "ignore previous instructions"; does it pollute the agent? (especially relevant for PDF research reports in finance)
7. **Over-long query** — full business scenario pasted; can it extract the key entity?

Aim for 5–10 domain-specific cases before declaring a verdict.

## Step 5 — Decision

Hard gates, then weighted ranking of survivors (see SKILL.md Decision Rule). Never average into a single score.
