from unittest import TestCase

from coursecarry.providers.np_brightspace import (
    NPBrightspaceProvider,
    classify_course_view,
    extract_course_id,
    extract_query_value,
    is_trusted_course_page_url,
    merge_discovered_courses,
)
from coursecarry.models import Course


class ParsingTests(TestCase):
    def test_classifies_current_and_archived_views(self) -> None:
        self.assertEqual(classify_course_view("Current Courses"), "current")
        self.assertEqual(classify_course_view("Past Courses"), "archived")
        self.assertEqual(classify_course_view("View All Courses"), "unknown")

    def test_accumulates_course_views_by_stable_id(self) -> None:
        discovered = {1: Course(1, "Current", category="current")}
        added = merge_discovered_courses(
            discovered,
            [
                Course(1, "Current", category="archived"),
                Course(2, "Past", category="archived"),
            ],
        )
        self.assertEqual(added, 1)
        self.assertEqual(discovered[1].category, "current")
        self.assertEqual(discovered[2].category, "archived")

    def test_parses_current_and_archived_cards_with_stable_ids(self) -> None:
        class TextLocator:
            def __init__(self, values: list[str]) -> None:
                self.values = values

            @property
            def first(self):
                return self

            def count(self) -> int:
                return len(self.values)

            def nth(self, index: int):
                return TextLocator([self.values[index]])

            def inner_text(self) -> str:
                return self.values[0]

        class Card:
            def __init__(self, course_id: int, name: str, code: str) -> None:
                self.href = f"/d2l/home/{course_id}"
                self.name = name
                self.code = code

            def get_attribute(self, name: str):
                if name == "href":
                    return self.href
                if name == "text":
                    return f"{self.code} {self.name}"
                return None

            def locator(self, selector: str):
                if selector == ".d2l-organization-name":
                    return TextLocator([self.name])
                return TextLocator([self.code])

        class Cards:
            def __init__(self, cards: list[Card]) -> None:
                self.cards = cards

            def count(self) -> int:
                return len(self.cards)

            def nth(self, index: int) -> Card:
                return self.cards[index]

        cards = Cards([Card(10, "Design", "26S1-DES")])
        current = NPBrightspaceProvider._courses_from_cards(cards, "current")
        archived = NPBrightspaceProvider._courses_from_cards(cards, "archived")
        self.assertEqual(current[0].id, 10)
        self.assertEqual(current[0].category, "current")
        self.assertEqual(archived[0].category, "archived")
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

    def test_load_more_can_repeat_after_new_courses_are_found(self) -> None:
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
                return "Load More" if name == "aria-label" else None

            def inner_text(self, timeout: int) -> str:
                return "Load More"

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
            NPBrightspaceProvider._open_additional_course_view(page, opened, 2),
            "Load More",
        )
        self.assertIsNone(
            NPBrightspaceProvider._open_additional_course_view(page, opened, 2)
        )
        self.assertEqual(
            NPBrightspaceProvider._open_additional_course_view(page, opened, 3),
            "Load More",
        )
        self.assertEqual(page.candidate.clicks, 2)
