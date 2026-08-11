# AGENTS.md

## Repository Purpose

Next-Gen IT is an IT audit / cybersecurity assessment platform. It exposes a **FastAPI** backend (`main.py`) that orchestrates DNS audits, gap-analysis, and HTML report generation for prospect domains. A small crash-course portal lives under `crash-course/` and static HTML tools (audit preview, presence dashboard) are served alongside the API.

## Project Layout

| Path | Description |
|------|-------------|
| `main.py` | FastAPI application entry-point |
| `config.py` | App settings (env-driven) |
| `scoring.py` | Domain scoring logic |
| `dns_audit.py` | DNS enumeration helpers |
| `gap_assistant.py` | AI-powered follow-up question generator |
| `requirements.txt` | Python runtime dependencies |
| `ruff.toml` | Ruff linter configuration |
| `crash-course/` | Static HTML crash-course portal |
| `reports/` | Generated HTML audit reports (git-tracked) |
| `data/` | Machine-generated data files (e.g. `presence.json`) |
| `scripts/` | Automation scripts run by CI workflows |
| `.github/workflows/` | CI / scheduled workflows |

## Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API (development)
uvicorn main:app --reload

# Or use Docker Compose
docker compose up
```

## Linting

```bash
ruff check . --config ruff.toml
```

This is the same command run by the CI linting job.

## Making Changes Safely

- **Python style**: follow existing patterns; run `ruff check` before committing.
- **Secrets / credentials**: never commit API keys or tokens — scan changed files before every commit.
- **`data/` files**: `data/presence.json` is auto-updated by the `presence-refresh` workflow; avoid manual edits that conflict with scheduled runs.
- **`reports/`**: generated files; do not hand-edit report HTML.
- **Workflows**: any change to `.github/workflows/` should be tested on a feature branch before merging to `main`.
- **Dependencies**: check the GitHub Advisory Database before adding or upgrading packages.
- **Default branch**: `main`.
