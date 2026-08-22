from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from playwright.sync_api import BrowserContext, Page, Playwright

from ..models import Assignment, BackupFile, Course


StatusCallback = Callable[[str], None]
CancelCallback = Callable[[], bool]


class LMSProvider(ABC):
    @abstractmethod
    def open_context(self, playwright: Playwright) -> BrowserContext:
        raise NotImplementedError

    @abstractmethod
    def wait_for_courses(
        self,
        context: BrowserContext,
        on_status: StatusCallback,
        cancelled: CancelCallback,
    ) -> list[Course]:
        raise NotImplementedError

    @abstractmethod
    def scan_assignments(
        self,
        page: Page,
        course: Course,
        on_status: StatusCallback,
        cancelled: CancelCallback,
    ) -> list[Assignment]:
        raise NotImplementedError

    @abstractmethod
    def scan_submission(
        self,
        page: Page,
        assignment: Assignment,
        on_status: StatusCallback,
        cancelled: CancelCallback,
    ) -> tuple[list[BackupFile], str | None]:
        raise NotImplementedError
