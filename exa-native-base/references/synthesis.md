# Synthesizing Research into Narrative

When the task calls for a prose answer (not a list/table), synthesize findings from multiple sources into a coherent response.

## When synthesis applies

- The user asks "what do people say about X" or "what's the state of Y".
- The answer requires integrating perspectives across sources.
- Output should be prose with citations, not a table of entities.

## Structure

**Lead with the answer.** Put the core finding first; the user should get value from the first paragraph alone.

**Organize by theme, not by source.**
- Bad: "Source A says X. Source B says Y. Source C says Z."
- Good: "Theme 1: [insight supported by A, B]. Theme 2: [insight from C, with a counterpoint from A]."

**Surface disagreement explicitly.** When credible sources disagree, don't collapse to consensus — present both sides with evidence and note when each applies.

**Include confidence signals:** how many independent sources support a claim, how fresh the evidence is, practitioners vs commentators.

## Thematic clustering

For many reactions/perspectives:
1. Read through all results.
2. Identify recurring *themes* (a theme has a stance, not just a topic).
3. Group results by theme.
4. Per theme: state it, cite 2-3 representative sources, note the volume.
5. Flag outlier themes that appear once but carry important signal.

## Citation practice

- Every factual claim gets a source URL.
- Prefer inline citations: "Engineers report 3x latency reduction ([source](url))".
- For quotes, include the exact text and attribute it.

## Common mistakes

- **Source-by-source summaries** — feels comprehensive, reads poorly, doesn't synthesize.
- **Collapsing disagreement** — picking a winner instead of presenting the landscape.
- **Missing recency** — treating 2023 sources as current for fast-moving topics.
- **Over-synthesis** — a full essay when the user asked a narrow question.

---
*Adapted from Exa Labs' open-source search skill (MIT).*
