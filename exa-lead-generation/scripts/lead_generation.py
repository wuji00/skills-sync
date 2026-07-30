#!/usr/bin/env python3
"""Lead generation preset — company discovery for prospect lists.

This is the first pass of lead-gen: find target companies that match an ICP.
Pass 2 (decision-makers) uses exa-people-research; see this skill's SKILL.md for
the full pipeline.

Usage:
    python lead_generation.py "Series A B2B SaaS companies in fintech" -n 20
    python lead_generation.py "category:company developer tools startups hiring 2026" -n 20

Defaults to category=company. Requires EXA_API_KEY (env or repo-root .env).
"""
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not os.path.isdir(os.path.join(_d, "_shared")):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "_shared"))

from exa_client import preset_cli  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(preset_cli(
        prog="lead-generation",
        description="Source target companies for a prospect list via Exa.",
        default_category="company",
        default_num=20,
    ))
