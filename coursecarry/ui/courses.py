from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..models import Course
from ..utils.filenames import extract_semester
from .components import page_heading


class CourseCard(QFrame):
    backup_requested = Signal(object)
    folder_requested = Signal(object)

    def __init__(self, course: Course) -> None:
        super().__init__()
        self.course = course
        self.setObjectName("CourseCard")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(19, 16, 19, 16)
        layout.setSpacing(18)

        copy = QVBoxLayout()
        copy.setSpacing(4)
        title = QLabel(course.name)
        title.setObjectName("SectionTitle")
        title.setWordWrap(True)
        code = QLabel(course.code or "No course code")
        code.setObjectName("Muted")
        meta = QLabel(f"{extract_semester(course.code)}    •    Course ID {course.id}")
        meta.setObjectName("Muted")
        copy.addWidget(title)
        copy.addWidget(code)
        copy.addWidget(meta)
        layout.addLayout(copy, 1)

        backup = QPushButton("Backup")
        backup.clicked.connect(lambda: self.backup_requested.emit(self.course))
        folder = QPushButton("Open Folder")
        folder.clicked.connect(lambda: self.folder_requested.emit(self.course))
        layout.addWidget(backup)
        layout.addWidget(folder)


class CoursesPage(QWidget):
    backup_requested = Signal(object)
    folder_requested = Signal(object)
    scan_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.courses: list[Course] = []
        self.current_semester = ""
        root = QVBoxLayout(self)
        root.setContentsMargins(34, 28, 34, 30)
        root.setSpacing(20)
        root.addWidget(
            page_heading(
                "Library",
                "Courses",
                "Search, filter, and back up courses detected from your own account.",
            )
        )

        controls = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search course name or code")
        self.search.setClearButtonEnabled(True)
        self.filter = QComboBox()
        self.filter.setMinimumWidth(150)
        self.scan_button = QPushButton("Scan Courses")
        self.scan_button.setObjectName("Primary")
        self.scan_button.clicked.connect(self.scan_requested)
        controls.addWidget(self.search, 1)
        controls.addWidget(self.filter)
        controls.addWidget(self.scan_button)
        root.addLayout(controls)

        self.empty = QLabel("No courses detected yet. Open Chrome with Scan Courses to begin.")
        self.empty.setObjectName("Muted")
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.empty)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(
            "QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; }"
        )
        self.scroll.viewport().setAutoFillBackground(False)
        self.container = QWidget()
        self.container.setAutoFillBackground(False)
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setContentsMargins(0, 0, 4, 0)
        self.list_layout.setSpacing(10)
        self.list_layout.addStretch()
        self.scroll.setWidget(self.container)
        root.addWidget(self.scroll, 1)

        self.search.textChanged.connect(self.refresh)
        self.filter.currentTextChanged.connect(self.refresh)

    def set_courses(self, courses: list[Course]) -> None:
        self.courses = sorted(courses, key=lambda item: (item.code, item.name))
        semesters = sorted(
            {extract_semester(item.code) for item in courses if extract_semester(item.code) != "Non-Term"},
            reverse=True,
        )
        self.current_semester = semesters[0] if semesters else ""
        selected = self.filter.currentText()
        self.filter.blockSignals(True)
        self.filter.clear()
        self.filter.addItems(["All", "Current", "Archived", *semesters, "Non-Term"])
        index = self.filter.findText(selected)
        self.filter.setCurrentIndex(max(index, 0))
        self.filter.blockSignals(False)
        self.refresh()

    def refresh(self) -> None:
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()

        query = self.search.text().strip().casefold()
        selected_filter = self.filter.currentText() or "All"
        visible = []
        for course in self.courses:
            semester = extract_semester(course.code)
            text_matches = not query or query in f"{course.name} {course.code}".casefold()
            filter_matches = (
                selected_filter == "All"
                or selected_filter == semester
                or (selected_filter == "Current" and semester == self.current_semester)
                or (
                    selected_filter == "Archived"
                    and semester not in {"Non-Term", self.current_semester}
                )
            )
            if text_matches and filter_matches:
                visible.append(course)

        for course in visible:
            card = CourseCard(course)
            card.backup_requested.connect(self.backup_requested)
            card.folder_requested.connect(self.folder_requested)
            self.list_layout.insertWidget(self.list_layout.count() - 1, card)
        self.empty.setVisible(not visible)
        self.scroll.setVisible(bool(visible))

    def set_busy(self, busy: bool) -> None:
        self.scan_button.setEnabled(True)
        self.scan_button.setText("Cancel Scan" if busy else "Scan Courses")
