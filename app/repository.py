from __future__ import annotations

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


def save_audit_outcome(audit_id: str, summary: str, score: int, report_path: Path) -> None:
    with db_cursor() as cur:
        cur.execute(
            '''
            UPDATE audits
            SET summary = ?, score = ?, report_path = ?, updated_at = ?
            WHERE id = ?
            ''',
            (summary, score, str(report_path), utc_now(), audit_id),
        )


def clear_findings(audit_id: str) -> None:
    with db_cursor() as cur:
        cur.execute("DELETE FROM findings WHERE audit_id = ?", (audit_id,))


def add_finding(audit_id: str, finding: dict[str, Any]) -> None:
    with db_cursor() as cur:
        cur.execute(
            '''
            INSERT INTO findings (
                audit_id, code, title, category, severity, description, recommendation, evidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                audit_id,
                finding["code"],
                finding["title"],
                finding["category"],
                finding["severity"],
                finding["description"],
                finding["recommendation"],
                finding["evidence"],
            ),
        )


def add_evidence(
    audit_id: str,
    kind: str,
    filename: str,
    path: str,
    content_type: str,
) -> None:
    with db_cursor() as cur:
        cur.execute(
            '''
            INSERT INTO evidence_items (audit_id, kind, filename, path, content_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (audit_id, kind, filename, path, content_type, utc_now()),
        )


def add_note(audit_id: str, source: str, content: str) -> None:
    with db_cursor() as cur:
        cur.execute(
            '''
            INSERT INTO notes (audit_id, source, content, created_at)
            VALUES (?, ?, ?, ?)
            ''',
            (audit_id, source, content, utc_now()),
        )


def get_audit(audit_id: str) -> dict[str, Any] | None:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM audits WHERE id = ?", (audit_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def list_audits() -> list[dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute("SELECT * FROM audits ORDER BY created_at DESC")
        return [dict(row) for row in cur.fetchall()]


def get_findings(audit_id: str) -> list[dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute(
            '''
            SELECT code, title, category, severity, description, recommendation, evidence
            FROM findings
            WHERE audit_id = ?
            ORDER BY
                CASE severity
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    ELSE 4
                END,
                id ASC
            ''',
            (audit_id,),
        )
        return [dict(row) for row in cur.fetchall()]


def get_evidence_items(audit_id: str) -> list[dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute(
            '''
            SELECT id, kind, filename, path, content_type, created_at
            FROM evidence_items
            WHERE audit_id = ?
            ORDER BY id DESC
            ''',
            (audit_id,),
        )
        return [dict(row) for row in cur.fetchall()]


def get_notes(audit_id: str) -> list[dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute(
            '''
            SELECT id, source, content, created_at
            FROM notes
            WHERE audit_id = ?
            ORDER BY id DESC
            ''',
            (audit_id,),
        )
        return [dict(row) for row in cur.fetchall()]


def add_chat_message(audit_id: str, role: str, content: str) -> None:
    with db_cursor() as cur:
        cur.execute(
            '''
            INSERT INTO chat_messages (audit_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            ''',
            (audit_id, role, content, utc_now()),
        )


def get_chat_history(audit_id: str) -> list[dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute(
            '''
            SELECT role, content, created_at
            FROM chat_messages
            WHERE audit_id = ?
            ORDER BY id ASC
            ''',
            (audit_id,),
        )
        return [dict(row) for row in cur.fetchall()]
