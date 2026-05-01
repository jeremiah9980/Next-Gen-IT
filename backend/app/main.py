from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from .repository import get_audit

app = FastAPI()

@app.get("/api/audits/{audit_id}/runbook")
def download_runbook(audit_id: str):
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")

    path = audit.get("runbook_path")
    if not path or not Path(path).exists():
        raise HTTPException(status_code=404, detail="Runbook not ready.")

    return FileResponse(path, media_type="text/html")

# 🔥 CLIENT-FACING SHARE LINK
@app.get("/share/{audit_id}/runbook")
def share_runbook(audit_id: str):
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Not found")

    path = audit.get("runbook_path")
    if not path or not Path(path).exists():
        raise HTTPException(status_code=404, detail="Runbook not available")

    return FileResponse(path, media_type="text/html")
