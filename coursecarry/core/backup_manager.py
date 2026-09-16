from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright

from ..config import AppConfig
from ..models import Assignment, BackupOptions, BackupStats, Course, DownloadStatus
from ..providers import create_provider
from ..utils.filenames import (
    assignment_archive_path,
    deduplicate_filename,
    sanitize_filename,
)
from ..utils.logging import redact_sensitive
from ..utils.url_security import source_fingerprint
from .database import CourseCarryDatabase
from .downloader import AuthenticatedDownloader, DownloadResult


LOGGER = logging.getLogger(__name__)


def choose_archive_filename(
    display_name: str,
    previous_filename: str | None,
    used_names: set[str],
    reserved_names: set[str],
) -> str:
    """Keep prior filenames stable even when Brightspace changes file order."""

    preferred = sanitize_filename(previous_filename or display_name, "unknown_file")
    if previous_filename:
        reserved_names.discard(preferred.casefold())
        return deduplicate_filename(preferred, used_names)

    blocked_names = used_names | reserved_names
    filename = deduplicate_filename(preferred, blocked_names)
    used_names.add(filename.casefold())
    return filename


class BackupEvents:
    """Callback surface kept independent from Qt for testability and CLI use."""

    def stage(self, message: str) -> None:
        pass

    def course_started(self, index: int, total: int, course: Course) -> None:
        pass

    def assignment_started(self, index: int, total: int, assignment: Assignment) -> None:
        pass

    def file_started(self, filename: str) -> None:
        pass

    def file_progress(self, downloaded: int, total: int | None) -> None:
        pass

    def file_completed(self, filename: str, status: DownloadStatus) -> None:
        pass

    def error(self, scope: str, message: str) -> None:
        pass


