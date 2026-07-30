#!/usr/bin/env python3
"""Exa API client + CLI — zero dependencies (Python 3.8+ stdlib only).

This is the shared engine every Exa skill in this repo calls. It wraps the Exa
REST API (https://api.exa.ai) so a skill never needs an MCP server: the only
requirement is an EXA_API_KEY in the environment (or in a .env file at the repo
root). Get a key at https://dashboard.exa.ai/api-keys.

Subcommands:
    search    Semantic search. Supports categories, domain/date/text filters,
              and optional page contents (--text / --highlights / --summary).
    contents  Fetch clean page contents for known URLs.
    answer    Ask a question; Exa returns a cited answer.
    similar   Find pages similar to a URL.

Output is human/agent-friendly Markdown by default, or raw JSON with --json.
Every search prints a trailing `sources_reviewed: N` line so an orchestrating
agent can tally coverage across calls.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://api.exa.ai"

# Categories accepted by the Exa /search endpoint (verified live, 2026-06).
# NOTE: the old "tweet" category was removed by Exa — search X/Twitter with
# --include-domains x.com,twitter.com instead (the exa-x-search skill does this).
VALID_CATEGORIES = {
    "company",
    "research paper",
    "news",
    "pdf",
    "github",
    "personal site",
    "linkedin profile",
    "financial report",
}


# --------------------------------------------------------------------------- #
# Key / .env handling
# --------------------------------------------------------------------------- #
def _load_dotenv() -> None:
    """Populate os.environ from the nearest .env file, walking up from CWD and
    from this file's directory. Never overwrites a value already in the env."""
    seen = set()
    for start in (os.getcwd(), os.path.dirname(os.path.abspath(__file__))):
        d = start
        while d and d not in seen:
            seen.add(d)
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
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent


def get_api_key() -> str:
    if not os.environ.get("EXA_API_KEY"):
        _load_dotenv()
    key = os.environ.get("EXA_API_KEY", "").strip()
    if not key:
        sys.exit(
            "ERROR: EXA_API_KEY is not set.\n"
            "  Set it in your shell:  export EXA_API_KEY=your-key\n"
            "  or create a .env file:  echo 'EXA_API_KEY=your-key' > .env\n"
            "  Get a key at https://dashboard.exa.ai/api-keys"
        )
    return key


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
class ExaError(RuntimeError):
    pass


