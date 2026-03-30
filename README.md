<p align="center">
  <img src="banner.svg" alt="AI Marketing Suite for Claude Code" width="100%">
</p>

# AI Marketing Suite for Claude Code

A comprehensive marketing analysis and automation skill system for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Audit any website's marketing, generate copy, build email sequences, create content calendars, analyze competitors, and produce client-ready PDF reports — all from your terminal.

**Built for entrepreneurs, agency builders, and solopreneurs who want to sell marketing services powered by AI.**

---

## What This Does

Type a command in Claude Code and get instant, actionable marketing analysis:

```
> /market audit https://calendly.com

Launching 5 parallel agents...
✓ Content & Messaging Analysis     — Score: 72/100
✓ Conversion Optimization          — Score: 58/100
✓ SEO & Discoverability            — Score: 81/100
✓ Competitive Positioning          — Score: 64/100
✓ Brand & Trust                    — Score: 76/100
✓ Growth & Strategy                — Score: 61/100

Overall Marketing Score: 69/100

Full report saved to MARKETING-AUDIT.md
```

---

## Installation

### One-Command Install

```bash
curl -fsSL https://raw.githubusercontent.com/zubair-trabzada/ai-marketing-claude/main/install.sh | bash
```

### Manual Install

```bash
git clone https://github.com/zubair-trabzada/ai-marketing-claude.git
cd ai-marketing-claude
./install.sh
```

### Optional: PDF Report Support

```bash
pip install reportlab
```

### Optional: PageSpeed Insights (Lighthouse scores)

`/market audit` can use **Google PageSpeed Insights API** for real Lighthouse category scores and lab Core Web Vitals.