class BackupManager:
    def __init__(self, config: AppConfig, database: CourseCarryDatabase) -> None:
        self.config = config
        self.database = database
        self.provider = create_provider(config)

    def run(
        self,
        courses: list[Course],
        options: BackupOptions,
        events: BackupEvents,
        cancelled,
    ) -> BackupStats:
        stats = BackupStats()
        run_id: int | None = None
        final_status = "cancelled"
        downloader = AuthenticatedDownloader(
            self.config.lms_base_url,
            chunk_size=self.config.chunk_size_mb * 1024 * 1024,
        )

        try:
            run_id = self.database.start_backup_run()
            with sync_playwright() as playwright:
                events.stage("Opening Chrome with your local CourseCarry profile…")
                context = self.provider.open_context(playwright)
                try:
                    page = self.provider.active_page(context)
                    for course_index, course in enumerate(courses, start=1):
                        if cancelled():
                            break
                        events.course_started(course_index, len(courses), course)
                        try:
                            assignments = self.provider.scan_assignments(
                                page, course, events.stage, cancelled
                            )
                        except Exception as error:
                            LOGGER.error("Course scan failed: %s", type(error).__name__)
                            events.error("Course", redact_sensitive(error))
                            stats.failed += 1
                            continue

                        stats.courses += 1
                        for assignment_index, assignment in enumerate(assignments, start=1):
                            if cancelled():
                                break
                            events.assignment_started(
                                assignment_index, len(assignments), assignment
                            )
                            try:
                                files, submitted_at = self.provider.scan_submission(
                                    page, assignment, events.stage, cancelled
                                )
                                assignment.submitted_at = submitted_at
                            except Exception as error:
                                LOGGER.error(
                                    "Assignment scan failed: %s", type(error).__name__
                                )
                                events.error("Assignment", redact_sensitive(error))
                                stats.failed += 1
                                continue

                            try:
                                assignment_dir = assignment_archive_path(
                                    self.config.archive_path,
                                    course.id,
                                    course.code,
                                    course.name,
                                    assignment.id,
                                    assignment.name,
                                )
                                submission_dir = assignment_dir / "Submission"
                                metadata_path = assignment_dir / "metadata.json"
                                previous_files = self._previous_files(
                                    metadata_path,
                                    course.id,
                                    assignment.id,
                                )
                            except (OSError, ValueError) as error:
                                LOGGER.error(
                                    "Assignment archive setup failed: %s",
                                    type(error).__name__,
                                )
                                events.error(
                                    "Assignment",
                                    "Could not prepare this assignment's archive folder.",
                                )
                                stats.failed += 1
                                continue

                            file_records: list[dict[str, Any]] = []
                            used_names: set[str] = set()
                            reserved_names = {
                                sanitize_filename(
                                    str(record.get("filename") or "unknown_file"),
                                    "unknown_file",
                                ).casefold()
                                for record in previous_files.values()
                            }

                            for item in files:
                                if cancelled():
                                    break
                                file_id = item.stable_id or source_fingerprint(
                                    item.source_url
                                )
                                previous = previous_files.get(file_id, {})
                                filename = choose_archive_filename(
                                    item.filename,
                                    str(previous.get("filename"))
                                    if previous.get("filename")
                                    else None,
                                    used_names,
                                    reserved_names,
                                )
                                events.file_started(filename)
                                try:
                                    if options.assignment_submissions:
                                        downloader.refresh_from_page(page)
                                        result = downloader.download(
                                            item,
                                            submission_dir / filename,
                                            str(previous.get("source_fingerprint") or "")
                                            or None,
                                            events.file_progress,
                                            cancelled,
                                        )
                                    else:
                                        result = DownloadResult(
                                            DownloadStatus.SKIPPED,
                                            expected_size=item.expected_size,
                                        )
                                except (OSError, ValueError) as error:
                                    LOGGER.error(
                                        "Download setup failed: %s", type(error).__name__
                                    )
                                    result = DownloadResult(
                                        DownloadStatus.FAILED,
                                        error="Could not safely prepare this download.",
                                    )
                                if options.assignment_submissions:
                                    stats.record(result.status)
                                events.file_completed(filename, result.status)
                                if result.status is DownloadStatus.FAILED:
                                    events.error("Download", redact_sensitive(result.error))
                                file_records.append(
                                    {
                                        "filename": filename,
                                        "file_id": file_id,
                                        "source_fingerprint": file_id,
                                        "expected_size": result.expected_size,
                                        "local_size": result.size,
                                        "status": result.status.value,
                                        "error": result.error,
                                    }
                                )

                            if options.submission_metadata:
                                try:
                                    assignment_dir.mkdir(parents=True, exist_ok=True)
                                    self._write_metadata(
                                        metadata_path,
                                        course,
                                        assignment,
                                        file_records,
                                    )
                                except OSError as error:
                                    LOGGER.error(
                                        "Metadata write failed: %s", type(error).__name__
                                    )
                                    events.error(
                                        "Metadata",
                                        "Could not save this assignment's metadata.",
                                    )
                                    stats.failed += 1
                            stats.assignments += 1
                    final_status = "cancelled" if cancelled() else "complete"
                finally:
                    context.close()
        except Exception as error:
            final_status = "failed"
            LOGGER.error("Backup run failed: %s", type(error).__name__)
            events.error("Backup", redact_sensitive(error))
        finally:
            downloader.close()
            if run_id is not None:
                try:
                    self.database.finish_backup_run(run_id, final_status, stats)
                except Exception as error:
                    LOGGER.error(
                        "Could not persist the final backup-run state: %s",
                        type(error).__name__,
                    )
        return stats

    @staticmethod
    def _previous_files(
        metadata_path: Path,
        expected_course_id: object,
        expected_assignment_id: object,
    ) -> dict[str, dict[str, str]]:
        if not metadata_path.exists():
            return {}
        try:
            data = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return {}
        if not isinstance(data, dict):
            return {}

        if (
            str(data.get("course_id")) != str(expected_course_id)
            or str(data.get("assignment_id")) != str(expected_assignment_id)
        ):
            raise ValueError("Existing metadata belongs to another LMS object.")

        records: dict[str, dict[str, str]] = {}
        for item in data.get("files", []):
            filename = item.get("filename")
            fingerprint = item.get("source_fingerprint")
            if not fingerprint and item.get("source_url"):
                fingerprint = source_fingerprint(str(item["source_url"]))
            file_id = item.get("file_id") or fingerprint
            if filename and fingerprint and file_id:
                records[str(file_id)] = {
                    "filename": str(filename),
                    "source_fingerprint": str(fingerprint),
                }
        return records

    @staticmethod
    def _write_metadata(
        path: Path,
        course: Course,
        assignment: Assignment,
        files: list[dict[str, Any]],
    ) -> None:
        payload = {
            "course_id": course.id,
            "course_code": course.code,
            "course_name": course.name,
            "assignment_id": assignment.id,
            "assignment_name": assignment.name,
            "submitted_at": assignment.submitted_at,
            "summary": assignment.summary,
            "files": files,
        }
        part_path = path.with_name(f"{path.name}.part")
        part_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(part_path, path)
