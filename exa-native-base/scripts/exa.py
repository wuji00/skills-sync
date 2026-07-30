#!/usr/bin/env python3
"""Generic Exa CLI — the full client (search / contents / answer / similar).

This is the un-specialized entry point. The use-case skills wrap it with
sensible defaults, but you can always drive the raw client from here:

    python exa.py search "category:company AI agents for sales" -n 10
    python exa.py search "WebGPU compute shaders tutorial" --text
    python exa.py contents https://exa.ai --text
    python exa.py answer "Who founded Exa?"
    python exa.py similar https://stripe.com -n 10

Requires EXA_API_KEY (env or a .env at the repo root).
"""
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not os.path.isdir(os.path.join(_d, "_shared")):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "_shared"))

from exa_client import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
