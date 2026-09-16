from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DownloadStatus(StrEnum):
    DOWNLOADED = "downloaded"
    SKIPPED = "skipped"
    UPDATED = "updated"
    FAILED = "failed"
    INCOMPLETE = "incomplete"


@dataclass(slots=True)
class BackupFile:
    filename: str
    source_url: str
    expected_size: int | None = None
    stable_id: str | None = None


@dataclass(slots=True)
class BackupOptions:
    assignment_submissions: bool = True
    submission_metadata: bool = True


@dataclass(slots=True)
class BackupStats:
    courses: int = 0
    assignments: int = 0
    downloaded: int = 0
    skipped: int = 0
    updated: int = 0
    failed: int = 0
    incomplete: int = 0

    @property
    def total_files(self) -> int:
        return (
            self.downloaded
            + self.skipped
            + self.updated
            + self.failed
            + self.incomplete
        )

    def record(self, status: DownloadStatus) -> None:
        setattr(self, status.value, getattr(self, status.value) + 1)

    def to_dict(self) -> dict[str, int]:
        return {
            "courses": self.courses,
            "assignments": self.assignments,
            "downloaded": self.downloaded,
            "skipped": self.skipped,
            "updated": self.updated,
            "failed": self.failed,
            "incomplete": self.incomplete,
        }
