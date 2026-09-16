from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from ..models import BackupStats, Course


class CourseCarryDatabase:
    """Small incremental index; JSON remains supported for course interchange."""

    def __init__(self, path: Path) -> None:
        self.path = path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        try:
            connection.row_factory = sqlite3.Row
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL,
                    href TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'unknown',
                    available INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS backup_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    status TEXT NOT NULL,
                    stats_json TEXT NOT NULL DEFAULT '{}'
                );
                """
            )
            course_columns = {
                str(row["name"])
                for row in connection.execute("PRAGMA table_info(courses)").fetchall()
            }
            if "category" not in course_columns:
                connection.execute(
                    "ALTER TABLE courses ADD COLUMN category TEXT NOT NULL DEFAULT 'unknown'"
                )
            if "available" not in course_columns:
                connection.execute(
                    "ALTER TABLE courses ADD COLUMN available INTEGER NOT NULL DEFAULT 1"
                )

    def save_courses(self, courses: list[Course]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            connection.executemany(
                """
                INSERT INTO courses (id, name, code, href, last_seen, category, available)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    code=excluded.code,
                    href=excluded.href,
                    last_seen=excluded.last_seen,
                    category=excluded.category,
                    available=excluded.available
                """,
                [
                    (
                        item.id,
                        item.name,
                        item.code,
                        item.href,
                        item.last_seen_at or now,
                        item.category,
                        int(item.available),
                    )
                    for item in courses
                ],
            )

    def start_backup_run(self) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO backup_runs (started_at, status) VALUES (?, ?)",
                (datetime.now(timezone.utc).isoformat(), "running"),
            )
            return int(cursor.lastrowid)

    def finish_backup_run(self, run_id: int, status: str, stats: BackupStats) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE backup_runs
                SET completed_at=?, status=?, stats_json=?
                WHERE id=?
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    status,
                    json.dumps(stats.to_dict()),
                    run_id,
                ),
            )

    def last_backup_at(self) -> str | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT completed_at FROM backup_runs
                WHERE status='complete'
                ORDER BY id DESC LIMIT 1
                """
            ).fetchone()
            return str(row["completed_at"]) if row else None
