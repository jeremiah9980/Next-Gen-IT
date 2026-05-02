from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import settings
from .db import init_db
from .repository import (
    add_evidence,
    add_note,
    create_audit,
    get_audit,
    get_evidence_items,
    get_findings,
    get_notes,
    list_audits,
)
from .schemas import (
    AuditCreateRequest,
    AuditCreateResponse,
    AuditDetailResponse,
    AuditSummaryResponse,
    NoteCreateRequest,
)
from .services.gap_assistant import generate_follow_up_questions
from .services.worker import start_audit_thread

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Protect internal API routes while keeping public /share links open."""
    if not settings.portal_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API key protection is not configured.",
        )
    if x_api_key != settings.portal_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/audits", response_model=AuditCreateResponse, dependencies=[Depends(require_api_key)])
def create_audit_endpoint(payload: AuditCreateRequest) -> AuditCreateResponse:
    domain = payload.domain.strip().lower()
    if "." not in domain:
        raise HTTPException(status_code=400, detail="Enter a valid domain.")
    audit_id = create_audit(domain=domain, company_name=payload.company_name)
    start_audit_thread(audit_id)
    return AuditCreateResponse(audit_id=audit_id, status="queued")


@app.get("/api/audits", response_model=list[AuditSummaryResponse], dependencies=[Depends(require_api_key)])
def list_audits_endpoint() -> list[AuditSummaryResponse]:
    return [AuditSummaryResponse(**row) for row in list_audits()]


@app.get("/api/audits/{audit_id}", response_model=AuditDetailResponse, dependencies=[Depends(require_api_key)])
def get_audit_endpoint(audit_id: str) -> AuditDetailResponse:
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    return AuditDetailResponse(
        **audit,
        findings=get_findings(audit_id),
        evidence_items=get_evidence_items(audit_id),
        notes=get_notes(audit_id),
    )


@app.post("/api/audits/{audit_id}/evidence", dependencies=[Depends(require_api_key)])
async def upload_evidence(audit_id: str, file: UploadFile = File(...)) -> dict[str, str]:
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    target_dir = settings.upload_dir / audit_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / file.filename
    with target_path.open("wb") as handle:
        shutil.copyfileobj(file.file, handle)
    add_evidence(
        audit_id=audit_id,
        kind="upload",
        filename=file.filename,
        path=str(target_path),
        content_type=file.content_type or "application/octet-stream",
    )
    return {"message": "Evidence uploaded."}


@app.post("/api/audits/{audit_id}/notes", dependencies=[Depends(require_api_key)])
def create_note(audit_id: str, payload: NoteCreateRequest) -> dict[str, str]:
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    add_note(audit_id=audit_id, source=payload.source, content=payload.content)
    return {"message": "Note saved."}


@app.get("/api/audits/{audit_id}/gaps", dependencies=[Depends(require_api_key)])
def get_gap_questions(audit_id: str) -> dict[str, list[str]]:
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    findings = get_findings(audit_id)
    evidence_items = get_evidence_items(audit_id)
    notes = get_notes(audit_id)
    questions = generate_follow_up_questions(audit, findings, evidence_items, notes)
    return {"questions": questions}


@app.get("/api/audits/{audit_id}/report", dependencies=[Depends(require_api_key)])
def download_report(audit_id: str) -> FileResponse:
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    report_path = audit.get("report_path")
    if not report_path or not Path(report_path).exists():
        raise HTTPException(status_code=404, detail="Report not generated yet.")
    return FileResponse(
        report_path,
        media_type="text/markdown",
        filename=f"{audit['domain']}-next-gen-it-report.md",
    )


@app.get("/api/audits/{audit_id}/runbook", dependencies=[Depends(require_api_key)])
def download_runbook(audit_id: str) -> FileResponse:
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


@app.get("/share/{audit_id}/runbook")
def share_runbook(audit_id: str) -> FileResponse:
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Not found")
    runbook_path = audit.get("runbook_path")
    if not runbook_path or not Path(runbook_path).exists():
        raise HTTPException(status_code=404, detail="Runbook not available")
    return FileResponse(runbook_path, media_type="text/html")
