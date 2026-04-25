# Next-Gen IT — Domain Health Audit System

Automated domain auditing pipeline for small realty teams in the Round Rock / Georgetown / Cedar Park market. Paste a domain, get a full scored report published to GitHub Pages in under 2 minutes.

**Live Portal → [jeremiah9980.github.io/Next-Gen-IT/portal](https://jeremiah9980.github.io/Next-Gen-IT/portal/)**

---

## What it does

1. You enter a domain name in the portal (e.g. `starskyowen.com`)
2. The portal triggers a GitHub Actions workflow via the GitHub API
3. The workflow runs a full audit — WHOIS, DNS, MXToolbox, live site HTML analysis — then calls Claude AI to score all 30 points
4. A styled HTML report is committed to `reports/` and published to GitHub Pages
5. The portal's **Published Reports** section updates live with a link to the report

---

## Repo Structure

```
Next-Gen-IT/
├── portal/
│   └── index.html              # Audit portal UI — domain input, progress, reports list
│
├── .github/
│   └── workflows/
│       └── domain-audit.yml    # GitHub Actions workflow (triggered by portal)
│
├── scripts/
│   ├── run_audit.py            # Main audit engine — DNS + MXToolbox + Claude AI
│   └── update_manifest.py      # Updates reports/manifest.json after each audit
│
├── skills/
│   └── domain-health-audit/    # Claude skill files (used internally by run_audit.py)
│       ├── SKILL.md
│       ├── scripts/
│       │   └── domain_audit.sh
│       └── references/
│           ├── audit-checklist.md
│           ├── provider-map.md
│           └── report-template.md
│
├── reports/
│   ├── manifest.json           # Index of all published reports (auto-updated)
│   └── *.html                  # Individual audit reports (auto-generated)
│
└── README.md                   # This file
```

---

## Setup (one-time)

### 1. Add GitHub Secrets

Go to **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name | Value |
|-------------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from [console.anthropic.com](https://console.anthropic.com) |

> `GITHUB_TOKEN` is provided automatically — no action needed.

### 2. Create a GitHub Personal Access Token (for the portal)

The portal needs a token to trigger the workflow via the GitHub API.

1. Go to [github.com/settings/tokens?type=beta](https://github.com/settings/tokens?type=beta)
2. Click **Generate new token (fine-grained)**
3. Set **Repository access** → Only `Next-Gen-IT`
4. Under **Permissions → Repository permissions**, set **Actions** → `Read and write`
5. Copy the token

### 3. Configure the portal

1. Open [jeremiah9980.github.io/Next-Gen-IT/portal](https://jeremiah9980.github.io/Next-Gen-IT/portal/)
2. Click **⚙ Config** in the top-right
3. Paste your GitHub PAT
4. Click **Save** — the token is stored in your browser's `localStorage` only, never sent anywhere except GitHub's own API

---

## Running an Audit

1. Type a domain in the portal input (e.g. `tkerrrealestate.com`)
2. Click **Run Audit →**
3. Watch the 6-step progress indicator as the workflow runs (~90 seconds)
4. A green banner appears with a link to the published report
5. The report is also added to the **Published Reports** section

---

## Audit Scorecard (30 points)

| Category | Points | What's checked |
|----------|--------|----------------|
| **Website & SEO** | 10 | SSL, mobile, IDX/MLS, contact form, Google Business, local keywords, blog, sitemap, analytics, schema |
| **Marketing & Social** | 10 | Facebook, Instagram, Pixel, LinkedIn/YouTube, email capture, video, testimonials, retargeting, Google Reviews |
| **Tech Stack & CRM** | 10 | CRM platform, live chat, transaction mgmt, e-signature, scheduling, automation, GTM, heatmap, IDX platform, HTTPS |

**Grade scale:** A (25–30) · B (20–24) · C (14–19) · D (8–13) · F (0–7)

**Email health** (reported separately): MX · SPF · DMARC · DKIM · Blacklist · SSL

---

## Report Output

Each audit produces:
- A fully styled HTML report at `reports/{domain}-{timestamp}.html`
- Published to GitHub Pages at `https://jeremiah9980.github.io/Next-Gen-IT/reports/{filename}`
- Includes: infrastructure summary, email health, 30-point scorecard, top 5 recommendations, and a sales pitch angle

---

## Target Market

Small realty teams in the **Round Rock / Georgetown / Cedar Park, TX** corridor. Current prospect list:

| Team | Area | Priority |
|------|------|----------|
| T. Kerr Property Group | Georgetown | High |
| Robert J Fischer Team | Round Rock | High |
| TRE Realty | Round Rock | High |
| New Hope Realty Group | Cedar Park | High |
| Russ Phillips Team \| KW | Georgetown | High |
| Chad Realty Group | Cedar Park | High |
| Jorgenson Real Estate | Round Rock | Medium |
| Pure Realty | Cedar Park | Medium |
| Cedar Park Living | Cedar Park | Medium |
| CTX Advantage Group | Georgetown | Low |
| The Rivera Team TX | Georgetown | Low |

---

## Tech Stack

- **Frontend:** Vanilla HTML/CSS/JS · GitHub Pages
- **CI/CD:** GitHub Actions (`workflow_dispatch`)
- **Audit engine:** Python 3.11 · `anthropic` SDK · `bash` (whois, dig, curl)
- **AI analysis:** Claude Sonnet (via Anthropic API)
- **Data source:** MXToolbox SuperTool · ipinfo.io · live site HTTP
- **Storage:** GitHub repo (flat files) · `reports/manifest.json`

---

## Local Development

```bash
# Install dependencies
pip install anthropic requests

# Run a single audit locally
export ANTHROPIC_API_KEY=your_key_here
python scripts/run_audit.py starskyowen.com ./reports/

# Check the output
open reports/starskyowen-*.html
```

---

*Built and maintained by [Next-Gen IT](https://jeremiah9980.github.io/Next-Gen-IT/portal/)*
