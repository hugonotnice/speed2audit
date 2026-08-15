import sqlite3
from pathlib import Path

from speed2audit.config import DATABASE_PATH
from speed2audit.core.models import AuditSession


class AuditDatabase:
    """Local SQLite persistence layer for Speed2Audit sessions, transcripts, and scorecards."""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_sessions (
                    session_id TEXT PRIMARY KEY,
                    website_url TEXT NOT NULL,
                    target_phone TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    data_json TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save_session(self, session: AuditSession) -> None:
        """Insert or replace an audit session and its full serialized payload."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO audit_sessions (
                    session_id, website_url, target_phone, status, created_at, data_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_id,
                    session.website_url,
                    session.target_phone,
                    session.status.value,
                    session.created_at.isoformat(),
                    session.model_dump_json(),
                ),
            )
            conn.commit()

    def get_session(self, session_id: str) -> AuditSession | None:
        """Retrieve a session by its unique session_id."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT data_json FROM audit_sessions WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return AuditSession.model_validate_json(row["data_json"])

    def list_sessions(self, limit: int = 50) -> list[AuditSession]:
        """List past audit sessions ordered by creation date descending."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT data_json FROM audit_sessions ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
            return [AuditSession.model_validate_json(r["data_json"]) for r in rows]

    def delete_session(self, session_id: str) -> bool:
        """Delete an audit session by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM audit_sessions WHERE session_id = ?",
                (session_id,),
            )
            conn.commit()
            return cursor.rowcount > 0
