#!/usr/bin/env python3
"""
Google PageSpeed Insights API v5 client — fetches raw PSI JSON for a URL.

Environment:
  PAGESPEED_API_KEY — Google API key with PageSpeed Insights API enabled
    (https://console.cloud.google.com/apis/library/pagespeedonline.googleapis.com)

Uses stdlib only; verifies TLS (no cert bypass).
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

PSI_BASE = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

DEFAULT_TIMEOUT_S = 120.0
DEFAULT_RETRIES = 3
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def get_api_key() -> str | None:
    return os.environ.get("PAGESPEED_API_KEY") or os.environ.get("GOOGLE_PAGESPEED_API_KEY")


def build_psi_url(
    page_url: str,
    *,
    strategy: str = "mobile",
    api_key: str | None = None,
    categories: tuple[str, ...] = ("performance", "accessibility", "best-practices", "seo"),
) -> str:
    """Build full PageSpeed API URL with query parameters."""
    key = api_key if api_key is not None else get_api_key()
    params: list[tuple[str, str]] = [
        ("url", page_url),
        ("strategy", strategy),
    ]
    for cat in categories:
        params.append(("category", cat))
    if key:
        params.append(("key", key))
    qs = urllib.parse.urlencode(params)
    return f"{PSI_BASE}?{qs}"


def fetch_pagespeed_raw(
    page_url: str,
    *,
    strategy: str = "mobile",
    api_key: str | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    retries: int = DEFAULT_RETRIES,
) -> dict[str, Any]:
    """
    Call PageSpeed Insights API and return the full JSON object.

    Raises:
        ValueError: on invalid JSON or missing body
        urllib.error.HTTPError: after retries exhausted for non-retryable errors
        urllib.error.URLError: on network failure after retries
    """
    request_url = build_psi_url(page_url, strategy=strategy, api_key=api_key)
    last_error: Exception | None = None

    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                request_url,
                headers={"Accept": "application/json"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw)
        except urllib.error.HTTPError as e:
            last_error = e
            body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            if e.code in RETRYABLE_STATUS and attempt < retries - 1:
                wait = (2**attempt) + 0.5
                time.sleep(wait)
                continue
            snippet = body[:2000] if body else ""
            raise urllib.error.HTTPError(
                e.url,
                e.code,
                f"{e.reason}; body={snippet!r}",
                e.headers,
                None,
            ) from e
        except urllib.error.URLError as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep((2**attempt) + 0.5)
                continue
            raise

    if last_error:
        raise last_error
    raise RuntimeError("fetch_pagespeed_raw: unexpected empty retry loop")
