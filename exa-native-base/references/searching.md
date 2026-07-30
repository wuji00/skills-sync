# Searching with Exa

You drive Exa through the local client:
- **`python exa.py search "<query>"`** — semantic search. Key flags: `-n` (numResults), `-c` (category), `-t` (type), `--include-domains`, `--only-domains`, `--start-published` / `--end-published`, `--include-text`, `--text` (include page text). The use-case skills wrap this with a default category.
- **`python exa.py contents <url> [<url> …] --text`** — read full content from known URLs, after search, when snippets are insufficient.

(Paths are relative to `exa-native-base/scripts/`; the use-case skills expose the same engine via their own `scripts/` wrapper.)

## How Exa search works

Exa uses vector embeddings, not keywords. It finds pages semantically similar to your query. It does **not** match keywords exactly, understand boolean logic (AND/OR/NOT), or validate that results meet your criteria. You are describing a target page; Exa returns the nearest neighbours in embedding space.

## Writing good queries

**Describe the page you want to find**, not the fact you want to know. Write natural grammatical phrases.

| Looking for | Bad query | Good query |
|---|---|---|
| Blog posts about X | "X" | "detailed blog post about X written by a practitioner" |
| Company doing Y | "Y company" | "category:company startup building Y for enterprise" |
| Person at company | "person at company" | "category:people senior engineer at Acme" |

**`numResults` sizing — match to query precision:**

| Query precision | `-n` | Example |
|---|---|---|
| Named entity (specific person/company) | 5 | `"WaveForms AI founding story funding details"` |
| Precise filter (narrow category + constraints) | 10 | `"category:company developer tools API testing Series A"` |
| Broad discovery (wide category, few constraints) | 15 | `"category:news engineer launches startup 2025 2026"` |

Never use `-n` above 25. For more coverage, run more queries at different angles (n=10-15) rather than one query at n=50.

**Categories.** Pass with `-c` or write `category:<type>` at the start of the query string. Valid: `company`, `research paper`, `news`, `pdf`, `github`, `personal site`, `linkedin profile`, `financial report`. (The old `tweet` category was retired; use `exa-x-search`, which filters to x.com/twitter.com.)

```bash
python exa.py search "category:research paper sparse attention mechanisms for long context" -n 10
python exa.py search "category:people VP Engineering AI infrastructure San Francisco" -n 10
python exa.py search "category:company developer tools for API testing" -n 10
```

## Query diversity

Multiple queries on one topic should target genuinely different angles, not synonym swaps. "overhyped" vs "overrated" vs "disappointment" are the same angle; skeptic vs builder vs practitioner are different. **Word order affects embeddings** — "Python async patterns for web scraping" and "web scraping async patterns in Python" can return different results. Run 2-3 phrasings in parallel when you need coverage.

## Encoding time

If the task involves time ("last week", "recent", "this month"), calculate exact dates FIRST from today's date. Then either encode them semantically in the query ("published in March 2026") or use `--start-published` / `--end-published`. Never eyeball dates or reuse dates from examples.

## Anti-patterns

- Boolean operators ("AND", "NOT") are just words to Exa, not operators.
- Quotes don't force exact-phrase matching.
- Very short queries (1-2 words) produce scattered, low-quality results.

## When searches return nothing

a. Make the query longer and more specific.
b. Try a different angle, not a synonym swap.
c. If multiple angles return nothing, the topic likely has limited web coverage — report that rather than fabricating results.

## Domain-specific patterns

Each use-case skill's `SKILL.md` carries specialized query patterns for its domain (companies, people, papers, code, news, hidden relationships). Read the relevant skill before a deep dive.

## After getting results

Exa returns similarity, not validation. Review titles/snippets and discard irrelevant results using judgment — don't assume all results match your criteria. For the most promising results, deep-read with `python exa.py contents <url> --text`.

---
*Adapted from Exa Labs' open-source search skill (MIT).*
