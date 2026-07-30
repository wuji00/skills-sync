#!/usr/bin/env python3
"""Personal site preset — find personal blogs, portfolios, and homepages via Exa.

Usage:
    python personal_site_search.py "machine learning engineer personal blog" -n 10
    python personal_site_search.py "indie hacker building in public portfolio" -n 12
    python personal_site_search.py "Andrej Karpathy personal site essays" -n 5

Defaults to category="personal site". Great for finding a person's own writing
(vs. press about them) and for relationship/terminology detection.
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
        prog="personal-site-search",
        description="Find personal blogs, portfolios, and homepages via Exa.",
        default_category="personal site",
        default_num=10,
    ))
