from unittest import TestCase

from coursecarry.providers.np_brightspace import (
    NPBrightspaceProvider,
    extract_course_id,
    extract_query_value,
    is_trusted_course_page_url,
)


class ParsingTests(TestCase):
    def test_extracts_course_id(self) -> None:
        self.assertEqual(extract_course_id("/d2l/home/123456"), 123456)
        self.assertIsNone(extract_course_id("/d2l/home/not-a-number"))

    def test_extracts_assignment_id_from_query(self) -> None:
        url = "https://example.invalid/folders_history.d2l?ou=12&db=654321"
        self.assertEqual(extract_query_value(url, "db"), "654321")
        self.assertIsNone(extract_query_value(url, "missing"))

    def test_course_cards_are_trusted_on_portal_or_lms_origin(self) -> None:
        portal = "https://portal.example.invalid"
        lms = "https://lms.example.invalid"
        self.assertTrue(
            is_trusted_course_page_url("https://portal.example.invalid/home", portal, lms)
        )
        self.assertTrue(
            is_trusted_course_page_url("https://lms.example.invalid/d2l/home", portal, lms)
        )
        self.assertFalse(
            is_trusted_course_page_url("https://evil.example.invalid/courses", portal, lms)
        )
        self.assertFalse(
            is_trusted_course_page_url("http://lms.example.invalid/d2l/home", portal, lms)
        )

    def test_my_courses_entry_is_opened_when_visible(self) -> None:
        class Candidate:
            clicked = False

            def count(self) -> int:
                return 1

            def nth(self, index: int):
                return self

            def is_visible(self) -> bool:
                return True

            def click(self, timeout: int) -> None:
                self.clicked = True

            def filter(self, **kwargs):
                return self

        class Page:
            candidate = Candidate()

            def get_by_role(self, *args, **kwargs):
                return self.candidate

            def locator(self, *args, **kwargs):
                return self.candidate

        page = Page()
        self.assertTrue(NPBrightspaceProvider._open_course_listing(page))
        self.assertTrue(page.candidate.clicked)

    def test_archived_course_control_is_opened_only_once_per_view(self) -> None:
        class Candidate:
            clicks = 0

            def count(self) -> int:
                return 1

            def nth(self, index: int):
                return self

            def is_visible(self) -> bool:
                return True

            def is_enabled(self) -> bool:
                return True

            def get_attribute(self, name: str):
                return "Archived Courses" if name == "aria-label" else None

            def inner_text(self, timeout: int) -> str:
                return "Archived Courses"

            def click(self, timeout: int) -> None:
                self.clicks += 1

            def filter(self, **kwargs):
                return self

        class Page:
            candidate = Candidate()

            def get_by_role(self, *args, **kwargs):
                return self.candidate

            def locator(self, *args, **kwargs):
                return self.candidate

        page = Page()
        opened: set[str] = set()
        self.assertEqual(
            NPBrightspaceProvider._open_additional_course_view(page, opened, 4),
            "Archived Courses",
        )
        self.assertIsNone(
            NPBrightspaceProvider._open_additional_course_view(page, opened, 4)
        )
        self.assertEqual(page.candidate.clicks, 1)
