# Extracting Structured Data from Search Results

After searching, extract structured information from the results.

## When snippets are enough

Search results include titles, URLs, and snippets/highlights. For many fields (company name, person name, funding round, publication date) the snippet suffices — extract directly before fetching full pages.

## When to deep-read with `contents`

Fetch the full page when:
- The snippet mentions what you need but omits the actual value.
- You need body text to make a judgment call ("genuine design opinion or generic?").
- You need multiple fields from one rich source (case study, team page, filing).

```bash
python exa.py contents https://source-1.com https://source-2.com --text
```
Batch up to 5-10 URLs per call to minimize round trips. Read full context rather than truncating.

## Extracting into a schema

Given a schema (the "columns"), extract each field per result:

1. **Structured fields** (name, date, URL, funding amount, ticker): extract the literal value; mark missing rather than guessing.
2. **Categorical fields** (industry, stage, role level): map to the closest category; note ambiguous mappings.
3. **Semantic fields** (sentiment, "genuine opinion?", relevance to a theme): read and judge; include a brief rationale.
4. **Negation fields** ("no Series A announcement"): check for *absence*. Search the positive case; if nothing surfaces, report absence with a confidence level tied to how thorough coverage was.

## Handling missing data

- Mark fields "not found" rather than guessing.
- Distinguish "confirmed absent" (searched thoroughly) from "not found" (limited access/coverage).
- Note paywalled/inaccessible sources explicitly.

## Confidence signals

- **Direct**: the source explicitly states the value.
- **Inferred**: derived from context.
- **Uncertain**: single indirect signal, could be wrong.

## Output format

Return compact structured output — keep it terse, because results merge with other searches and verbosity compounds:

```json
[ { "name": "...", "field_1": "...", "source": "url", "confidence": "direct" } ]
```
…or a Markdown table if that suits the task better.

---
*Adapted from Exa Labs' open-source search skill (MIT).*
