# Next-Gen IT — Domain Health Audit System

Automated domain auditing pipeline for small realty teams. Paste a domain, get a fully scored HTML report published to GitHub Pages in under 2 minutes.

**Live Portal → [jeremiah9980.github.io/Next-Gen-IT/portal](https://jeremiah9980.github.io/Next-Gen-IT/portal/)**

[![CI](https://github.com/jeremiah9980/Next-Gen-IT/actions/workflows/ci.yml/badge.svg)](https://github.com/jeremiah9980/Next-Gen-IT/actions/workflows/ci.yml)

---

## What it does

1. Enter a domain in the portal (e.g. `starskyowen.com`)
2. The portal triggers a GitHub Actions workflow via the GitHub API
3. The workflow runs a full audit — WHOIS, DNS, MXToolbox, live site HTML analysis — then calls Claude AI to score all 30 points
4. A styled HTML report is committed to `reports/` and published to GitHub Pages
5. The portal's **Published Reports** section updates live with a link to the report

---

## Repo structure

```
Next-Gen-IT/
├── portal/                     # Public-facing audit portal (GitHub Pages)
│   ├── index.html
│   └── login.html
├── frontend/                   # Alternative portal UI (local dev)
│   └── index.html
├── backend/                    # FastAPI backend (local/self-hosted mode)
│   └── app/
│       ├── main.py
│       ├── db.py
│       ├── repository.py
│       ├── schemas.py
│       └── services/
├── scripts/
│   ├── run_audit.py            # Audit engine — DNS + MXToolbox + Claude AI
│   └── update_manifest.py      # Updates reports/manifest.json after each audit
├── reports/
│   ├── manifest.json           # Index of all published reports (auto-updated)
│   └── *.html                  # Individual audit reports (auto-generated)
├── .github/
│   └── workflows/
│       ├── ci.yml              # Lint + link-check on every push / PR
│       ├── deploy.yml          # Deploy portal to GitHub Pages
│       └── domain-audit.yml    # Triggered by portal to run an audit
└── requirements.txt
```

---

## Quick start (local — full stack)

### Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com) for AI-powered audit scoring

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit .env and add your ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

### 2) Frontend

In a second terminal:

```bash
cd frontend
python -m http.server 4173
```

Open `http://localhost:4173` and set **API Base URL** to `http://localhost:8000`.

### 3) Run a single audit from the command line

```bash
pip install anthropic requests
export ANTHROPIC_API_KEY=your_key_here
python scripts/run_audit.py starskyowen.com ./reports/
open reports/starskyowen-*.html
```

---

## GitHub Pages portal setup (one-time)

### 1. Add GitHub Secrets

**Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|--------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |

> `GITHUB_TOKEN` is provided automatically.

### 2. Create a Personal Access Token for the portal

1. Go to [github.com/settings/tokens?type=beta](https://github.com/settings/tokens?type=beta)
2. **Generate new token (fine-grained)** → restrict to this repo → **Actions: Read and write**
3. Copy the token

### 3. Configure the portal

1. Open the [live portal](https://jeremiah9980.github.io/Next-Gen-IT/portal/)
2. Click **⚙ Config** → paste your PAT → **Save**

The token is stored only in your browser's `localStorage`.

---

## CI checks (run locally before pushing)

Install the linter once:

```bash
pip install ruff
```

Run it:

```bash
ruff check .
```

The same check runs automatically on every push and pull request via [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

---

## API endpoints (backend mode)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/audits` | Start a new audit |
| `GET` | `/api/audits` | List all audits |
| `GET` | `/api/audits/{id}` | Get audit status & findings |
| `GET` | `/api/audits/{id}/report` | Download the Markdown report |
| `POST` | `/api/audits/{id}/evidence` | Upload supporting evidence |
| `POST` | `/api/audits/{id}/notes` | Add consultant notes |
| `GET` | `/api/audits/{id}/gaps` | Get gap-analysis questions |

---

## Audit scorecard (30 points)

| Category | Points | What's checked |
|----------|--------|----------------|
| **Website & SEO** | 10 | SSL, mobile, IDX/MLS, contact form, Google Business, local keywords, blog, sitemap, analytics, schema |
| **Marketing & Social** | 10 | Facebook, Instagram, Pixel, LinkedIn/YouTube, email capture, video, testimonials, retargeting, Google Reviews |
| **Tech Stack & CRM** | 10 | CRM platform, live chat, transaction mgmt, e-signature, scheduling, automation, GTM, heatmap, IDX platform, HTTPS |

**Grade scale:** A (25–30) · B (20–24) · C (14–19) · D (8–13) · F (0–7)

**Email health** (reported separately): MX · SPF · DMARC · DKIM · Blacklist · SSL

---

## Tech stack

- **Frontend:** Vanilla HTML/CSS/JS · GitHub Pages
- **Backend:** Python 3.11 · FastAPI · SQLite
- **CI/CD:** GitHub Actions
- **Audit engine:** Python 3.11 · `anthropic` SDK · `bash` (whois, dig, curl)
- **AI analysis:** Claude Sonnet (via Anthropic API)
- **Data sources:** MXToolbox · ipinfo.io · live site HTTP

---

## License

[MIT](LICENSE) © 2026 Jeremiah Cargill
