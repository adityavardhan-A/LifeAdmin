"""SQLite persistence: documents, reminders, users, activity_logs."""
from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set

from .models import Document

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("LIFEADMIN_DB", BASE_DIR / "data" / "lifeadmin.db"))

DOC_COLUMNS = [
    "filename", "doc_type", "holder_name", "doc_number", "organization",
    "vehicle_no", "amount", "start_date", "expiry_date", "notes",
    "stored_path", "uploaded_at",
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    doc_type TEXT NOT NULL DEFAULT 'Other',
    holder_name TEXT DEFAULT '',
    doc_number TEXT DEFAULT '',
    organization TEXT DEFAULT '',
    vehicle_no TEXT DEFAULT '',
    amount TEXT DEFAULT '',
    start_date TEXT DEFAULT '',
    expiry_date TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    stored_path TEXT DEFAULT '',
    uploaded_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    dismissed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    detail TEXT DEFAULT '',
    created_at TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


DEFAULT_USER = os.environ.get("LIFEADMIN_USER", "Adityavardhan Reddy")


def init_db() -> None:
    with closing(connect()) as conn, conn:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            conn.execute("INSERT INTO users (name, created_at) VALUES (?, ?)",
                         (DEFAULT_USER, _now()))
        # Older databases were seeded with a placeholder name.
        conn.execute("UPDATE users SET name = ? WHERE name = 'Default User'", (DEFAULT_USER,))


def get_user_name() -> str:
    with closing(connect()) as conn:
        row = conn.execute("SELECT name FROM users ORDER BY id LIMIT 1").fetchone()
    return row[0] if row else DEFAULT_USER


def set_user_name(name: str) -> None:
    name = name.strip()
    if not name:
        raise ValueError("Name cannot be empty")
    with closing(connect()) as conn, conn:
        conn.execute("UPDATE users SET name = ? WHERE id = (SELECT MIN(id) FROM users)", (name,))
    log("PROFILE", f"name set to {name}")


def log(action: str, detail: str = "") -> None:
    with closing(connect()) as conn, conn:
        conn.execute(
            "INSERT INTO activity_logs (action, detail, created_at) VALUES (?, ?, ?)",
            (action, detail, _now()),
        )


def add_document(doc: Document) -> int:
    doc.uploaded_at = doc.uploaded_at or _now()
    values = doc.to_dict()
    with closing(connect()) as conn, conn:
        cur = conn.execute(
            f"INSERT INTO documents ({', '.join(DOC_COLUMNS)}) "
            f"VALUES ({', '.join('?' for _ in DOC_COLUMNS)})",
            [values[c] for c in DOC_COLUMNS],
        )
        doc_id = cur.lastrowid
    log("ADD", f"{doc.filename} ({doc.doc_type})")
    return doc_id


def update_document(doc: Document) -> None:
    if doc.id is None:
        raise ValueError("Cannot update a document without an id")
    values = doc.to_dict()
    sets = ", ".join(f"{c} = ?" for c in DOC_COLUMNS)
    with closing(connect()) as conn, conn:
        conn.execute(f"UPDATE documents SET {sets} WHERE id = ?",
                     [values[c] for c in DOC_COLUMNS] + [doc.id])
    log("UPDATE", f"{doc.filename} (id {doc.id})")


def delete_document(doc_id: int) -> None:
    doc = get_document(doc_id)
    with closing(connect()) as conn, conn:
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    if doc:
        if doc.stored_path:
            try:
                Path(doc.stored_path).unlink(missing_ok=True)
            except OSError:
                pass
        log("DELETE", f"{doc.filename} (id {doc_id})")


def get_document(doc_id: int) -> Optional[Document]:
    with closing(connect()) as conn:
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
    return Document.from_row(row) if row else None


def list_documents() -> List[Document]:
    with closing(connect()) as conn:
        rows = conn.execute("SELECT * FROM documents ORDER BY id DESC").fetchall()
    return [Document.from_row(r) for r in rows]


def dismiss_reminder(doc_id: int) -> None:
    """Mark a reminder as completed (it moves to the Completed tab)."""
    with closing(connect()) as conn, conn:
        conn.execute("INSERT INTO reminders (document_id, dismissed_at) VALUES (?, ?)",
                     (doc_id, _now()))
    log("COMPLETE", f"reminder for document id {doc_id}")


def dismissed_ids() -> Set[int]:
    with closing(connect()) as conn:
        rows = conn.execute("SELECT DISTINCT document_id FROM reminders").fetchall()
    return {r[0] for r in rows}


def restore_reminder(doc_id: int) -> None:
    with closing(connect()) as conn, conn:
        conn.execute("DELETE FROM reminders WHERE document_id = ?", (doc_id,))
    log("RESTORE", f"reminder for document id {doc_id}")


# Friendlier names used by the Reminders page.
complete_reminder = dismiss_reminder
completed_ids = dismissed_ids


def list_logs(limit: int = 50) -> List[sqlite3.Row]:
    with closing(connect()) as conn:
        return conn.execute(
            "SELECT * FROM activity_logs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
