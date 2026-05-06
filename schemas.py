from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


AuditStatus = Literal["queued", "running", "needs_input", "completed", "failed"]


class AuditCreateRequest(BaseModel):
    domain: str = Field(min_length=3, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)


class FindingModel(BaseModel):
    code: str
    title: str
    category: str
    severity: str
    description: str
    recommendation: str
    evidence: str


class AuditSummaryResponse(BaseModel):
    id: str
    company_name: str | None
    domain: str
    status: AuditStatus
    created_at: str
    updated_at: str
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None
    summary: str | None = None
    report_path: str | None = None
    score: int = 0


class AuditDetailResponse(AuditSummaryResponse):
    findings: list[FindingModel] = []
    evidence_items: list[dict[str, Any]] = []
    notes: list[dict[str, Any]] = []


class NoteCreateRequest(BaseModel):
    source: str = Field(default="portal", max_length=50)
    content: str = Field(min_length=1, max_length=5000)


class AuditCreateResponse(BaseModel):
    audit_id: str
    status: AuditStatus


class TargetModel(BaseModel):
    name: str
    category: str
    tier: str
    city: str
    state: str = "TX"
    region: str = "Central Texas"
    domain: str | None = None
    website: str | None = None
    estimated_size: str | None = None
    notes: str | None = None
    source: str = "seed"


class TargetListRequest(BaseModel):
    primary_count: int = Field(default=20, ge=1, le=50)
    secondary_count: int = Field(default=15, ge=1, le=50)
    use_ai: bool = True


class TargetListResponse(BaseModel):
    generated_at: str
    region: str
    model: str | None = None
    source: str
    primary_targets: list[TargetModel] = []
    secondary_targets: list[TargetModel] = []
    counts: dict[str, int] = {}
