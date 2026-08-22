"""Legacy console entry point backed by the current CourseCarry engine.

The desktop app is the recommended interface. This module remains for developers
who used the original ``python backup_all.py`` workflow.
"""

from __future__ import annotations

import json

from coursecarry.config import ConfigStore
from coursecarry.core.backup_manager import BackupEvents, BackupManager
from coursecarry.core.database import CourseCarryDatabase
from coursecarry.models import Assignment, BackupOptions, Course, DownloadStatus
from coursecarry.utils.logging import configure_logging
from coursecarry.version import __version__


class ConsoleEvents(BackupEvents):
    def stage(self, message: str) -> None:
        print(message)

    def course_started(self, index: int, total: int, course: Course) -> None:
        print(f"\nCOURSE {index}/{total} — {course.name}")

    def assignment_started(self, index: int, total: int, assignment: Assignment) -> None:
        print(f"  Assignment {index}/{total} — {assignment.name}")

    def file_started(self, filename: str) -> None:
        print(f"    Downloading: {filename}")

    def file_progress(self, downloaded: int, total: int | None) -> None:
        if total:
            print(
                f"\r      {downloaded / 1024 / 1024:.1f} MB / "
                f"{total / 1024 / 1024:.1f} MB",
                end="",
                flush=True,
            )

    def file_completed(self, filename: str, status: DownloadStatus) -> None:
        print(f"\n    {status.value.upper()}: {filename}")

    def error(self, scope: str, message: str) -> None:
        print(f"    ERROR — {scope}: {message}")


def main() -> int:
    store = ConfigStore()
    config = store.load()
    configure_logging(config.logs_dir)
    database = CourseCarryDatabase(config.database_path)
    database.initialize()

    if not config.courses_path.exists():
        print("No course cache found. Use Scan Courses in the desktop app first.")
        return 1

    data = json.loads(config.courses_path.read_text(encoding="utf-8"))
    courses = [Course.from_dict(item) for item in data.get("courses", [])]
    print(f"CourseCarry v{__version__} — console compatibility mode")
    print(f"Courses loaded: {len(courses)}")
    print("Chrome will open. Complete the normal school login if requested.")

    manager = BackupManager(config, database)
    stats = manager.run(courses, BackupOptions(), ConsoleEvents(), lambda: False)
    print("\nBACKUP COMPLETE")
    print(f"Downloaded: {stats.downloaded}")
    print(f"Skipped:    {stats.skipped}")
    print(f"Updated:    {stats.updated}")
    print(f"Failed:     {stats.failed}")
    print(f"Incomplete: {stats.incomplete}")
    return 0 if stats.failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
