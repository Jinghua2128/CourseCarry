from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from ..models import BackupOptions, BackupStats, Course
from .components import page_heading


class BackupPage(QWidget):
    start_requested = Signal(object, object)
    cancel_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.courses: list[Course] = []
        root = QVBoxLayout(self)
        root.setContentsMargins(34, 28, 34, 30)
        root.setSpacing(18)
        root.addWidget(
            page_heading(
                "Backup",
                "Choose what to preserve",
                "Only content accessible to the logged-in student is requested.",
            )
        )

        columns = QHBoxLayout()
        columns.setSpacing(14)
        options_panel = QFrame()
        options_panel.setObjectName("Panel")
        options_layout = QVBoxLayout(options_panel)
        options_layout.setContentsMargins(20, 18, 20, 18)
        options_title = QLabel("Content")
        options_title.setObjectName("SectionTitle")
        options_layout.addWidget(options_title)
        self.submissions = QCheckBox("My assignment submissions")
        self.submissions.setChecked(True)
        self.metadata = QCheckBox("Submission metadata")
        self.metadata.setChecked(True)
        options_layout.addWidget(self.submissions)
        options_layout.addWidget(self.metadata)
        for label in (
            "Course materials  ·  Coming Soon",
            "Grades  ·  Coming Soon",
            "Feedback  ·  Coming Soon",
            "Other accessible files  ·  Coming Soon",
        ):
            checkbox = QCheckBox(label)
            checkbox.setDisabled(True)
            options_layout.addWidget(checkbox)
        options_layout.addStretch()
        columns.addWidget(options_panel, 1)

        courses_panel = QFrame()
        courses_panel.setObjectName("Panel")
        courses_layout = QVBoxLayout(courses_panel)
        courses_layout.setContentsMargins(20, 18, 20, 18)
        courses_title = QLabel("Courses")
        courses_title.setObjectName("SectionTitle")
        courses_layout.addWidget(courses_title)
        self.all_courses = QRadioButton("Backup all detected courses")
        self.selected_courses = QRadioButton("Select courses manually")
        self.all_courses.setChecked(True)
        self.course_list = QListWidget()
        self.course_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.course_list.setDisabled(True)
        self.all_courses.toggled.connect(lambda checked: self.course_list.setDisabled(checked))
        courses_layout.addWidget(self.all_courses)
        courses_layout.addWidget(self.selected_courses)
        courses_layout.addWidget(self.course_list, 1)
        columns.addWidget(courses_panel, 1)
        root.addLayout(columns, 1)

        self.progress_panel = QFrame()
        self.progress_panel.setObjectName("Panel")
        progress_layout = QVBoxLayout(self.progress_panel)
        progress_layout.setContentsMargins(20, 16, 20, 16)
        self.progress_title = QLabel("Ready")
        self.progress_title.setObjectName("SectionTitle")
        self.progress_detail = QLabel("Choose content and courses, then start the backup.")
        self.progress_detail.setObjectName("Muted")
        self.file_progress = QProgressBar()
        self.file_progress.setRange(0, 100)
        self.file_progress.setValue(0)
        self.course_progress = QProgressBar()
        self.course_progress.setRange(0, 100)
        self.course_progress.setValue(0)
        progress_layout.addWidget(self.progress_title)
        progress_layout.addWidget(self.progress_detail)
        progress_layout.addWidget(self.file_progress)
        progress_layout.addWidget(self.course_progress)
        root.addWidget(self.progress_panel)

        actions = QHBoxLayout()
        self.start_button = QPushButton("Start Backup")
        self.start_button.setObjectName("Primary")
        self.start_button.clicked.connect(self._request_start)
        self.cancel_button = QPushButton("Cancel Safely")
        self.cancel_button.setObjectName("Danger")
        self.cancel_button.setDisabled(True)
        self.cancel_button.clicked.connect(self.cancel_requested)
        actions.addStretch()
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.start_button)
        root.addLayout(actions)

    def set_courses(self, courses: list[Course]) -> None:
        self.courses = [course for course in courses if course.available]
        self.course_list.clear()
        for course in self.courses:
            item = QListWidgetItem(course.code or course.name)
            item.setData(Qt.ItemDataRole.UserRole, course)
            self.course_list.addItem(item)

    def select_course(self, course: Course) -> None:
        self.select_courses([course])

    def select_courses(self, courses: list[Course]) -> None:
        selected_ids = {course.id for course in courses if course.available}
        self.selected_courses.setChecked(True)
        for index in range(self.course_list.count()):
            item = self.course_list.item(index)
            item.setSelected(
                item.data(Qt.ItemDataRole.UserRole).id in selected_ids
            )

    def _request_start(self) -> None:
        if self.all_courses.isChecked():
            courses = self.courses
        else:
            courses = [item.data(Qt.ItemDataRole.UserRole) for item in self.course_list.selectedItems()]
        options = BackupOptions(
            assignment_submissions=self.submissions.isChecked(),
            submission_metadata=self.metadata.isChecked(),
        )
        self.start_requested.emit(courses, options)

    def set_running(self, running: bool) -> None:
        self.start_button.setDisabled(running)
        self.cancel_button.setEnabled(running)
        self.start_button.setText("Backup Running…" if running else "Start Backup")
        if running:
            self.file_progress.setRange(0, 0)

    def set_stage(self, text: str) -> None:
        self.progress_detail.setText(text)

    def set_course(self, index: int, total: int, course: Course) -> None:
        self.progress_title.setText(course.name)
        self.progress_detail.setText(f"Course {index} of {total}")
        self.course_progress.setRange(0, max(total, 1))
        self.course_progress.setValue(index - 1)

    def set_assignment(self, index: int, total: int, name: str) -> None:
        self.progress_detail.setText(f"Assignment {index} of {total}  ·  {name}")

    def set_file(self, filename: str) -> None:
        self.progress_detail.setText(f"Downloading  ·  {filename}")
        self.file_progress.setRange(0, 0)

    def set_file_progress(self, downloaded: int, total: int | None) -> None:
        if total:
            self.file_progress.setRange(0, 1000)
            self.file_progress.setValue(int(downloaded / total * 1000))
            self.progress_detail.setText(
                f"{downloaded / 1024 / 1024:.1f} MB / {total / 1024 / 1024:.1f} MB"
            )
        else:
            self.file_progress.setRange(0, 0)

    def finish(self, stats: BackupStats, cancelled: bool) -> None:
        self.set_running(False)
        self.file_progress.setRange(0, 100)
        self.file_progress.setValue(0 if cancelled else 100)
        self.course_progress.setValue(self.course_progress.maximum())
        self.progress_title.setText("Backup cancelled" if cancelled else "Backup complete")
        self.progress_detail.setText(
            f"Downloaded {stats.downloaded}  ·  Skipped {stats.skipped}  ·  "
            f"Updated {stats.updated}  ·  Failed {stats.failed}  ·  "
            f"Incomplete {stats.incomplete}"
        )
