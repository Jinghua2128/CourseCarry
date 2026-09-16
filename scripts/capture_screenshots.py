"""Render GitHub screenshots from the real UI using fake student data."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from coursecarry.config import AppConfig, ConfigStore
from coursecarry.core.database import CourseCarryDatabase
from coursecarry.models import Course
from coursecarry.ui.main_window import MainWindow
from coursecarry.ui.theme import APP_STYLESHEET, configure_app_font


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"


def process_events(app: QApplication) -> None:
    for _ in range(4):
        app.processEvents()


def capture(window: MainWindow, app: QApplication, name: str) -> None:
    process_events(app)
    if not window.grab().save(str(SCREENSHOTS_DIR / name), "PNG"):
        raise RuntimeError(f"Could not save screenshot: {name}")


def main() -> int:
    app = QApplication([])
    app.setApplicationName("CourseCarry")
    app.setOrganizationName("CourseCarry")
    app.setStyle("Fusion")
    configure_app_font(app)
    app.setStyleSheet(APP_STYLESHEET)

    fake_courses = [
        Course(100101, "Applied Artificial Intelligence", "26S1-1_AAI_000101", category="current"),
        Course(100102, "Cloud Architecture Fundamentals", "26S1-1_CAF_000102", category="current"),
        Course(100103, "Secure Software Development", "26S1-1_SSD_000103", category="current"),
        Course(900201, "Data Structures and Algorithms", "25S2-1_DSA_000201", category="archived"),
        Course(900202, "User Experience Design", "25S1-1_UXD_000202", category="archived", available=False),
    ]

    with tempfile.TemporaryDirectory(prefix="coursecarry-screenshots-") as temp_dir:
        temp = Path(temp_dir)
        config = AppConfig(
            archive_dir=r"C:\Users\Student\Documents\CourseCarry Archive",
            browser_profile_dir=r"C:\Users\Student\AppData\Local\CourseCarry\browser-data",
            first_run=False,
            animations=False,
        )
        store = ConfigStore(temp / "config.json")
        database = CourseCarryDatabase(temp / "coursecarry.db")
        database.initialize()
        window = MainWindow(config, store, database)
        window.resize(1220, 790)
        window._set_courses(fake_courses)
        window.courses_page.set_last_scan("Last scanned today at 2:30 PM")
        window.dashboard.set_scan_status("Last scanned today at 2:30 PM")
        window.show()

        window._navigate(0)
        window.dashboard.set_stats(20, 47, 128, "5.8 GB", "21 Aug 2026")
        capture(window, app, "dashboard.png")

        window._navigate(1)
        window.courses_page.selected_ids.update({100101, 100102})
        window.courses_page.refresh()
        capture(window, app, "courses.png")

        window._navigate(2)
        window.backup_page.progress_title.setText("Ready")
        window.backup_page.progress_detail.setText(
            "Choose content and courses, then start the backup."
        )
        capture(window, app, "backup.png")

        window._navigate(4)
        capture(window, app, "settings.png")

        window.close()
        app.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
