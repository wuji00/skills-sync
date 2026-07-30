#!/usr/bin/env python3
"""People research preset — LinkedIn-weighted semantic search over Exa.

Usage:
    python people_research.py "engineer at OpenAI" -n 10
    python people_research.py "Head of Growth B2B SaaS startup San Francisco" -n 12
    python people_research.py "Jane Smith Anthropic machine learning" -n 5

Defaults to category="linkedin profile". Be specific (company, role, location) —
vague people queries match many irrelevant profiles.
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
        prog="people-research",
        description="Find people by role, company, and location via Exa.",
        default_category="linkedin profile",
        default_num=10,
    ))
