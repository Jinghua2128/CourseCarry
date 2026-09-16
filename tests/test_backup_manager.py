from unittest import TestCase

from coursecarry.core.backup_manager import choose_archive_filename


class StableArchiveFilenameTests(TestCase):
    def test_new_same_named_file_does_not_take_a_reserved_previous_name(self) -> None:
        used: set[str] = set()
        reserved = {"report.pdf"}
        new_filename = choose_archive_filename("report.pdf", None, used, reserved)
        existing_filename = choose_archive_filename(
            "renamed-by-lms.pdf", "report.pdf", used, reserved
        )
        self.assertEqual(new_filename, "report (2).pdf")
        self.assertEqual(existing_filename, "report.pdf")

    def test_previous_filename_is_reused_when_order_changes(self) -> None:
        used: set[str] = set()
        reserved = {"first.pdf", "second.pdf"}
        second = choose_archive_filename("duplicate.pdf", "second.pdf", used, reserved)
        first = choose_archive_filename("duplicate.pdf", "first.pdf", used, reserved)
        self.assertEqual(second, "second.pdf")
        self.assertEqual(first, "first.pdf")
