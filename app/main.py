from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import settings
from .db import init_db
from .repository import (
    add_chat_message,
    add_evidence,
    add_note,
    create_audit,
    get_audit,
    get_chat_history,
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
    ChatMessageModel,
    ChatMessageRequest,
    ChatResponse,
    NoteCreateRequest,
)
from .services.ai_agent import get_ai_response
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


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/audits", response_model=AuditCreateResponse)
def create_audit_endpoint(payload: AuditCreateRequest) -> AuditCreateResponse:
    domain = payload.domain.strip().lower()
    if "." not in domain:
        raise HTTPException(status_code=400, detail="Enter a valid domain.")
    audit_id = create_audit(domain=domain, company_name=payload.company_name)
    start_audit_thread(audit_id)
    return AuditCreateResponse(audit_id=audit_id, status="queued")


@app.get("/api/audits", response_model=list[AuditSummaryResponse])
def list_audits_endpoint() -> list[AuditSummaryResponse]:
    return [AuditSummaryResponse(**row) for row in list_audits()]


@app.get("/api/audits/{audit_id}", response_model=AuditDetailResponse)
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


@app.post("/api/audits/{audit_id}/evidence")
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


@app.post("/api/audits/{audit_id}/notes")
def create_note(audit_id: str, payload: NoteCreateRequest) -> dict[str, str]:
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    add_note(audit_id=audit_id, source=payload.source, content=payload.content)
    return {"message": "Note saved."}


@app.get("/api/audits/{audit_id}/gaps")
def get_gap_questions(audit_id: str) -> dict[str, list[str]]:
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    findings = get_findings(audit_id)
    evidence_items = get_evidence_items(audit_id)
    notes = get_notes(audit_id)
    questions = generate_follow_up_questions(audit, findings, evidence_items, notes)
    return {"questions": questions}


@app.get("/api/audits/{audit_id}/report")
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


@app.post("/api/audits/{audit_id}/chat", response_model=ChatResponse)
def chat_with_agent(audit_id: str, payload: ChatMessageRequest) -> ChatResponse:
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    findings = get_findings(audit_id)
    evidence_items = get_evidence_items(audit_id)
    notes = get_notes(audit_id)
    history = get_chat_history(audit_id)

    add_chat_message(audit_id, "user", payload.message)

    reply = get_ai_response(
        message=payload.message,
        history=history,
        audit=audit,
        findings=findings,
        evidence_items=evidence_items,
        notes=notes,
    )

    add_chat_message(audit_id, "assistant", reply)

    # Build the updated history from the already-fetched state plus the two new messages
    updated_history = history + [
        {"role": "user", "content": payload.message, "created_at": ""},
        {"role": "assistant", "content": reply, "created_at": ""},
    ]
    return ChatResponse(
        reply=reply,
        history=[ChatMessageModel(**msg) for msg in updated_history],
    )


@app.get("/api/audits/{audit_id}/chat", response_model=list[ChatMessageModel])
def get_chat_endpoint(audit_id: str) -> list[ChatMessageModel]:
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    history = get_chat_history(audit_id)
    return [ChatMessageModel(**msg) for msg in history]
