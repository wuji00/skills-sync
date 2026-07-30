# Evaluating Source Quality

Source quality matters most for "best of", ranking, expert-finding, and best-practices queries — but it's useful context for almost any research task. Tag quality signals in your output so results can be weighted downstream.

## Noise signals — filter out first

| Signal | What to look for |
|---|---|
| No skin in the game | Theorists who don't do the work — no portfolio, no shipped products, no verifiable results |
| Misaligned incentives | Paid to sell, not to be right (sponsored content, vendor blogs, affiliate-heavy) |
| Circular credentials | Validated only by peers in the same bubble — no external evidence of impact |
| Positive-only advice | No tradeoffs or failure modes — "just do X" with no caveats |
| Temporal decay | Shifted from doing to teaching/advising — are they still actively building? |

## Practitioner vs commentator

The most important distinction. Practitioners do the work; commentators write about it.
- **Practitioner signals:** shipped products, open-source contributions, case studies with specific numbers, "we built X and here's what happened".
- **Commentator signals:** roundup posts, "top 10" lists, content that mainly links to others, no first-hand experience.

## Verification searches (only when judging credibility)

```bash
python exa.py search "[name] recommended by experts practitioners" -n 5   # who cites them?
python exa.py search "[name] results portfolio case study shipped"   -n 5   # track record?
python exa.py search "[name] criticism overrated wrong"              -n 5   # criticism?
```

## Tagging in output

For each source, include a short free-form `quality` note describing what you observed — e.g. "shipped the product, writes from direct experience" or "roundup blog, no original work, links to others." Don't classify into rigid categories; just preserve the signal for downstream ranking.

## At the orchestrator level

1. **Convergence across high-signal sources** beats raw convergence (3 low-quality sources agreeing is shared noise).
2. **Weight practitioners over commentators.**
3. **Via negativa** — define who to exclude before synthesizing; filtering noise beats seeking brilliance.
4. **Red-team the compiled results** — what perspectives or biases are missing? Run a targeted follow-up for gaps.
5. **Ideas over entities** for expert-finding — lead with what the best sources agree on, then cite who said it.

---
*Adapted from Exa Labs' open-source search skill (MIT).*
