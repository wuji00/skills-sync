#!/usr/bin/env python3
"""Code context preset — find code, APIs, docs, repos, and error fixes via Exa.

Always include the programming language and framework/library in your query.

Usage:
    python code_context.py "Stripe API create subscription Node.js code example" -n 8
    python code_context.py "React hydration mismatch server client fix" -n 10
    python code_context.py "production-ready vector database in Rust" -c github -n 10

No default category (most code/docs/error queries live on the open web).
Add -c github to discover repositories.
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
        prog="code-context",
        description="Find code examples, API usage, docs, and repos via Exa.",
        default_category=None,
        default_num=8,
    ))
