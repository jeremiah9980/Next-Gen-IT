from __future__ import annotations

import sqlite3
from contextlib import contextmanager

from .config import settings

DB_PATH = settings.data_dir / "next_gen_it.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_cursor():
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    finally:
        conn.close()


def ensure_column(cur: sqlite3.Cursor, table_name: str, column_name: str, column_definition: str) -> None:
    cur.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {row[1] for row in cur.fetchall()}
    if column_name not in existing_columns:
        cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


def init_db() -> None:
    with db_cursor() as cur:
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS audits (
                id TEXT PRIMARY KEY,
                company_name TEXT,
                domain TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                error TEXT,
                summary TEXT,
                report_path TEXT,
                runbook_path TEXT,
                score INTEGER DEFAULT 0
            )
            '''
        )
        ensure_column(cur, "audits", "runbook_path", "TEXT")
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id TEXT NOT NULL,
                code TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                evidence TEXT NOT NULL,
                FOREIGN KEY(audit_id) REFERENCES audits(id)
            )
            '''
        )
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS evidence_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                content_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(audit_id) REFERENCES audits(id)
            )
            '''
        )
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id TEXT NOT NULL,
                source TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(audit_id) REFERENCES audits(id)
            )
            '''
        )
