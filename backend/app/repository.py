from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .db import db_cursor


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_audit(domain: str, company_name: str | None) -> str:
    audit_id = str(uuid.uuid4())
    now = utc_now()
    with db_cursor() as cur:
        cur.execute(
            '''
            INSERT INTO audits (id, company_name, domain, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (audit_id, company_name, domain, "queued", now, now),
        )
    return audit_id


def set_audit_status(audit_id: str, status: str, error: str | None = None) -> None:
    now = utc_now()
    started_at = now if status == "running" else None
    completed_at = now if status in {"completed", "failed"} else None
    with db_cursor() as cur:
        if status == "running":
            cur.execute(
                '''
                UPDATE audits
                SET status = ?, updated_at = ?, started_at = ?, error = NULL
                WHERE id = ?
                ''',
                (status, now, started_at, audit_id),
            )
        elif status in {"completed", "failed"}:
            cur.execute(
                '''
                UPDATE audits
                SET status = ?, updated_at = ?, completed_at = ?, error = ?
                WHERE id = ?
                ''',
                (status, now, completed_at, error, audit_id),
            )
        else:
            cur.execute(
                '''
                UPDATE audits
                SET status = ?, updated_at = ?, error = ?
                WHERE id = ?
                ''',
                (status, now, error, audit_id),
            )


def save_audit_outcome(audit_id: str, summary: str, score: int, report_path: Path, runbook_path: Path) -> None:
    with db_cursor() as cur:
        cur.execute(
            '''
            UPDATE audits
            SET summary = ?, score = ?, report_path = ?, runbook_path = ?, updated_at = ?
            WHERE id = ?
            ''',
            (summary, score, str(report_path), str(runbook_path), utc_now(), audit_id),
        )

# rest unchanged...
