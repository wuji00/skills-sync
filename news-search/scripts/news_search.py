#!/usr/bin/env python3
"""Brave Search News API CLI — usage:

    python scripts/news_search.py "cybersecurity" -n 5 --freshness pd

Requires BRAVE_SEARCH_API_KEY in environment or a .env file at the repo root.
Proxy is auto-detected from HTTPS_PROXY / HTTP_PROXY, or from common local
ports (7890, 10808). Get a key at https://api.search.brave.com.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import urllib.request
from urllib.error import HTTPError

API_BASE = "https://api.search.brave.com/res/v1/news/search"


def _load_dotenv() -> None:
    """Load nearest .env walking up from CWD."""
    start = os.getcwd()
    d = start
    while d and d != os.path.dirname(d):
        envpath = os.path.join(d, ".env")
        if os.path.isfile(envpath):
            try:
                with open(envpath, encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, _, v = line.partition("=")
                        os.environ.setdefault(k.strip(), v.strip().strip("'\""))
            except OSError:
                pass
            return
        d = os.path.dirname(d)


def _detect_proxy() -> str | None:
    """Return a working http proxy URL or None."""
    for env in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        if os.environ.get(env):
            return os.environ[env]
    for port in (7890, 10808, 7897):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return f"http://127.0.0.1:{port}"
    return None


def get_api_key() -> str:
    if not os.environ.get("BRAVE_SEARCH_API_KEY"):
        _load_dotenv()
    key = os.environ.get("BRAVE_SEARCH_API_KEY", "").strip()
    if not key:
        sys.exit(
            "ERROR: BRAVE_SEARCH_API_KEY is not set.\n"
            "  Set it in your shell:  export BRAVE_SEARCH_API_KEY=your-key\n"
            "  or create a .env file:  echo 'BRAVE_SEARCH_API_KEY=your-key' > .env\n"
            "  Get a key at https://api.search.brave.com"
        )
    return key


def search(
    query: str,
    count: int = 20,
    freshness: str | None = None,
    country: str = "US",
    safesearch: str = "strict",
    extra_snippets: bool = False,
) -> dict:
    params = {
        "q": query,
        "count": count,
        "country": country,
        "safesearch": safesearch,
        "spellcheck": "true",
    }
    if freshness:
        params["freshness"] = freshness
    if extra_snippets:
        params["extra_snippets"] = "true"

    url = f"{API_BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "X-Subscription-Token": get_api_key(),
            "User-Agent": "codealive-news-search/1.0",
        },
    )

    proxy = _detect_proxy()
    opener = urllib.request.build_opener()
    if proxy:
        opener.add_handler(urllib.request.ProxyHandler({"https": proxy, "http": proxy}))

    try:
        with opener.open(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        msg = body
        try:
            msg = json.loads(body).get("error", body)
        except Exception:
            pass
        sys.exit(f"ERROR {e.code}: {msg}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Brave Search News API CLI")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-n", "--count", type=int, default=10, help="Number of results (1-50)")
    parser.add_argument("--freshness", default="pd", help="pd/pw/pm/py or YYYY-MM-DDtoYYYY-MM-DD")
    parser.add_argument("--country", default="US", help="2-letter country code")
    parser.add_argument("--safesearch", default="strict", choices=["off", "moderate", "strict"])
    parser.add_argument("--extra-snippets", action="store_true", help="Include extra snippets")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    data = search(
        query=args.query,
        count=min(max(args.count, 1), 50),
        freshness=args.freshness,
        country=args.country,
        safesearch=args.safesearch,
        extra_snippets=args.extra_snippets,
    )

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    print(f"## News Search: \"{data['query']['original']}\"\n")
    for i, r in enumerate(data.get("results", []), 1):
        print(f"{i}. [{r['title']}]({r['url']})")
        if r.get("age"):
            print(f"   _{r['age']}_")
        if r.get("description"):
            print(f"   {r['description']}")
        if r.get("extra_snippets"):
            for snippet in r["extra_snippets"]:
                print(f"   > {snippet}")
        print()
    print(f"sources_reviewed: {len(data.get('results', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
