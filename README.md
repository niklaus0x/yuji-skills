# Yuji's Skills

Yuji is the AI Web App Testing Specialist for **niklaus0x**, powered by [Appy.AI](https://appy.ai).

He uses Python Playwright to test, verify, debug, and QA local and deployed web applications — with full CI/CD integration, visual regression, accessibility checks, performance metrics, and multi-browser support.

## Quick Start

```bash
git clone https://github.com/niklaus0x/yuji-skills
cd yuji-skills
pip install -r requirements.txt
playwright install
```

## Skill Modules

| Module | What it does |
|---|---|
| `skills/core.py` | Base Playwright helpers — launch, screenshot, logs, DOM inspection |
| `skills/visual.py` | Visual regression — screenshot diffs, baseline management |
| `skills/accessibility.py` | WCAG accessibility checks via axe-playwright |
| `skills/performance.py` | Page load, LCP, TTI, CLS performance metrics |
| `skills/network.py` | Intercept and log all network requests/responses |
| `skills/multi_browser.py` | Cross-browser testing — Chromium, Firefox, WebKit |
| `skills/reporter.py` | HTML + JSON test report generation |
| `scripts/with_server.py` | Server lifecycle manager (single + multi-server) |

## GitHub Actions

See `.github/workflows/test.yml` — auto-runs tests on every push and PR. Posts results as PR comments.

## Known Apps (pre-configured)

| App | URL | Key flows |
|---|---|---|
| saas-lead-generator | saas-lead-generator-production.up.railway.app | Search leads, export CSV |
| tola-skills dashboard | localhost:3001 | Queue, repurpose, analytics |
| mission-control | github.com/niklaus0x/mission-control | Agent management |

## Install

```bash
# Option 1 — Anthropic skills
npx skills add anthropics/skills -g -y

# Option 2 — Direct
pip install playwright axe-playwright pillow requests
playwright install
```

---
**Managed by Yuji** — AI Web App Testing Specialist for @niklaus0x
