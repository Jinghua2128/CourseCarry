from __future__ import annotations

import logging
import re
import time
from collections.abc import Callable
from urllib.parse import parse_qs, urljoin, urlparse

from playwright.sync_api import BrowserContext, Error as PlaywrightError, Page, Playwright

from ..config import AppConfig
from ..models import Assignment, BackupFile, Course
from ..utils.url_security import (
    is_same_https_origin,
    require_same_https_origin,
    source_fingerprint,
)
from .base import CancelCallback, LMSProvider, StatusCallback


LOGGER = logging.getLogger(__name__)


class BrowserUnavailableError(RuntimeError):
    pass


class AuthenticationTimeoutError(RuntimeError):
    pass


def extract_course_id(href: str) -> int | None:
    match = re.search(r"/d2l/home/(\d+)", href)
    return int(match.group(1)) if match else None


def extract_query_value(url: str, key: str) -> str | None:
    values = parse_qs(urlparse(url).query).get(key)
    return values[0] if values else None


def stable_file_id(url: str) -> str:
    """Use the stable LMS file path while excluding rotating private query values."""

    parsed = urlparse(url)
    return source_fingerprint(f"{parsed.scheme}://{parsed.netloc}{parsed.path}")


def is_trusted_course_page_url(
    url: str,
    portal_origin: str,
    lms_origin: str,
) -> bool:
    """Course cards may be rendered by either the portal or Brightspace."""

    return is_same_https_origin(url, portal_origin) or is_same_https_origin(
        url, lms_origin
    )


def classify_course_view(label: str) -> str:
    normalized = label.casefold()
    if re.search(r"\b(archived|past|previous|older|inactive)\b", normalized):
        return "archived"
    if re.search(r"\b(current|active)\b", normalized):
        return "current"
    if re.fullmatch(r"\s*(?:my\s+)?courses?\s*", normalized):
        return "current"
    return "unknown"


def merge_discovered_courses(
    discovered: dict[int, Course], incoming: list[Course]
) -> int:
    """Accumulate course views by stable id without reclassifying earlier cards."""

    before = len(discovered)
    for course in incoming:
        previous = discovered.get(course.id)
        if (
            previous is not None
            and previous.category != "unknown"
            and previous.category != course.category
        ):
            course.category = previous.category
        discovered[course.id] = course
    return len(discovered) - before


