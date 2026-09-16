import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from coursecarry.core.course_cache import (
    CourseCache,
    CourseCacheStore,
    cache_is_from_earlier_day,
    format_last_scan,
    merge_course_results,
)
from coursecarry.models import Course


class CourseCacheTests(TestCase):
    def test_loads_and_deduplicates_cached_courses_by_lms_id(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "courses.json"
            path.write_text(
                json.dumps(
                    {
                        "last_successful_scan_at": "2026-08-28T06:30:00+00:00",
                        "courses": [
                            {"id": 10, "name": "Old title"},
                            {"id": 10, "name": "Latest title"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            cache = CourseCacheStore(path).load()
            self.assertEqual(len(cache.courses), 1)
            self.assertEqual(cache.courses[0].name, "Latest title")
            self.assertEqual(
                cache.last_successful_scan_at, "2026-08-28T06:30:00+00:00"
            )

    def test_saves_scan_timestamp_and_course_state_atomically(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "courses.json"
            store = CourseCacheStore(path)
            store.save(
                CourseCache(
                    [Course(7, "Design", category="archived", available=True)],
                    "2026-09-02T06:30:00+00:00",
                )
            )
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["schema_version"], 2)
            self.assertEqual(data["last_successful_scan_at"], "2026-09-02T06:30:00+00:00")
            self.assertEqual(data["courses"][0]["category"], "archived")
            self.assertFalse(path.with_name("courses.json.part").exists())


class CourseMergeTests(TestCase):
    def test_merges_current_and_archived_without_duplicates(self) -> None:
        scanned_at = "2026-09-02T06:30:00+00:00"
        merged = merge_course_results(
            [Course(1, "Cached", category="current")],
            [
                Course(1, "Current title", category="current"),
                Course(2, "Archived title", category="archived"),
                Course(2, "Archived title", category="archived"),
            ],
            scanned_at=scanned_at,
            complete=True,
        )
        self.assertEqual({course.id for course in merged}, {1, 2})
        self.assertEqual(len(merged), 2)
        self.assertTrue(all(course.available for course in merged))
        self.assertTrue(all(course.last_seen_at == scanned_at for course in merged))

    def test_missing_course_is_only_marked_unavailable_after_complete_scan(self) -> None:
        cached = [Course(1, "Still here"), Course(2, "Missing for now")]
        incomplete = merge_course_results(
            cached,
            [Course(1, "Still here")],
            scanned_at="2026-09-02T06:30:00+00:00",
            complete=False,
        )
        complete = merge_course_results(
            cached,
            [Course(1, "Still here")],
            scanned_at="2026-09-02T06:30:00+00:00",
            complete=True,
        )
        self.assertTrue(next(course for course in incomplete if course.id == 2).available)
        self.assertFalse(next(course for course in complete if course.id == 2).available)

    def test_repeated_rescan_does_not_duplicate_courses(self) -> None:
        first = merge_course_results(
            [],
            [Course(42, "Course")],
            scanned_at="2026-09-01T06:30:00+00:00",
            complete=True,
        )
        second = merge_course_results(
            first,
            [Course(42, "Course")],
            scanned_at="2026-09-02T06:30:00+00:00",
            complete=True,
        )
        self.assertEqual([course.id for course in second], [42])


class ScanTimestampTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 9, 2, 14, 30, tzinfo=timezone.utc)

    def test_formats_never_today_yesterday_and_older(self) -> None:
        self.assertEqual(format_last_scan(None, now=self.now), "Never scanned")
        self.assertEqual(
            format_last_scan("2026-09-02T06:30:00+00:00", now=self.now),
            "Last scanned today at 6:30 AM",
        )
        self.assertEqual(
            format_last_scan("2026-09-01T06:30:00+00:00", now=self.now),
            "Last scanned yesterday",
        )
        self.assertEqual(
            format_last_scan("2026-08-28T06:30:00+00:00", now=self.now),
            "Last scanned 28 Aug 2026",
        )

    def test_detects_cache_from_earlier_day(self) -> None:
        self.assertTrue(
            cache_is_from_earlier_day("2026-09-01T23:59:00+00:00", now=self.now)
        )
        self.assertFalse(
            cache_is_from_earlier_day("2026-09-02T00:01:00+00:00", now=self.now)
        )
