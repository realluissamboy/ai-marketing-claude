#!/usr/bin/env python3
"""
CLI: fetch PageSpeed Insights (Lighthouse) scores for a URL.

Usage:
  python3 scripts/pagespeed_score.py <url> [mobile|desktop]

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

from pagespeed_client import DEFAULT_TIMEOUT_S, fetch_pagespeed_raw, get_api_key
from pagespeed_normalize import normalize_psi_response


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


def main() -> None:
    _load_env_file()
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "usage": "python3 pagespeed_score.py <url> [mobile|desktop]",
                    "example": "python3 pagespeed_score.py https://example.com mobile",
                    "env": {"PAGESPEED_API_KEY": "Google API key (recommended)"},
                    "note": "PageSpeed API may accept unauthenticated requests with low quota.",
                },
                indent=2,
            )
        )
        sys.exit(0)

    page_url = _ensure_scheme(sys.argv[1])
    strategy = "mobile"
    if len(sys.argv) > 2:
        s = sys.argv[2].lower().strip()
        if s in ("mobile", "desktop"):
            strategy = s
        else:
            print(
                json.dumps(
                    {
                        "error": {
                            "message": f"Invalid strategy {sys.argv[2]!r}; use mobile or desktop",
                            "code": None,
                        }
                    },
                    indent=2,
                )
            )
            sys.exit(2)

    if not get_api_key():
        # Still attempt request — Google allows limited unauthenticated use
        pass

    try:
        raw = fetch_pagespeed_raw(page_url, strategy=strategy, timeout_s=DEFAULT_TIMEOUT_S)
        payload = normalize_psi_response(raw, page_url=page_url, strategy=strategy)
    except urllib.error.HTTPError as e:
        payload = {
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
        payload = {
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
        payload = {
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
        payload = {
            "url": page_url,
            "strategy": strategy,
            "scores": None,
            "core_web_vitals": None,
            "supporting_metrics": None,
            "opportunities": [],
            "field_data": None,
            "error": {"message": str(e), "code": None},
        }

    print(json.dumps(payload, indent=2, default=str))
    if payload.get("error") and payload["error"].get("message"):
        sys.exit(1)


if __name__ == "__main__":
    main()
