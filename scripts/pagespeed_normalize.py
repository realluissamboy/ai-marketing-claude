#!/usr/bin/env python3
"""
Normalize Google PageSpeed Insights v5 API responses into a stable audit schema.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _audit_metric(audits: dict[str, Any], audit_id: str) -> dict[str, Any] | None:
    a = audits.get(audit_id)
    if not isinstance(a, dict):
        return None
    out: dict[str, Any] = {"id": audit_id, "title": a.get("title"), "display_value": a.get("displayValue")}
    nv = a.get("numericValue")
    if nv is not None:
        try:
            out["numeric_value"] = float(nv)
        except (TypeError, ValueError):
            out["numeric_value"] = None
    out["score"] = a.get("score")
    nu = a.get("numericUnit")
    if nu:
        out["numeric_unit"] = nu
    return out


def _category_score(categories: dict[str, Any], key: str) -> int | None:
    c = categories.get(key)
    if not isinstance(c, dict):
        return None
    s = c.get("score")
    if s is None:
        return None
    try:
        return int(round(float(s) * 100))
    except (TypeError, ValueError):
        return None


def _band_timings_ms(value: float | None) -> str | None:
    if value is None:
        return None
    if value <= 2500:
        return "good"
    if value <= 4000:
        return "needs_improvement"
    return "poor"


def _band_cls(value: float | None) -> str | None:
    if value is None:
        return None
    if value <= 0.1:
        return "good"
    if value <= 0.25:
        return "needs_improvement"
    return "poor"


def _band_inp_ms(value: float | None) -> str | None:
    if value is None:
        return None
    if value <= 200:
        return "good"
    if value <= 500:
        return "needs_improvement"
    return "poor"


def _worst_band(bands: list[str | None]) -> str | None:
    order = {"good": 0, "needs_improvement": 1, "poor": 2}
    present = [b for b in bands if b]
    if not present:
        return None
    return max(present, key=lambda b: order.get(b, -1))


def _extract_opportunities(audits: dict[str, Any], limit: int = 15) -> list[dict[str, Any]]:
    rows: list[tuple[float, dict[str, Any]]] = []
    for aid, a in audits.items():
        if not isinstance(a, dict):
            continue
        details = a.get("details")
        if not isinstance(details, dict):
            continue
        savings_ms = details.get("overallSavingsMs")
        if savings_ms is None:
            continue
        try:
            ms = float(savings_ms)
        except (TypeError, ValueError):
            continue
        if ms <= 0:
            continue
        rows.append(
            (
                ms,
                {
                    "id": aid,
                    "title": a.get("title"),
                    "display_value": a.get("displayValue"),
                    "estimated_savings_ms": int(round(ms)),
                },
            )
        )
    rows.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in rows[:limit]]


def _extract_field_experience(loading_experience: Any) -> dict[str, Any] | None:
    """CrUX field data if present in PSI response."""
    if not isinstance(loading_experience, dict):
        return None
    metrics = loading_experience.get("metrics")
    if not isinstance(metrics, dict):
        return None
    slim: dict[str, Any] = {}
    for key in ("FIRST_CONTENTFUL_PAINT_MS", "LARGEST_CONTENTFUL_PAINT_MS", "CUMULATIVE_LAYOUT_SHIFT_SCORE"):
        m = metrics.get(key)
        if isinstance(m, dict):
            slim[key.lower()] = {
                "percentile": m.get("percentile"),
                "distributions": m.get("distributions"),
            }
    return slim or None


def normalize_psi_response(
    raw: dict[str, Any],
    *,
    page_url: str,
    strategy: str,
) -> dict[str, Any]:
    """
    Build stable audit payload from raw PSI API JSON.

    On API error responses, `raw` may contain `error` only — pass through with schema wrapper.
    """
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if "error" in raw and "lighthouseResult" not in raw:
        err = raw.get("error", {})
        return {
            "url": page_url,
            "strategy": strategy,
            "fetched_at": fetched_at,
            "scores": None,
            "core_web_vitals": None,
            "supporting_metrics": None,
            "opportunities": [],
            "field_data": None,
            "error": {
                "message": err.get("message") if isinstance(err, dict) else str(err),
                "code": err.get("code") if isinstance(err, dict) else None,
            },
        }

    lh = raw.get("lighthouseResult")
    if not isinstance(lh, dict):
        return {
            "url": page_url,
            "strategy": strategy,
            "fetched_at": fetched_at,
            "scores": None,
            "core_web_vitals": None,
            "supporting_metrics": None,
            "opportunities": [],
            "field_data": _extract_field_experience(raw.get("loadingExperience")),
            "error": {"message": "Missing lighthouseResult in API response", "code": None},
        }

    categories = lh.get("categories")
    if not isinstance(categories, dict):
        categories = {}

    audits = lh.get("audits")
    if not isinstance(audits, dict):
        audits = {}

    scores = {
        "performance": _category_score(categories, "performance"),
        "accessibility": _category_score(categories, "accessibility"),
        "best_practices": _category_score(categories, "best-practices"),
        "seo": _category_score(categories, "seo"),
    }

    lcp_raw = _audit_metric(audits, "largest-contentful-paint")
    cls_raw = _audit_metric(audits, "cumulative-layout-shift")
    inp_raw = _audit_metric(audits, "interaction-to-next-paint")
    if inp_raw is None:
        inp_raw = _audit_metric(audits, "experimental-interaction-to-next-paint")

    lcp_ms = lcp_raw.get("numeric_value") if lcp_raw else None
    cls_val = cls_raw.get("numeric_value") if cls_raw else None
    inp_ms = inp_raw.get("numeric_value") if inp_raw else None

    lcp_band = _band_timings_ms(lcp_ms)
    cls_band = _band_cls(cls_val)
    inp_band = _band_inp_ms(inp_ms)

    cwv_status = _worst_band([lcp_band, cls_band, inp_band])
    cwv_note = None
    if inp_ms is None:
        cwv_note = "Lab INP not reported by Lighthouse for this run; assessment uses LCP and CLS only."

    core_web_vitals: dict[str, Any] = {
        "lcp_ms": int(round(lcp_ms)) if lcp_ms is not None else None,
        "lcp_status": lcp_band,
        "cls": cls_val,
        "cls_status": cls_band,
        "inp_ms": int(round(inp_ms)) if inp_ms is not None else None,
        "inp_status": inp_band,
        "cwv_overall_status": cwv_status,
        "notes": cwv_note,
        "audits": {
            k: v for k, v in {"lcp": lcp_raw, "cls": cls_raw, "inp": inp_raw}.items() if v
        },
    }

    fcp = _audit_metric(audits, "first-contentful-paint")
    si = _audit_metric(audits, "speed-index")
    ttfb = _audit_metric(audits, "server-response-time")
    tbt = _audit_metric(audits, "total-blocking-time")

    supporting_metrics = {
        "fcp_ms": int(round(fcp["numeric_value"])) if fcp and fcp.get("numeric_value") is not None else None,
        "speed_index_ms": int(round(si["numeric_value"])) if si and si.get("numeric_value") is not None else None,
        "ttfb_ms": int(round(ttfb["numeric_value"])) if ttfb and ttfb.get("numeric_value") is not None else None,
        "tbt_ms": int(round(tbt["numeric_value"])) if tbt and tbt.get("numeric_value") is not None else None,
        "audits": {k: v for k, v in {"fcp": fcp, "speed_index": si, "ttfb": ttfb, "tbt": tbt}.items() if v},
    }

    opportunities = _extract_opportunities(audits)

    final_url = lh.get("finalUrl") or raw.get("id") or page_url

    return {
        "url": page_url,
        "final_url": final_url,
        "strategy": strategy,
        "fetched_at": fetched_at,
        "scores": scores,
        "core_web_vitals": core_web_vitals,
        "supporting_metrics": supporting_metrics,
        "opportunities": opportunities,
        "field_data": _extract_field_experience(raw.get("loadingExperience")),
        "error": None,
    }
