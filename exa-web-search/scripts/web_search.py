#!/usr/bin/env python3
"""General web search preset — the plain `search_web` analog, powered by Exa.

No category, no domain lock — just semantic web search over the whole index.
Reach for a specialized skill (company / people / papers / code / finance /
personal-site / X) when you know the domain; use this for everything else.

Usage:
    python web_search.py "how do vector databases handle deletes" -n 10
    python web_search.py "best practices for prompt caching" --text
    python web_search.py "WebGPU compute shader tutorial" -n 12

Optional flags: -c CATEGORY, -t TYPE, --include-domains, --start-published,
--include-text, --text, --summary, --json. Run -h for the full list.
Requires EXA_API_KEY (env or repo-root .env). See exa-native-base for setup.
"""
import os
import sys

# Self-contained: exa_client.py is vendored next to this script, so this folder
# can be installed on its own (just copy exa-web-search/ and set EXA_API_KEY).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from exa_client import preset_cli  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(preset_cli(
        prog="web-search",
        description="General-purpose semantic web search via Exa (the search_web analog).",
        default_category=None,
        default_num=10,
    ))