class BrightspaceProvider(LMSProvider):
    """Configurable Brightspace flow using normal browser authentication."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def open_context(self, playwright: Playwright) -> BrowserContext:
        self.config.browser_profile_path.mkdir(parents=True, exist_ok=True)
        launch_options: dict[str, object] = {
            "user_data_dir": str(self.config.browser_profile_path),
            "headless": False,
            "no_viewport": True,
            "accept_downloads": False,
        }
        if self.config.chrome_executable:
            launch_options["executable_path"] = self.config.chrome_executable
        else:
            launch_options["channel"] = "chrome"

        try:
            return playwright.chromium.launch_persistent_context(**launch_options)
        except PlaywrightError as error:
            raise BrowserUnavailableError(
                "Google Chrome could not be opened. Install Chrome or choose its "
                "executable in Settings."
            ) from error

    @staticmethod
    def active_page(context: BrowserContext) -> Page:
        usable = [page for page in context.pages if page.url != "about:blank"]
        if usable:
            return usable[-1]
        return context.pages[-1] if context.pages else context.new_page()

    def wait_for_courses(
        self,
        context: BrowserContext,
        on_status: StatusCallback,
        cancelled: CancelCallback,
    ) -> list[Course]:
        page = self.active_page(context)
        on_status(
            "Complete the institution's normal login. CourseCarry will then open My Courses; "
            "you can also click it yourself."
        )
        try:
            page.goto(self.config.base_url, wait_until="commit", timeout=15_000)
        except PlaywrightError as error:
            if "interrupted by another navigation" not in str(error):
                LOGGER.warning("Portal navigation did not complete: %s", type(error).__name__)

        deadline = time.monotonic() + 600
        next_course_entry_attempt = 0.0
        next_collection_attempt = 0.0
        discovered: dict[int, Course] = {}
        opened_controls: set[str] = set()
        last_discovery_at = time.monotonic()
        collection_hint = "current"
        while time.monotonic() < deadline:
            if cancelled():
                return []
            page = self.active_page(context)
            try:
                cards = page.locator('d2l-card[href*="/d2l/home/"]')
                if cards.count() > 0 and is_trusted_course_page_url(
                    page.url,
                    self.config.base_url,
                    self.config.lms_base_url,
                ):
                    page_hint = self._selected_course_view(page) or collection_hint
                    added = merge_discovered_courses(
                        discovered, self._courses_from_cards(cards, page_hint)
                    )
                    if added:
                        last_discovery_at = time.monotonic()
                        on_status(
                            f"Found {len(discovered)} course(s). Checking archived and "
                            "additional course views…"
                        )
            except PlaywrightError:
                pass

            now = time.monotonic()
            if (
                discovered
                and now >= next_collection_attempt
                and is_trusted_course_page_url(
                    page.url,
                    self.config.base_url,
                    self.config.lms_base_url,
                )
            ):
                next_collection_attempt = now + 1.5
                opened = self._open_additional_course_view(
                    page,
                    opened_controls,
                    len(discovered),
                )
                if opened:
                    opened_hint = classify_course_view(opened)
                    if opened_hint != "unknown":
                        collection_hint = opened_hint
                    elif re.search(r"\ball\s+courses\b", opened, re.IGNORECASE):
                        collection_hint = "unknown"
                    last_discovery_at = now
                    on_status(
                        f"Opened {opened}. Continuing to collect current and archived courses…"
                    )
                    if not self._interruptible_wait(page, 1_000, cancelled):
                        return []
                    continue
                self._nudge_course_loading(page)

            if discovered and now - last_discovery_at >= 8:
                courses = list(discovered.values())
                LOGGER.info("Authenticated course cards detected: %d", len(courses))
                return courses

            if (
                now >= next_course_entry_attempt
                and is_same_https_origin(page.url, self.config.base_url)
            ):
                next_course_entry_attempt = now + 5
                if self._open_course_listing(page):
                    on_status("Opening My Courses and waiting for the course list…")
                    if not self._interruptible_wait(page, 1_500, cancelled):
                        return []
                    continue
            if not self._interruptible_wait(page, 400, cancelled):
                return []

        raise AuthenticationTimeoutError(
            "Timed out waiting for My Courses. Open My Courses in Chrome and "
            "run Scan Courses again. No credentials were captured."
        )

    @staticmethod
    def _open_course_listing(page: Page) -> bool:
        """Open the post-login My Courses entry without assuming one HTML shape."""

        label = re.compile(r"^\s*(?:my\s+)?courses?\s*$", re.IGNORECASE)
        candidates = (
            page.get_by_role("link", name=label),
            page.get_by_role("button", name=label),
            page.locator("a, button, [role='link'], [role='button']").filter(
                has_text=label
            ),
        )
        for candidate in candidates:
            try:
                for index in range(min(candidate.count(), 5)):
                    target = candidate.nth(index)
                    if not target.is_visible():
                        continue
                    target.click(timeout=3_000)
                    return True
            except PlaywrightError:
                continue
        return False

    @staticmethod
    def _open_additional_course_view(
        page: Page,
        opened_controls: set[str],
        discovery_marker: int,
    ) -> str | None:
        """Open course collection controls while retaining already found courses."""

        label = re.compile(
            r"^\s*(?:"
            r"(?:view|show)\s+all\s+courses|"
            r"all\s+courses|"
            r"my\s+courses?|"
            r"archived(?:\s+courses)?|"
            r"(?:show\s+)?archived\s+courses|"
            r"(?:past|previous|older|inactive)(?:\s+courses)?|"
            r"(?:current|active)(?:\s+courses)?|"
            r"(?:course|semester|term)\s+(?:selector|filter)|"
            r"more\s+courses|"
            r"(?:load|show)\s+more"
            r")(?:\s*\(\d+\))?\s*$",
            re.IGNORECASE,
        )
        candidates = (
            page.get_by_role("button", name=label),
            page.get_by_role("link", name=label),
            page.get_by_role("tab", name=label),
            page.get_by_role("combobox", name=label),
            page.locator("summary").filter(has_text=label),
            page.locator(
                'd2l-my-courses button[aria-label*="Next" i], '
                'd2l-my-courses a[aria-label*="Next" i]'
            ),
        )
        for candidate in candidates:
            try:
                for index in range(min(candidate.count(), 8)):
                    target = candidate.nth(index)
                    if not target.is_visible() or not target.is_enabled():
                        continue
                    text = (
                        target.get_attribute("aria-label")
                        or target.inner_text(timeout=1_000)
                        or "additional courses"
                    ).strip()
                    identity = "|".join(
                        (
                            text.casefold(),
                            target.get_attribute("aria-controls") or "",
                            target.get_attribute("href") or "",
                        )
                    )
                    repeatable = bool(
                        re.match(
                            r"^\s*(?:(?:load|show)\s+more|next)\b",
                            text,
                            re.IGNORECASE,
                        )
                    )
                    if repeatable:
                        identity = f"{identity}|batch:{discovery_marker}"
                    if identity in opened_controls:
                        continue
                    target.click(timeout=3_000)
                    opened_controls.add(identity)
                    return text or "additional courses"
            except PlaywrightError:
                continue
        return None

    @staticmethod
    def _nudge_course_loading(page: Page) -> None:
        """Trigger ordinary lazy loading without bypassing any access control."""

        try:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.mouse.wheel(0, 1_200)
        except PlaywrightError:
            pass

    @staticmethod
    def _selected_course_view(page: Page) -> str | None:
        try:
            selected = page.locator(
                '[aria-selected="true"], [aria-current="page"], '
                'option:checked'
            )
            for index in range(min(selected.count(), 8)):
                text = selected.nth(index).inner_text(timeout=500).strip()
                category = classify_course_view(text)
                if category != "unknown":
                    return category
        except PlaywrightError:
            pass
        return None

    @staticmethod
    def _interruptible_wait(
        page: Page,
        milliseconds: int,
        cancelled: CancelCallback,
    ) -> bool:
        remaining = milliseconds
        while remaining > 0:
            if cancelled():
                return False
            interval = min(remaining, 100)
            page.wait_for_timeout(interval)
            remaining -= interval
        return not cancelled()

    @staticmethod
    def _courses_from_cards(cards, category: str = "unknown") -> list[Course]:
        courses: list[Course] = []
        seen: set[int] = set()
        for index in range(cards.count()):
            card = cards.nth(index)
            href = card.get_attribute("href") or ""
            course_id = extract_course_id(href)
            if course_id is None or course_id in seen:
                continue
            seen.add(course_id)

            full_text = card.get_attribute("text") or ""
            name_locator = card.locator(".d2l-organization-name")
            name = (
                name_locator.first.inner_text().strip()
                if name_locator.count()
                else full_text.strip()
            )
            code = ""
            code_locator = card.locator(".d2l-organization-code")
            for code_index in range(code_locator.count()):
                candidate = code_locator.nth(code_index).inner_text().strip()
                if candidate:
                    code = candidate
                    break

            courses.append(
                Course(
                    id=course_id,
                    name=name or f"Course {course_id}",
                    code=code,
                    href=href,
                    full_text=full_text,
                    category=category,
                )
            )
        return courses

    def navigate(
        self,
        page: Page,
        url: str,
        on_status: StatusCallback,
        cancelled: CancelCallback,
    ) -> Page:
        require_same_https_origin(url, self.config.lms_base_url)
        try:
            page.goto(url, wait_until="commit", timeout=15_000)
        except PlaywrightError as error:
            if "interrupted by another navigation" not in str(error):
                raise

        if not self._interruptible_wait(page, 2_000, cancelled):
            return page
        if "login.microsoftonline.com" in page.url:
            on_status("Login required — complete Microsoft / school SSO and MFA in Chrome.")
            deadline = time.monotonic() + 600
            while "login.microsoftonline.com" in page.url and time.monotonic() < deadline:
                if cancelled():
                    return page
                page.wait_for_timeout(500)
            if "login.microsoftonline.com" in page.url:
                raise AuthenticationTimeoutError("Timed out waiting for normal browser login.")
            try:
                page.goto(url, wait_until="commit", timeout=15_000)
            except PlaywrightError as error:
                if "interrupted by another navigation" not in str(error):
                    raise
            if not self._interruptible_wait(page, 2_000, cancelled):
                return page
        require_same_https_origin(page.url, self.config.lms_base_url)
        return page

    def scan_assignments(
        self,
        page: Page,
        course: Course,
        on_status: StatusCallback,
        cancelled: CancelCallback,
    ) -> list[Assignment]:
        url = (
            f"{self.config.lms_base_url}/d2l/lms/dropbox/user/"
            f"folders_list.d2l?ou={course.id}&isprv=0"
        )
        page = self.navigate(page, url, on_status, cancelled)

        links = page.locator('a[href*="folders_history.d2l"]')
        assignments: list[Assignment] = []
        seen: set[str] = set()
        for index in range(links.count()):
            link = links.nth(index)
            href = link.get_attribute("href") or ""
            assignment_id = extract_query_value(href, "db")
            if not href or not assignment_id or assignment_id in seen:
                continue
            full_url = urljoin(self.config.lms_base_url, href)
            if not is_same_https_origin(full_url, self.config.lms_base_url):
                continue
            seen.add(assignment_id)
            title = link.get_attribute("title") or ""
            prefix = "Submission history for "
            name = title[len(prefix) :] if title.startswith(prefix) else title
            assignment = Assignment(
                id=assignment_id,
                course_id=course.id,
                name=name or f"Assignment {assignment_id}",
                url=full_url,
                summary=link.inner_text().strip(),
            )
            assignments.append(assignment)
        LOGGER.info("Assignment records detected: %d", len(assignments))
        return assignments

    def scan_submission(
        self,
        page: Page,
        assignment: Assignment,
        on_status: StatusCallback,
        cancelled: CancelCallback,
    ) -> tuple[list[BackupFile], str | None]:
        page = self.navigate(page, assignment.url, on_status, cancelled)
        links = page.locator('a[href*="/d2l/common/viewFile.d2lfile/"]')
        files: list[BackupFile] = []
        seen: set[str] = set()
        for index in range(links.count()):
            link = links.nth(index)
            href = link.get_attribute("href") or ""
            full_url = urljoin(self.config.lms_base_url, href)
            if (
                not href
                or not is_same_https_origin(full_url, self.config.lms_base_url)
                or full_url in seen
            ):
                continue
            seen.add(full_url)
            files.append(
                BackupFile(
                    filename=link.inner_text().strip() or "unknown_file",
                    source_url=full_url,
                    stable_id=stable_file_id(full_url),
                )
            )

        submitted_at = None
        labels = page.locator("label")
        for index in range(labels.count()):
            text = labels.nth(index).inner_text().strip()
            if re.search(r"\d{1,2}\s+\w+\s+\d{4}", text):
                submitted_at = text
                break
        return files, submitted_at


class NPBrightspaceProvider(BrightspaceProvider):
    """The Brightspace flow with NP's tested portal and LMS URL preset."""
