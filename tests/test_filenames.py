from pathlib import Path
from unittest import TestCase

from politeload.utils.filenames import (
    assignment_archive_path,
    deduplicate_filename,
    extract_semester,
    sanitize_filename,
)


class FilenameTests(TestCase):
    def test_sanitizes_only_windows_invalid_characters(self) -> None:
        self.assertEqual(sanitize_filename('Week 1: "Draft"?.pptx'), "Week 1_ _Draft__.pptx")

    def test_sanitizes_reserved_and_trailing_names(self) -> None:
        self.assertEqual(sanitize_filename("CON.txt"), "_CON.txt")
        self.assertEqual(sanitize_filename("Report. "), "Report")

    def test_extracts_generic_semester(self) -> None:
        self.assertEqual(extract_semester("26S1-1_SAMPLE_000001"), "26S1")
        self.assertEqual(extract_semester("25S2_SUPPORT"), "25S2")
        self.assertEqual(extract_semester("Internship"), "Non-Term")

    def test_builds_predictable_assignment_path(self) -> None:
        result = assignment_archive_path(
            Path("Archive"),
            123456,
            "26S1-1_TEST_000001",
            "Sample Course",
            "987654",
            "Week 1 / Upload",
        )
        self.assertEqual(
            result,
            Path(
                "Archive/26S1/26S1-1_TEST_000001 [course-123456]/Assignments/"
                "Week 1 _ Upload [assignment-987654]"
            ),
        )

    def test_deduplicates_case_insensitively(self) -> None:
        used: set[str] = set()
        self.assertEqual(deduplicate_filename("report.pdf", used), "report.pdf")
        self.assertEqual(deduplicate_filename("Report.pdf", used), "Report (2).pdf")
