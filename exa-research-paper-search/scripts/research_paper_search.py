#!/usr/bin/env python3
"""Research paper preset — semantic search over Exa's academic index.

Usage:
    python research_paper_search.py "sparse attention mechanisms for long context" -n 12
    python research_paper_search.py "diffusion models comprehensive survey review" -n 10
    python research_paper_search.py "large language model agents 2025 2026" -n 15

Defaults to category="research paper". To find seminal work, search for survey
papers first, then deep-read them for foundational references.
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
        prog="research-paper-search",
        description="Find academic papers, surveys, and preprints via Exa.",
        default_category="research paper",
        default_num=12,
    ))
