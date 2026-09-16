from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..models import Course


@dataclass(slots=True)
class CourseCache:
    courses: list[Course]
    last_successful_scan_at: str | None = None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def merge_course_results(
    cached: list[Course],
    discovered: list[Course],
    *,
    scanned_at: str,
    complete: bool,
) -> list[Course]:
    """Merge a scan by stable LMS id without silently losing cached courses."""

    merged = {course.id: Course.from_dict(course.to_dict()) for course in cached}
    for discovered_course in discovered:
        course = Course.from_dict(discovered_course.to_dict())
        previous = merged.get(course.id)
        if course.category == "unknown" and previous is not None:
            course.category = previous.category
        course.available = True
        course.last_seen_at = scanned_at
        merged[course.id] = course

    if complete:
        discovered_ids = {course.id for course in discovered}
        for course_id, course in merged.items():
            if course_id not in discovered_ids:
                course.available = False

    return sorted(
        merged.values(),
        key=lambda item: (item.code.casefold(), item.name.casefold(), item.id),
    )


def format_last_scan(value: str | None, *, now: datetime | None = None) -> str:
    if not value:
        return "Never scanned"
    try:
        scanned = datetime.fromisoformat(value)
    except ValueError:
        return "Last scan time unavailable"
    if scanned.tzinfo is None:
        scanned = scanned.replace(tzinfo=timezone.utc)
    local_now = now or datetime.now().astimezone()
    if local_now.tzinfo is None:
        local_now = local_now.replace(tzinfo=timezone.utc)
    local_scan = scanned.astimezone(local_now.tzinfo)
    if local_scan.date() == local_now.date():
        clock = local_scan.strftime("%I:%M %p").lstrip("0")
        return f"Last scanned today at {clock}"
    if local_scan.date() == (local_now - timedelta(days=1)).date():
        return "Last scanned yesterday"
    return f"Last scanned {local_scan.strftime('%d %b %Y')}"


def cache_is_from_earlier_day(value: str | None, *, now: datetime | None = None) -> bool:
    if not value:
        return False
    try:
        scanned = datetime.fromisoformat(value)
    except ValueError:
        return False
    if scanned.tzinfo is None:
        scanned = scanned.replace(tzinfo=timezone.utc)
    local_now = now or datetime.now().astimezone()
    if local_now.tzinfo is None:
        local_now = local_now.replace(tzinfo=timezone.utc)
    return scanned.astimezone(local_now.tzinfo).date() < local_now.date()


class CourseCacheStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> CourseCache:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            courses = [Course.from_dict(item) for item in data.get("courses", [])]
            courses = list({course.id: course for course in courses}.values())
            courses.sort(
                key=lambda item: (item.code.casefold(), item.name.casefold(), item.id)
            )
            return CourseCache(
                courses=courses,
                last_successful_scan_at=(
                    str(data["last_successful_scan_at"])
                    if data.get("last_successful_scan_at")
                    else None
                ),
            )
        except (OSError, ValueError, TypeError, KeyError):
            return CourseCache([])

    def save(self, cache: CourseCache) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 2,
            "last_successful_scan_at": cache.last_successful_scan_at,
            "course_count": len(cache.courses),
            "courses": [course.to_dict() for course in cache.courses],
        }
        part_path = self.path.with_name(f"{self.path.name}.part")
        part_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(part_path, self.path)
