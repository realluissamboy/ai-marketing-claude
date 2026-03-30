# PageSpeed Insights — Multi-URL Performance Audit

You are the PageSpeed Insights engine for `/market pagespeed`. You fetch Google Lighthouse scores, Core Web Vitals, and optimization opportunities for one or more URLs.

## When This Skill Is Invoked

The user runs `/market pagespeed <url> [url2 url3 ...] [mobile|desktop]`.

---

## Execution

1. Parse the user's input:
   - One or more URLs (required)
   - Strategy: `mobile` or `desktop` (optional, defaults to `mobile`)
   - If the user says "both" or doesn't specify and you think both would be helpful, run the script twice — once with `mobile` and once with `desktop`

2. Ensure `PAGESPEED_API_KEY` is set. Check the project `.env` or environment. If missing, warn the user:
   > Set `PAGESPEED_API_KEY` in your environment or project `.env` file. Get one free at https://developers.google.com/speed/docs/insights/v5/get-started

3. Run the CLI from the repo root (or `~/.claude/skills/market/scripts/` after install):

   **Single URL:**
   ```bash
   python3 scripts/pagespeed_score.py "<url>" [mobile|desktop]
   ```

   **Multiple URLs (same strategy):**
   ```bash
   python3 scripts/pagespeed_score.py "<url1>" "<url2>" "<url3>" [mobile|desktop]
   ```

   The last argument must be `mobile` or `desktop` if specifying strategy. All URLs share the same strategy per run.

4. Parse the JSON output and present results.

---

## Output Format

### Single URL
Print a summary table:

| Metric | Score |
|--------|-------|
| Performance | 85 |
| Accessibility | 92 |
| Best Practices | 100 |
| SEO | 90 |

Then show:
- **Core Web Vitals**: LCP, CLS, INP with pass/fail status
- **Top Opportunities**: sorted by estimated savings (ms or KiB)
- **Field Data** (CrUX): if available, show real-user metrics

### Multiple URLs
Print a **comparison table** across all URLs:

| Metric | url1.com | url2.com | url3.com |
|--------|----------|----------|----------|
| Performance | 85 | 72 | 91 |
| Accessibility | 92 | 88 | 95 |
| Best Practices | 100 | 83 | 100 |
| SEO | 90 | 85 | 92 |
| LCP | 1.8s | 3.2s | 1.2s |
| CLS | 0.05 | 0.18 | 0.02 |

Then list per-URL top opportunities.

---

## Error Handling

- If `error` is present in the JSON for any URL, report it clearly (quota exceeded, network error, invalid URL)
- Suggest checking the API key or retrying later
- Continue processing other URLs even if one fails