1. Create an API key in [Google Cloud Console](https://console.cloud.google.com/) and enable **PageSpeed Insights API**.
2. Export the key and run (from repo root):

```bash
export PAGESPEED_API_KEY="your-api-key-here"
python3 scripts/pagespeed_score.py https://example.com mobile
python3 scripts/pagespeed_score.py https://example.com desktop
# Multiple URLs share the same strategy (default mobile; or put mobile|desktop last):
python3 scripts/pagespeed_score.py https://a.com https://b.com desktop
```

The CLI prints JSON with `scores` (performance, accessibility, best-practices, seo), `core_web_vitals`, `supporting_metrics`, `opportunities`, and optional CrUX `field_data`. On failure, an `error` object is included instead. For **multiple URLs**, output is `{"strategy", "url_count", "results": [ ... ]}` where each item matches the single-URL shape.

---

## Commands

| Command | What It Does |
|---------|-------------|
| `/market audit <url>` | Full marketing audit with 5 parallel agents |
| `/market quick <url>` | 60-second marketing snapshot |
| `/market copy <url>` | Generate optimized copy with before/after examples |
| `/market emails <topic>` | Generate complete email sequences |
| `/market social <topic>` | 30-day social media content calendar |
| `/market ads <url>` | Ad creative and copy for all platforms |
| `/market funnel <url>` | Sales funnel analysis and optimization |
| `/market competitors <url>` | Competitive intelligence report |
| `/market landing <url>` | Landing page CRO analysis |
| `/market launch <product>` | Product launch playbook |
| `/market proposal <client>` | Client proposal generator |
| `/market report <url>` | Full marketing report (Markdown) |
| `/market report-pdf <url>` | Professional marketing report (PDF) |
| `/market seo <url>` | SEO content audit |
| `/market brand <url>` | Brand voice analysis and guidelines |
| `/market pagespeed <urls>` | PageSpeed Insights for one or more URLs |

---

## Architecture

```
ai-marketing-claude/
├── market/SKILL.md                     # Main orchestrator (routes all /market commands)
│
├── skills/                             # 14 sub-skills
│   ├── market-audit/SKILL.md           # Full audit orchestration
│   ├── market-copy/SKILL.md            # Copywriting analysis & generation
│   ├── market-emails/SKILL.md          # Email sequence generation
│   ├── market-social/SKILL.md          # Social media content calendar
│   ├── market-ads/SKILL.md             # Ad creative & copy
│   ├── market-funnel/SKILL.md          # Funnel analysis & optimization
│   ├── market-competitors/SKILL.md     # Competitive intelligence
│   ├── market-landing/SKILL.md         # Landing page CRO
│   ├── market-launch/SKILL.md          # Launch playbook generation
│   ├── market-proposal/SKILL.md        # Client proposal generator
│   ├── market-report/SKILL.md          # Marketing report (Markdown)
│   ├── market-report-pdf/SKILL.md      # Marketing report (PDF)
│   ├── market-seo/SKILL.md             # SEO content audit
│   └── market-brand/SKILL.md           # Brand voice analysis
│
├── agents/                             # 5 parallel subagents
│   ├── market-content.md               # Content & messaging analysis
│   ├── market-conversion.md            # CRO & funnel optimization
│   ├── market-competitive.md           # Competitive positioning
│   ├── market-technical.md             # Technical SEO & tracking
│   └── market-strategy.md              # Brand, pricing & growth strategy
│
├── scripts/                            # Python utility scripts
│   ├── analyze_page.py                 # Webpage marketing analysis
│   ├── competitor_scanner.py           # Competitor website scanner
│   ├── social_calendar.py              # Social content calendar generator
│   ├── generate_pdf_report.py          # PDF report generator
│   ├── pagespeed_client.py             # PageSpeed Insights API client
│   ├── pagespeed_normalize.py          # PSI → stable audit JSON schema
│   └── pagespeed_score.py              # CLI: Lighthouse/PageSpeed scores
│
├── templates/                          # Marketing templates
│   ├── email-welcome.md                # Welcome email sequence (5 emails)
│   ├── email-nurture.md                # Lead nurture sequence (6 emails)
│   ├── email-launch.md                 # Product launch sequence (8 emails)
│   ├── proposal-template.md            # Client proposal template
│   ├── content-calendar.md             # 30-day content calendar
│   └── launch-checklist.md             # Launch checklist
│
├── install.sh                          # One-command installer
├── uninstall.sh                        # Clean uninstaller
├── requirements.txt                    # Python dependencies
└── LICENSE                             # MIT License
```

---

## Scoring Methodology

The full marketing audit scores websites across 6 dimensions:

| Category | Weight | What It Measures |
|----------|--------|------------------|
| Content & Messaging | 25% | Copy quality, value props, headlines, CTAs |
| Conversion Optimization | 20% | Funnels, forms, social proof, friction, urgency |
| SEO & Discoverability | 20% | On-page SEO, technical SEO, content structure |
| Competitive Positioning | 15% | Differentiation, market awareness, alternatives |
| Brand & Trust | 10% | Design quality, trust signals, authority |
| Growth & Strategy | 10% | Pricing, acquisition channels, retention |

**Overall Marketing Score** = Weighted average of all categories (0-100)

---

## How It Works

1. **You type a command** — e.g., `/market audit https://example.com`
2. **Claude reads the skill files** — they tell Claude exactly how to analyze the site
3. **5 subagents launch in parallel** — each one analyzes a different dimension
4. **Python scripts run** — automated page analysis, competitor scanning
5. **Results are compiled** — into a scored, prioritized, actionable report
6. **Output is saved** — as a Markdown file or professional PDF

---

## Tool Reference: Data Sources & How Each Tool Works

Every tool in this suite derives its analysis from a small set of data sources — **no proprietary datasets or paid APIs are required by default**.

### Shared Data Sources

| Source | What It Provides |
|--------|-----------------|
| **WebFetch** (built-in) | Raw HTML of target pages — the primary input for almost everything |
| **Google PageSpeed Insights API** | Lighthouse scores, Core Web Vitals, CrUX field data *(optional, needs `PAGESPEED_API_KEY`)* |
| **robots.txt / meta tags** | AI crawler access rules (used by GEO tools) |
| **llms.txt** | Emerging standard for helping AI systems understand site structure |
| **Python scripts** (`scripts/`) | Parsing, normalization, and report generation — stdlib only, no pip deps |

### Market Tools

| Tool | What It Does | Where It Gets Its Data |
|------|-------------|------------------------|
| `market-audit` | Full marketing audit — launches 5 parallel subagents | WebFetch (homepage + up to 5 key pages) + optional PageSpeed API |
| `market-copy` | Scores headlines, value props, CTAs; generates rewrites using PAS/AIDA frameworks | WebFetch — parses H1-H6, meta tags, buttons from page HTML |
| `market-landing` | 7-point CRO analysis (hero, value prop, social proof, features, objections, urgency, mobile) | WebFetch (full landing page HTML) |
| `market-funnel` | Maps entire conversion flow, scores each step on clarity/friction/trust | WebFetch — follows the funnel path from homepage through signup |
| `market-competitors` | Identifies 3-5 direct + indirect competitors, builds SWOT and positioning map | WebFetch + `competitor_scanner.py` (extracts pricing, features, CTAs) |
| `market-seo` | On-page SEO audit (keywords, meta, structure, technical) | WebFetch (page content + HTML structure) |
| `market-pagespeed` | Multi-URL performance comparison with Core Web Vitals | Google PageSpeed Insights API v5 via `pagespeed_score.py` |
| `market-brand` | Analyzes brand voice dimensions (formality, emotion, authority) | WebFetch (existing copy analysis) |
| `market-emails` | Generates 5-12 email sequences (welcome, nurture, launch, etc.) | WebFetch (business context) + user-provided topic |
| `market-social` | 30-day content calendar | WebFetch + `social_calendar.py` |
| `market-ads` | Ad copy for Google, Facebook, LinkedIn, TikTok | WebFetch (brand/product understanding) |
| `market-launch` | Product launch playbook (pre/during/post phases) | User input (product name, features, audience) |
| `market-proposal` | Client proposal with tiered pricing | User input (client name, services, budget) |
| `market-report` | Compiles all analysis into one Markdown deliverable | Previously generated audit/analysis files |
| `market-report-pdf` | Professional PDF report with charts and tables | Previously generated files + ReportLab for rendering |

### Parallel Subagents (launched by `market-audit`)

| Agent | Dimension Scored | What It Analyzes |
|-------|-----------------|------------------|
| `market-content` | Content & Messaging (25%) | Copy quality, headlines, value props, messaging clarity |
| `market-conversion` | Conversion Optimization (20%) | CTAs, forms, friction points, social proof, urgency |
| `market-competitive` | Competitive Positioning (15%) | Competitor positioning, differentiation, messaging gaps |
| `market-technical` | SEO & Discoverability (20%) | Technical SEO, meta tags, structure + PageSpeed results |
| `market-strategy` | Brand & Trust (10%) + Growth (10%) | Business model, pricing, growth loops, trust signals |

### Python Scripts

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `pagespeed_score.py` | CLI wrapper for PageSpeed API | URL(s), strategy | JSON: scores, Core Web Vitals, opportunities |
| `pagespeed_client.py` | Low-level PageSpeed API client | URL, strategy, API key | Raw PSI JSON response |
| `pagespeed_normalize.py` | Normalizes PSI response | PSI JSON | Stable schema with extracted metrics |
| `analyze_page.py` | Marketing page analysis | URL | JSON: headings, links, forms, buttons, schema |
| `competitor_scanner.py` | Competitor website scanner | Competitor URL | JSON: title, pricing, social links, CTAs |
| `social_calendar.py` | Social content calendar | Topic/business info | Markdown calendar |
| `generate_pdf_report.py` | PDF from Markdown report | Markdown file | PDF with formatted tables and charts |

### Data Flow Summary

```
/market audit https://example.com
    │
    ├─ WebFetch: homepage + pricing, about, product, blog, contact pages
    ├─ (Optional) PageSpeed API: Lighthouse scores + Core Web Vitals
    ├─ Business type detection: SaaS | E-commerce | Agency | Local | Creator | Marketplace
    │
    ├─ 5 parallel subagents each score their dimension ──┐
    │                                                      │
    ├─ Weighted composite score (0-100) + letter grade  ◄──┘
    ├─ Quick wins, strategic recommendations, revenue impact estimates
    │
    └─ Output: MARKETING-AUDIT.md (+ optional PDF)
```

---

## Use Cases

### For Agency Builders
- Run `/market audit` on a prospect's website before a sales call
- Generate `/market proposal` with specific findings and pricing
- Deliver `/market report-pdf` as a professional client deliverable

### For Solopreneurs
- Use `/market copy` to optimize your own landing pages
- Generate `/market emails` for your product launches
- Build `/market social` calendars for consistent posting

### For Content Creators
- Research competitors with `/market competitors`
- Plan launches with `/market launch`
- Analyze your funnel with `/market funnel`

---

## Uninstall

```bash
./uninstall.sh
```

Or manually:
```bash
rm -rf ~/.claude/skills/market*
rm -f ~/.claude/agents/market-*.md
```

---

## Learn More

Want to learn how to build a marketing agency powered by AI tools like this?

**[Join the AI Workshop Community](https://www.skool.com/aiworkshop)** — Learn AI automations, vibe coding, and how to build AI-powered services for clients.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
