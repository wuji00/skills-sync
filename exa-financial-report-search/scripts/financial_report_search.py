#!/usr/bin/env python3
"""Financial report preset — SEC filings, earnings, and annual reports via Exa.

Usage:
    python financial_report_search.py "Nvidia 10-K annual report fiscal 2024 revenue" -n 8
    python financial_report_search.py "Tesla Q3 2025 earnings results guidance" -n 8
    python financial_report_search.py "Stripe S-1 filing" -c pdf -n 5

Defaults to category="financial report". Encode the fiscal year and report type
(10-K, 10-Q, S-1, earnings) in the query; then deep-read with `exa.py contents`.
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
        prog="financial-report-search",
        description="Find SEC filings, earnings, and annual reports via Exa.",
        default_category="financial report",
        default_num=8,
    ))
