# Filtering Results

After extracting data from search results, filter rows against the criteria in the original query.

## Hard filters

Clear, binary criteria: a date range, a geographic constraint, a numeric threshold, a category membership. Apply mechanically — check each row, remove failures, no judgment call needed.

Examples: "published in 2025", "based in SF or NYC", "under $500B market cap", "excluding Novo Nordisk".

**Negation filters** ("excluding X", "not sponsored by Y") are hard filters in reverse: detect the excluded value and remove matches.

## Soft filters

Require judgment: "genuine design opinion" vs "generic blog post", "actually shipping" vs "just evaluating", "high-signal" vs "noise". For these:

1. Read the relevant content (`python exa.py contents <url> --text` if snippets are insufficient).
2. Make a judgment call based on the content.
3. Include a brief rationale for each keep/drop so your reasoning is visible.

**Semantic negation** is a soft filter: "no review mentions smell, noise, or pests" requires reading content and detecting whether those topics appear, even if phrased differently.

## Filter order

1. **Hard filters first** — cheap, mechanical, eliminates rows before you spend tokens on judgment.
2. **Soft filters second** — only on rows that passed hard filters.

## Temporal filters

Calculate exact date boundaries from today's date before filtering. Check publication/event dates against the boundary. If a date is ambiguous ("early 2025"), note the uncertainty rather than silently including or excluding.

## Completeness vs precision

The query sets the balance:
- "Find every…" / "exhaustive" → include borderline cases, flag them as uncertain.
- "Find the best…" / "top N" → favour precision, drop borderline cases.
- Default → include borderline cases with a flag; let downstream processing decide.

---
*Adapted from Exa Labs' open-source search skill (MIT).*
