from __future__ import annotations

import json
from threading import Event

from PySide6.QtCore import QObject, Signal, Slot
from playwright.sync_api import sync_playwright

from ..config import AppConfig
from ..models import Assignment, BackupOptions, BackupStats, Course, DownloadStatus
from ..providers import NPBrightspaceProvider
from ..utils.logging import redact_sensitive
from .backup_manager import BackupEvents, BackupManager
from .database import CourseCarryDatabase


class CourseScanWorker(QObject):
    status_changed = Signal(str)
    courses_ready = Signal(object)
    failed = Signal(str)
    completed = Signal()

    def __init__(self, config: AppConfig, database: CourseCarryDatabase) -> None:
        super().__init__()
        self.config = config
        self.database = database
        self._cancelled = Event()

    @Slot()
    def run(self) -> None:
        try:
            with sync_playwright() as playwright:
                provider = NPBrightspaceProvider(self.config)
                context = provider.open_context(playwright)
                try:
                    courses = provider.wait_for_courses(
                        context, self.status_changed.emit, self._cancelled.is_set
                    )
                    if not self._cancelled.is_set():
                        self.config.data_dir.mkdir(parents=True, exist_ok=True)
                        self.config.courses_path.write_text(
                            json.dumps(
                                {
                                    "course_count": len(courses),
                                    "courses": [course.to_dict() for course in courses],
                                },
                                ensure_ascii=False,
                                indent=2,
                            )
                            + "\n",
                            encoding="utf-8",
                        )
                        self.database.save_courses(courses)
                        self.courses_ready.emit(courses)
                finally:
                    context.close()
        except Exception as error:
            self.failed.emit(redact_sensitive(error))
        finally:
            self.completed.emit()

    def cancel(self) -> None:
        self._cancelled.set()


class BackupWorker(QObject, BackupEvents):
    stage_changed = Signal(str)
    course_changed = Signal(int, int, object)
    assignment_changed = Signal(int, int, str)
    file_changed = Signal(str)
    file_progress_changed = Signal(object, object)
    file_completed_changed = Signal(str, str)
    error_occurred = Signal(str, str)
    finished = Signal(object, bool)

    def __init__(
        self,
        config: AppConfig,
        database: CourseCarryDatabase,
        courses: list[Course],
        options: BackupOptions,
    ) -> None:
        super().__init__()
        self.manager = BackupManager(config, database)
        self.courses = courses
        self.options = options
        self._cancelled = Event()

    @Slot()
    def run(self) -> None:
        stats = self.manager.run(
            self.courses,
            self.options,
            self,
            self._cancelled.is_set,
        )
        self.finished.emit(stats, self._cancelled.is_set())

    def cancel(self) -> None:
        self._cancelled.set()
        self.stage_changed.emit("Cancellation requested — finishing the current safe step…")

    def stage(self, message: str) -> None:
        self.stage_changed.emit(message)

    def course_started(self, index: int, total: int, course: Course) -> None:
        self.course_changed.emit(index, total, course)

    def assignment_started(self, index: int, total: int, assignment: Assignment) -> None:
        self.assignment_changed.emit(index, total, assignment.name)

    def file_started(self, filename: str) -> None:
        self.file_changed.emit(filename)

    def file_progress(self, downloaded: int, total: int | None) -> None:
        self.file_progress_changed.emit(downloaded, total)

    def file_completed(self, filename: str, status: DownloadStatus) -> None:
        self.file_completed_changed.emit(filename, status.value)

    def error(self, scope: str, message: str) -> None:
        self.error_occurred.emit(scope, message)
