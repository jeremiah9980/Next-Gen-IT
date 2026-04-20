# Next-Gen-IT Functional MVP

This starter project makes the **Run Audit** flow functional for the public portal.

## What it does

- Starts an audit from a domain and optional company name
- Runs a background DNS / mail security scan
- Stores audit status and findings in SQLite
- Shows findings in a client-facing portal
- Accepts uploads as supporting evidence
- Accepts consultant/client notes
- Generates a Markdown report
- Produces targeted follow-up questions for missing details

## Project layout

- `frontend/` static client portal
- `backend/` FastAPI API + background audit worker
- `scripts/` helper scripts

## Quick start

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 2) Frontend

In another terminal:

```bash
cd frontend
python -m http.server 4173
```

Open `http://localhost:4173`

Set **API Base URL** to:

```text
http://localhost:8000
```

## API endpoints

- `POST /api/audits`
- `GET /api/audits`
- `GET /api/audits/{audit_id}`
- `GET /api/audits/{audit_id}/report`
- `POST /api/audits/{audit_id}/evidence`
- `POST /api/audits/{audit_id}/notes`
- `GET /api/audits/{audit_id}/gaps`

## Notes

- This MVP uses SQLite so it is easy to run locally.
- The audit worker is thread-based for simplicity.
- DKIM verification is intentionally conservative: if a selector is not known, the system reports that DKIM could not be publicly verified.
- The generated report is Markdown. You can later swap that for PDF generation.
