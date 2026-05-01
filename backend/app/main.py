# (only showing added endpoint)

@app.get("/api/audits/{audit_id}/runbook")
def download_runbook(audit_id: str):
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")

    runbook_path = audit.get("runbook_path")
    if not runbook_path or not Path(runbook_path).exists():
        raise HTTPException(status_code=404, detail="Runbook not generated yet.")

    return FileResponse(
        runbook_path,
        media_type="text/html",
        filename=f"{audit['domain']}-runbook.html",
    )
