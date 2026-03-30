#!/usr/bin/env python3
"""
CLI: fetch PageSpeed Insights (Lighthouse) scores for one or more URLs.

Usage:
  python3 scripts/pagespeed_score.py <url> [mobile|desktop]
  python3 scripts/pagespeed_score.py <url1> <url2> ... [mobile|desktop]

If the last argument is "mobile" or "desktop", it is the strategy for all URLs.
Otherwise strategy defaults to "mobile".

Single URL: prints one JSON object (same shape as before).
Multiple URLs: prints {"strategy", "url_count", "results": [ ... ]}.

Environment:
  PAGESPEED_API_KEY — optional but strongly recommended (Google Cloud API key)
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from pagespeed_client import DEFAULT_TIMEOUT_S, fetch_pagespeed_raw, get_api_key  # noqa: E402
from pagespeed_normalize import normalize_psi_response  # noqa: E402


def _ensure_scheme(url: str) -> str:
    u = url.strip()
    if not u.startswith(("http://", "https://")):
        return "https://" + u
    return u


def _load_env_file() -> None:
    """Load simple KEY=VALUE pairs from repo .env if present."""
    repo_root = os.path.dirname(_SCRIPT_DIR)
    env_path = os.path.join(repo_root, ".env")
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw or raw.startswith("#") or "=" not in raw:
                continue
            key, value = raw.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def _parse_argv(argv: list[str]) -> tuple[list[str], str] | None:
    """
    Return (url_strings, strategy). None means caller should print usage and exit 0.
    Raises ValueError for invalid input (caller exit 2).
    """
    if not argv:
        return None
    last = argv[-1].lower().strip()
    if last in ("mobile", "desktop"):
        urls_raw = argv[:-1]
        strategy = last
    else:
        urls_raw = argv
        strategy = "mobile"
    if not urls_raw:
        raise ValueError("No URLs provided. Put one or more URLs before mobile|desktop.")
    urls = [_ensure_scheme(u) for u in urls_raw]
    return urls, strategy


def _run_one(page_url: str, strategy: str) -> dict:
    try:
        raw = fetch_pagespeed_raw(page_url, strategy=strategy, timeout_s=DEFAULT_TIMEOUT_S)
        return normalize_psi_response(raw, page_url=page_url, strategy=strategy)
    except urllib.error.HTTPError as e:
        return {
            "url": page_url,
            "strategy": strategy,
            "scores": None,
            "core_web_vitals": None,
            "supporting_metrics": None,
            "opportunities": [],
            "field_data": None,
            "error": {"message": str(e.reason) if e.reason else str(e), "code": getattr(e, "code", None)},
        }
    except urllib.error.URLError as e:
        return {
            "url": page_url,
            "strategy": strategy,
            "scores": None,
            "core_web_vitals": None,
            "supporting_metrics": None,
            "opportunities": [],
            "field_data": None,
            "error": {"message": str(e.reason) if getattr(e, "reason", None) else str(e), "code": None},
        }
    except json.JSONDecodeError as e:
        return {
            "url": page_url,
            "strategy": strategy,
            "scores": None,
            "core_web_vitals": None,
            "supporting_metrics": None,
            "opportunities": [],
            "field_data": None,
            "error": {"message": f"Invalid JSON from API: {e}", "code": None},
        }
    except Exception as e:  # noqa: BLE001
        return {
            "url": page_url,
            "strategy": strategy,
            "scores": None,
            "core_web_vitals": None,
            "supporting_metrics": None,
            "opportunities": [],
            "field_data": None,
            "error": {"message": str(e), "code": None},
        }


def main() -> None:
    _load_env_file()
    try:
        parsed = _parse_argv(sys.argv[1:])
    except ValueError as e:
        print(json.dumps({"error": {"message": str(e), "code": None}}, indent=2))
        sys.exit(2)

    if parsed is None:
        print(
            json.dumps(
                {
                    "usage": (
                        "python3 pagespeed_score.py <url> [mobile|desktop]\n"
                        "python3 pagespeed_score.py <url1> <url2> ... [mobile|desktop]"
                    ),
                    "examples": [
                        "python3 pagespeed_score.py https://example.com mobile",
                        "python3 pagespeed_score.py https://a.com https://b.com desktop",
                        "python3 pagespeed_score.py https://example.com",
                    ],
                    "note": "When omitted, strategy defaults to mobile. "
                    "If the last token is mobile or desktop, it applies to all URLs.",
                    "env": {"PAGESPEED_API_KEY": "Google API key (recommended)"},
                },
                indent=2,
            )
        )
        sys.exit(0)

    urls, strategy = parsed
    if not get_api_key():
        pass

    results = [_run_one(u, strategy) for u in urls]

    if len(urls) == 1:
        out = results[0]
    else:
        out = {"strategy": strategy, "url_count": len(urls), "results": results}

    print(json.dumps(out, indent=2, default=str))

    if any(r.get("error") and r["error"].get("message") for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
