from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QThread, QTimer, QUrl
from PySide6.QtGui import QCloseEvent, QDesktopServices
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..config import AppConfig, ConfigStore
from ..core.database import PoliteLoadDatabase
from ..core.workers import BackupWorker, CourseScanWorker
from ..models import BackupOptions, BackupStats, Course
from ..utils.filenames import assignment_archive_path, extract_semester, sanitize_filename
from ..version import __version__
from .activity import ActivityPage
from .backup import BackupPage
from .courses import CoursesPage
from .dashboard import DashboardPage
from .onboarding import OnboardingDialog
from .settings import SettingsPage


class MainWindow(QMainWindow):
    def __init__(
        self,
        config: AppConfig,
        config_store: ConfigStore,
        database: PoliteLoadDatabase,
    ) -> None:
        super().__init__()
        self.config = config
        self.config_store = config_store
        self.database = database
        self.courses = self._load_courses()
        self.worker_thread: QThread | None = None
        self.worker = None
        self.page_animation: QPropertyAnimation | None = None
        self.animated_page: QWidget | None = None

        self.setWindowTitle(f"PoliteLoad {__version__}")
        self.resize(1220, 790)
        self.setMinimumSize(980, 680)
        self._build_ui()
        self._connect_pages()
        self._set_courses(self.courses)
        self.refresh_dashboard()

        if self.config.first_run:
            QTimer.singleShot(100, self._show_onboarding)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(22, 24, 22, 22)
        sidebar_layout.setSpacing(7)
        brand = QLabel("POLITELOAD")
        brand.setObjectName("Brand")
        version = QLabel(f"v{__version__}\nEXPERIMENTAL BUILD")
        version.setObjectName("Version")
        sidebar_layout.addWidget(brand)
        sidebar_layout.addWidget(version)
        sidebar_layout.addSpacing(28)

        self.stack = QStackedWidget()
        self.dashboard = DashboardPage()
        self.courses_page = CoursesPage()
        self.backup_page = BackupPage()
        self.activity_page = ActivityPage()
        self.settings_page = SettingsPage(self.config)
        pages = [
            ("Dashboard", self.dashboard),
            ("Courses", self.courses_page),
            ("Backup", self.backup_page),
            ("Activity", self.activity_page),
            ("Settings", self.settings_page),
        ]
        group = QButtonGroup(self)
        group.setExclusive(True)
        self.nav_buttons: list[QPushButton] = []
        for index, (label, page) in enumerate(pages):
            self.stack.addWidget(page)
            button = QPushButton(label)
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, item=index: self._navigate(item))
            group.addButton(button)
            self.nav_buttons.append(button)
            sidebar_layout.addWidget(button)
            if index == 0:
                button.setChecked(True)
        sidebar_layout.addStretch()
        privacy = QLabel("Local-first backup\nNo password capture")
        privacy.setObjectName("Muted")
        sidebar_layout.addWidget(privacy)
        root.addWidget(sidebar)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        topbar = QFrame()
        topbar.setObjectName("TopBar")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(30, 14, 30, 14)
        topbar_layout.addWidget(QLabel("POLITEMall / Brightspace"))
        topbar_layout.addStretch()
        self.status = QLabel("●  Session unchecked")
        self.status.setObjectName("StatusUnknown")
        topbar_layout.addWidget(self.status)
        content_layout.addWidget(topbar)
        content_layout.addWidget(self.stack, 1)
        root.addWidget(content, 1)

    def _connect_pages(self) -> None:
        self.dashboard.scan_requested.connect(self.start_scan)
        self.dashboard.backup_requested.connect(lambda: self._navigate(2))
        self.dashboard.archive_requested.connect(self.open_archive)
        self.dashboard.activity_requested.connect(lambda: self._navigate(3))
        self.courses_page.scan_requested.connect(self.start_scan)
        self.courses_page.backup_requested.connect(self._backup_single_course)
        self.courses_page.folder_requested.connect(self._open_course_folder)
        self.backup_page.start_requested.connect(self.start_backup)
        self.backup_page.cancel_requested.connect(self.cancel_worker)
        self.activity_page.open_logs_requested.connect(self.open_logs)
        self.settings_page.open_logs_requested.connect(self.open_logs)
        self.settings_page.save_requested.connect(self.save_settings)

    def _show_onboarding(self) -> None:
        dialog = OnboardingDialog(str(self.config.archive_path), self)
        if dialog.exec():
            self.config.archive_dir = dialog.archive.text().strip()
            self.config.first_run = False
            self.config_store.save(self.config)
            self.settings_page.archive.setText(str(self.config.archive_path))
            self.activity_page.add("INFO", "First-run setup completed.")

    def _load_courses(self) -> list[Course]:
        try:
            data = json.loads(self.config.courses_path.read_text(encoding="utf-8"))
            return [Course.from_dict(item) for item in data.get("courses", [])]
        except (OSError, ValueError, TypeError, KeyError):
            return []

    def _set_courses(self, courses: list[Course]) -> None:
        self.courses = courses
        self.courses_page.set_courses(courses)
        self.backup_page.set_courses(courses)

    def start_scan(self) -> None:
        if self._job_running():
            if isinstance(self.worker, CourseScanWorker):
                self.cancel_worker()
                self.activity_page.add("INFO", "Course scan cancellation requested.")
            return
        self._navigate(1)
        self.courses_page.set_busy(True)
        self.status.setText("●  Checking session")
        self.status.setObjectName("StatusUnknown")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)
        self.activity_page.add("INFO", "Opening Chrome to scan visible courses.")

        thread = QThread(self)
        worker = CourseScanWorker(self.config, self.database)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.status_changed.connect(self._scan_status)
        worker.courses_ready.connect(self._scan_ready)
        worker.failed.connect(self._scan_failed)
        worker.completed.connect(thread.quit)
        worker.completed.connect(worker.deleteLater)
        thread.finished.connect(self._job_finished)
        thread.finished.connect(thread.deleteLater)
        self.worker_thread = thread
        self.worker = worker
        thread.start()

    def _scan_status(self, message: str) -> None:
        self.activity_page.add("INFO", message)

    def _scan_ready(self, courses: list[Course]) -> None:
        self._set_courses(courses)
        self.status.setText("●  Connected")
        self.status.setObjectName("StatusConnected")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)
        self.activity_page.add("INFO", f"Detected {len(courses)} courses.")
        self.refresh_dashboard()

    def _scan_failed(self, message: str) -> None:
        self.status.setText("●  Login required")
        self.status.setObjectName("StatusUnknown")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)
        self.activity_page.add("ERROR", message)
        QMessageBox.warning(self, "Course scan could not finish", message)

    def _backup_single_course(self, course: Course) -> None:
        self._navigate(2)
        self.backup_page.select_course(course)

    def start_backup(self, courses: list[Course], options: BackupOptions) -> None:
        if self._job_running():
            return
        if not courses:
            QMessageBox.information(self, "Choose a course", "Scan or select at least one course first.")
            return
        if not options.assignment_submissions and not options.submission_metadata:
            QMessageBox.information(self, "Choose content", "Select at least one available backup option.")
            return

        self.backup_page.set_running(True)
        self.activity_page.add("INFO", f"Backup started for {len(courses)} course(s).")
        thread = QThread(self)
        worker = BackupWorker(self.config, self.database, courses, options)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.stage_changed.connect(self._backup_stage)
        worker.course_changed.connect(self.backup_page.set_course)
        worker.assignment_changed.connect(self.backup_page.set_assignment)
        worker.file_changed.connect(self.backup_page.set_file)
        worker.file_progress_changed.connect(self.backup_page.set_file_progress)
        worker.file_completed_changed.connect(
            lambda name, status: self.activity_page.add("INFO", f"{status.title()}: {name}")
        )
        worker.error_occurred.connect(
            lambda scope, message: self.activity_page.add("ERROR", f"{scope}: {message}")
        )
        worker.finished.connect(self._backup_finished)
        worker.finished.connect(lambda *_: thread.quit())
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(self._job_finished)
        thread.finished.connect(thread.deleteLater)
        self.worker_thread = thread
        self.worker = worker
        thread.start()

    def _backup_stage(self, message: str) -> None:
        self.backup_page.set_stage(message)
        self.activity_page.add("INFO", message)

    def _backup_finished(self, stats: BackupStats, cancelled: bool) -> None:
        self.backup_page.finish(stats, cancelled)
        self.refresh_dashboard()
        title = "Backup Cancelled" if cancelled else "Backup Complete"
        message_box = QMessageBox(self)
        message_box.setWindowTitle(title)
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setText(title)
        message_box.setInformativeText(
            f"Downloaded     {stats.downloaded}\n"
            f"Skipped        {stats.skipped}\n"
            f"Updated        {stats.updated}\n"
            f"Failed         {stats.failed}\n"
            f"Incomplete     {stats.incomplete}"
        )
        view_activity = message_box.addButton("View Activity", QMessageBox.ButtonRole.ActionRole)
        message_box.addButton(QMessageBox.StandardButton.Close)
        message_box.exec()
        if message_box.clickedButton() is view_activity:
            self._navigate(3)

    def cancel_worker(self) -> None:
        if self.worker is not None and hasattr(self.worker, "cancel"):
            self.worker.cancel()

    def _job_running(self) -> bool:
        return bool(self.worker_thread and self.worker_thread.isRunning())

    def _job_finished(self) -> None:
        self.courses_page.set_busy(False)
        self.worker_thread = None
        self.worker = None

    def _navigate(self, index: int) -> None:
        if self.page_animation is not None and self.animated_page is not None:
            self.page_animation.stop()
            self.animated_page.setGraphicsEffect(None)
        self.stack.setCurrentIndex(index)
        if 0 <= index < len(self.nav_buttons):
            self.nav_buttons[index].setChecked(True)
        if self.config.animations:
            page = self.stack.currentWidget()
            effect = QGraphicsOpacityEffect(page)
            page.setGraphicsEffect(effect)
            animation = QPropertyAnimation(effect, b"opacity", self)
            animation.setDuration(150)
            animation.setStartValue(0.72)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            animation.finished.connect(lambda: page.setGraphicsEffect(None))
            self.page_animation = animation
            self.animated_page = page
            animation.start()

    def save_settings(self) -> None:
        self.settings_page.apply_to(self.config)
        self.config_store.save(self.config)
        self.activity_page.add("INFO", "Settings saved locally.")
        self.refresh_dashboard()

    def open_archive(self) -> None:
        self.config.archive_path.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.config.archive_path)))

    def open_logs(self) -> None:
        self.config.logs_dir.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.config.logs_dir)))

    def _open_course_folder(self, course: Course) -> None:
        folder = (
            self.config.archive_path
            / extract_semester(course.code)
            / sanitize_filename(course.code or course.name)
        )
        folder.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def refresh_dashboard(self) -> None:
        assignments = 0
        files = 0
        total_bytes = 0
        archive = self.config.archive_path
        if archive.exists():
            try:
                for path in archive.rglob("*"):
                    if not path.is_file():
                        continue
                    if path.name == "metadata.json":
                        assignments += 1
                    elif path.suffix != ".part":
                        files += 1
                    total_bytes += path.stat().st_size
            except OSError:
                pass
        last_value = "Never"
        last_backup = self.database.last_backup_at()
        if last_backup:
            try:
                last_value = datetime.fromisoformat(last_backup).strftime("%d %b %Y")
            except ValueError:
                last_value = "Recorded"
        self.dashboard.set_stats(
            len(self.courses),
            assignments,
            files,
            self._format_bytes(total_bytes),
            last_value,
        )

    @staticmethod
    def _format_bytes(value: int) -> str:
        amount = float(value)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if amount < 1024 or unit == "TB":
                return f"{amount:.1f} {unit}" if unit != "B" else f"{int(amount)} B"
            amount /= 1024
        return f"{amount:.1f} TB"

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._job_running():
            QMessageBox.information(
                self,
                "Backup is still running",
                "Cancel the active operation and wait for it to stop safely before closing PoliteLoad.",
            )
            event.ignore()
            return
        event.accept()
