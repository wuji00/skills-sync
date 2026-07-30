#!/usr/bin/env python3
"""X / Twitter preset — search posts on x.com / twitter.com via Exa.

IMPORTANT: Exa retired the `tweet` category and X blocks crawlers, so X/Twitter
coverage is limited. This preset filters to x.com/twitter.com (client-side, via
--only-domains) so you never get off-domain noise — but results are often sparse
or empty. When empty, search the open web for discussion *about* the topic
instead (exa-company-research with -c news), or use a dedicated X API.

Usage:
    python x_search.py "Anthropic Claude launch reactions" -n 15
    python x_search.py "founder thread lessons scaling startup" -n 15

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
        prog="x-search",
        description="Search X/Twitter posts via Exa (limited coverage).",
        default_category=None,
        default_num=15,
        include_domains=["x.com", "twitter.com"],
        only_domains=["x.com", "twitter.com"],
        empty_note=("note: no x.com/twitter.com results — Exa's X coverage is limited "
                    "since the 'tweet' category was retired. Try searching the open web "
                    "for discussion about the topic (drop the domain filter), or use a "
                    "dedicated X/Twitter API."),
    ))