def _post(path: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/{path.lstrip('/')}",
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-api-key": get_api_key(),
            "User-Agent": "codealive-exa-skills/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        msg = body
        try:
            msg = json.loads(body).get("error", body)
        except Exception:
            pass
        if e.code == 401:
            raise ExaError("401 Unauthorized — EXA_API_KEY is missing or invalid. "
                           "Get one at https://dashboard.exa.ai/api-keys") from None
        if e.code == 429:
            raise ExaError("429 Rate limited by Exa — slow down or upgrade your plan.") from None
        raise ExaError(f"HTTP {e.code} from Exa: {msg}") from None
    except urllib.error.URLError as e:
        raise ExaError(f"Network error talking to Exa: {e.reason}") from None


# --------------------------------------------------------------------------- #
# API methods
# --------------------------------------------------------------------------- #
def _contents_block(text: bool, highlights: bool, summary: bool, livecrawl: str | None) -> dict | None:
    block: dict = {}
    if text:
        block["text"] = {"maxCharacters": 2000}
    if highlights:
        block["highlights"] = {"numSentences": 3, "highlightsPerUrl": 2}
    if summary:
        block["summary"] = True
    if livecrawl:
        block["livecrawl"] = livecrawl  # "never" | "fallback" | "always" | "preferred"
    return block or None


def search(query, num_results=10, category=None, search_type="auto",
           include_domains=None, exclude_domains=None,
           start_published=None, end_published=None,
           include_text=None, exclude_text=None,
           text=False, highlights=True, summary=False, livecrawl=None,
           only_domains=None) -> dict:
    include_domains = list(include_domains or [])

    # Defensive: the "tweet" category was retired — transparently route to X/Twitter domains.
    if category == "tweet":
        category = None
        for d in ("x.com", "twitter.com"):
            if d not in include_domains:
                include_domains.append(d)
        print("note: 'tweet' category is retired; searching x.com/twitter.com instead.",
              file=sys.stderr)

    if category and category not in VALID_CATEGORIES:
        print(f"note: '{category}' is not a known Exa category; sending it anyway. "
              f"Known: {', '.join(sorted(VALID_CATEGORIES))}", file=sys.stderr)

    payload: dict = {"query": query, "numResults": int(num_results), "type": search_type}
    if category:
        payload["category"] = category
    if include_domains:
        payload["includeDomains"] = include_domains
    if exclude_domains:
        payload["excludeDomains"] = list(exclude_domains)
    if start_published:
        payload["startPublishedDate"] = start_published
    if end_published:
        payload["endPublishedDate"] = end_published
    if include_text:
        payload["includeText"] = [include_text] if isinstance(include_text, str) else include_text
    if exclude_text:
        payload["excludeText"] = [exclude_text] if isinstance(exclude_text, str) else exclude_text
    cb = _contents_block(text, highlights, summary, livecrawl)
    if cb:
        payload["contents"] = cb
    resp = _post("search", payload)

    # Client-side domain enforcement. Exa's includeDomains is a soft filter for
    # sparsely-indexed domains (notably x.com/twitter.com, which Exa can no longer
    # crawl well), so it sometimes returns off-domain pages. only_domains drops
    # anything not actually hosted on the requested domains.
    if only_domains:
        suffixes = tuple(d.lower().lstrip(".") for d in only_domains)
        kept = []
        for r in resp.get("results", []):
            host = urllib.parse.urlparse(r.get("url", "")).netloc.lower()
            host = host[4:] if host.startswith("www.") else host
            if any(host == s or host.endswith("." + s) for s in suffixes):
                kept.append(r)
        resp["results"] = kept
    return resp


def contents(urls, text=True, highlights=False, summary=False, livecrawl="fallback") -> dict:
    payload = {"urls": list(urls)}
    cb = _contents_block(text, highlights, summary, livecrawl)
    if cb:
        payload.update(cb)
    return _post("contents", payload)


def answer(query, text=False) -> dict:
    return _post("answer", {"query": query, "text": bool(text)})


def find_similar(url, num_results=10, text=False, highlights=True) -> dict:
    payload = {"url": url, "numResults": int(num_results)}
    cb = _contents_block(text, highlights, False, None)
    if cb:
        payload["contents"] = cb
    return _post("findSimilar", payload)


# --------------------------------------------------------------------------- #
# Formatting
# --------------------------------------------------------------------------- #
def _fmt_result(i: int, r: dict) -> str:
    title = (r.get("title") or "(no title)").strip()
    url = r.get("url", "")
    line = f"{i}. [{title}]({url})"
    meta = []
    if r.get("author"):
        meta.append(str(r["author"])[:60])
    if r.get("publishedDate"):
        meta.append(str(r["publishedDate"])[:10])
    if meta:
        line += f"\n   _{' · '.join(meta)}_"
    snippet = ""
    if r.get("highlights"):
        snippet = " … ".join(h.strip() for h in r["highlights"])
    elif r.get("summary"):
        snippet = r["summary"].strip()
    elif r.get("text"):
        snippet = r["text"].strip().replace("\n", " ")
    if snippet:
        line += f"\n   {snippet[:400].strip()}"
    return line


def format_results(resp: dict, header: str | None = None) -> str:
    results = resp.get("results", [])
    out = []
    if header:
        out.append(f"## {header}\n")
    if not results:
        out.append("_No results. Try a longer, more specific query or a different angle._")
    else:
        out.extend(_fmt_result(i, r) for i, r in enumerate(results, 1))
    out.append(f"\nsources_reviewed: {len(results)}")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Preset CLI — used by each skill's thin wrapper script
# --------------------------------------------------------------------------- #
def preset_cli(*, prog, description, default_category=None, default_num=10,
               include_domains=None, only_domains=None, empty_note=None, argv=None) -> int:
    """A ready-made `search` CLI with skill-specific defaults baked in.

    Each skill ships an ~8-line wrapper that calls this. Users can still
    override the category, result count, type, domains, dates, etc."""
    ap = argparse.ArgumentParser(prog=prog, description=description)
    ap.add_argument("query")
    ap.add_argument("-n", "--num", type=int, default=default_num, help="numResults")
    ap.add_argument("-c", "--category", default=default_category,
                    help=f"override category (default: {default_category or 'none'})")
    ap.add_argument("-t", "--type", default="auto",
                    choices=["auto", "fast", "deep", "deep-reasoning", "instant"])
    ap.add_argument("--include-domains", default=None, help="comma-separated (adds to preset)")
    ap.add_argument("--exclude-domains", default=None, help="comma-separated")
    ap.add_argument("--start-published", default=None, help="ISO date")
    ap.add_argument("--end-published", default=None, help="ISO date")
    ap.add_argument("--include-text", default=None, help="single phrase that must appear")
    ap.add_argument("--text", action="store_true", help="include page text")
    ap.add_argument("--summary", action="store_true", help="LLM summary per result")
    ap.add_argument("--json", action="store_true", help="raw JSON output")
    args = ap.parse_args(argv)

    inc = list(include_domains or []) + (_csv(args.include_domains) or [])
    try:
        resp = search(
            args.query, num_results=args.num, category=args.category, search_type=args.type,
            include_domains=inc or None, exclude_domains=_csv(args.exclude_domains),
            only_domains=only_domains, start_published=args.start_published,
            end_published=args.end_published, include_text=args.include_text,
            text=args.text, highlights=not args.text, summary=args.summary,
        )
    except ExaError as e:
        sys.exit(f"ERROR: {e}")
    if empty_note and not resp.get("results"):
        print(empty_note, file=sys.stderr)
    _emit(resp, args.json, header=f'{prog}: "{args.query}"')
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _emit(resp: dict, as_json: bool, header: str | None = None) -> None:
    if as_json:
        print(json.dumps(resp, indent=2, ensure_ascii=False))
    else:
        print(format_results(resp, header))


def _add_search_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("query")
    p.add_argument("-n", "--num", type=int, default=10, help="numResults (1-25 recommended)")
    p.add_argument("-c", "--category", default=None, help=f"one of: {', '.join(sorted(VALID_CATEGORIES))}")
    p.add_argument("-t", "--type", dest="type", default="auto",
                   choices=["auto", "fast", "deep", "deep-reasoning", "instant"], help="search type")
    p.add_argument("--include-domains", default=None, help="comma-separated")
    p.add_argument("--exclude-domains", default=None, help="comma-separated")
    p.add_argument("--only-domains", default=None,
                   help="comma-separated; drop any result not actually on these domains (client-side)")
    p.add_argument("--start-published", default=None, help="ISO date, e.g. 2025-01-01")
    p.add_argument("--end-published", default=None, help="ISO date")
    p.add_argument("--include-text", default=None, help="single phrase that must appear")
    p.add_argument("--exclude-text", default=None, help="single phrase to exclude")
    p.add_argument("--text", action="store_true", help="include page text")
    p.add_argument("--no-highlights", action="store_true", help="disable highlight snippets")
    p.add_argument("--summary", action="store_true", help="include an LLM summary per result")
    p.add_argument("--livecrawl", default=None, choices=["never", "fallback", "always", "preferred"])
    p.add_argument("--json", action="store_true", help="raw JSON output")


def _csv(v):
    return [x.strip() for x in v.split(",") if x.strip()] if v else None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="exa", description="Exa API client (no MCP required).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="semantic web search")
    _add_search_args(s)

    c = sub.add_parser("contents", help="fetch page contents for URLs")
    c.add_argument("urls", nargs="+")
    c.add_argument("--no-text", action="store_true")
    c.add_argument("--highlights", action="store_true")
    c.add_argument("--summary", action="store_true")
    c.add_argument("--json", action="store_true")

    a = sub.add_parser("answer", help="ask a question, get a cited answer")
    a.add_argument("query")
    a.add_argument("--text", action="store_true", help="include source text")
    a.add_argument("--json", action="store_true")

    sim = sub.add_parser("similar", help="find pages similar to a URL")
    sim.add_argument("url")
    sim.add_argument("-n", "--num", type=int, default=10)
    sim.add_argument("--text", action="store_true")
    sim.add_argument("--json", action="store_true")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.cmd == "search":
            resp = search(
                args.query, num_results=args.num, category=args.category, search_type=args.type,
                include_domains=_csv(args.include_domains), exclude_domains=_csv(args.exclude_domains),
                start_published=args.start_published, end_published=args.end_published,
                include_text=args.include_text, exclude_text=args.exclude_text,
                text=args.text, highlights=not args.no_highlights, summary=args.summary,
                livecrawl=args.livecrawl, only_domains=_csv(args.only_domains),
            )
            _emit(resp, args.json, header=f'Search: "{args.query}"')
        elif args.cmd == "contents":
            resp = contents(args.urls, text=not args.no_text, highlights=args.highlights, summary=args.summary)
            _emit(resp, args.json, header="Contents")
        elif args.cmd == "answer":
            resp = answer(args.query, text=args.text)
            if args.json:
                print(json.dumps(resp, indent=2, ensure_ascii=False))
            else:
                print(resp.get("answer", "(no answer)"))
                cites = resp.get("citations") or []
                if cites:
                    print("\nCitations:")
                    for i, c in enumerate(cites, 1):
                        print(f"  [{i}] {c.get('title','')} — {c.get('url','')}")
        elif args.cmd == "similar":
            resp = find_similar(args.url, num_results=args.num, text=args.text)
            _emit(resp, args.json, header=f"Similar to {args.url}")
    except ExaError as e:
        sys.exit(f"ERROR: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
