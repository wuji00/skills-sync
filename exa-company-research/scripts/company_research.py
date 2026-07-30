#!/usr/bin/env python3
"""Company research preset — semantic search over Exa's company index.

Usage:
    python company_research.py "AI infrastructure startups in San Francisco" -n 15
    python company_research.py "companies like Stripe" -n 10
    python company_research.py "Anthropic funding rounds" -c news --start-published 2025-01-01

Defaults to category=company. Override with -c (e.g. -c news for press coverage).
Requires EXA_API_KEY (env or repo-root .env). See exa-native-base for setup.
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
        prog="company-research",
        description="Find companies, competitors, funding, and news via Exa.",
        default_category="company",
        default_num=10,
    ))
