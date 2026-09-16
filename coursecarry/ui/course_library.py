from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
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


class SelectableCourseRow(QFrame):
    selection_changed = Signal(int, bool)
    folder_requested = Signal(object)

    def __init__(self, course: Course, selected: bool) -> None:
        super().__init__()
        self.course = course
        self.setObjectName("CourseCard")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(14)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(selected)
        self.checkbox.setEnabled(course.available)
        self.checkbox.setAccessibleName(f"Select {course.name}")
        self.checkbox.toggled.connect(
            lambda checked: self.selection_changed.emit(course.id, checked)
        )
        layout.addWidget(self.checkbox, 0, Qt.AlignmentFlag.AlignTop)

        copy = QVBoxLayout()
        copy.setSpacing(3)
        title = QLabel(course.name)
        title.setObjectName("SectionTitle")
        title.setWordWrap(True)
        code = QLabel(course.code or "No course code")
        code.setObjectName("Muted")
        state = course.category.title() if course.category != "unknown" else extract_semester(course.code)
        if not course.available:
            state = "Unavailable after the latest complete scan"
        meta = QLabel(f"{state}  ·  Course ID {course.id}")
        meta.setObjectName("Unavailable" if not course.available else "Muted")
        meta.setWordWrap(True)
        copy.addWidget(title)
        copy.addWidget(code)
        copy.addWidget(meta)
        layout.addLayout(copy, 1)

        folder = QPushButton("Open Folder")
        folder.clicked.connect(lambda: self.folder_requested.emit(course))
        layout.addWidget(folder)


class CourseLibraryPage(QWidget):
    download_requested = Signal(object)
    folder_requested = Signal(object)
    scan_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.courses: list[Course] = []
        self.selected_ids: set[int] = set()
        self.current_semester = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 26)
        root.setSpacing(16)
        root.addWidget(
            page_heading(
                "Course library",
                "Choose courses to carry with you",
                "Saved courses appear immediately. Scanning is always your choice and opens Chrome only for the scan.",
            )
        )

        scan_row = QFrame()
        scan_row.setObjectName("Panel")
        scan_layout = QHBoxLayout(scan_row)
        scan_layout.setContentsMargins(16, 12, 16, 12)
        scan_copy = QVBoxLayout()
        scan_copy.setSpacing(2)
        self.scan_state = QLabel("Never scanned")
        self.scan_state.setObjectName("SectionTitle")
        self.scan_detail = QLabel("Use the saved list, or scan for newly released courses.")
        self.scan_detail.setObjectName("Muted")
        scan_copy.addWidget(self.scan_state)
        scan_copy.addWidget(self.scan_detail)
        scan_layout.addLayout(scan_copy, 1)
        self.scan_button = QPushButton("Scan for Updates")
        self.scan_button.clicked.connect(self.scan_requested)
        scan_layout.addWidget(self.scan_button)
        root.addWidget(scan_row)

        filters = QHBoxLayout()
        filters.setSpacing(10)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search by course name or code")
        self.search.setClearButtonEnabled(True)
        self.filter = QComboBox()
        self.filter.setMinimumWidth(145)
        self.filter.addItems(["All", "Current", "Archived", "Unavailable"])
        filters.addWidget(self.search, 1)
        filters.addWidget(self.filter)
        root.addLayout(filters)

        selection_row = QHBoxLayout()
        self.selection_count = QLabel("0 courses selected")
        self.selection_count.setObjectName("SelectionCount")
        select_all = QPushButton("Select All Visible")
        clear = QPushButton("Clear Selection")
        select_all.clicked.connect(self.select_all_visible)
        clear.clicked.connect(self.clear_selection)
        selection_row.addWidget(self.selection_count)
        selection_row.addStretch()
        selection_row.addWidget(select_all)
        selection_row.addWidget(clear)
        root.addLayout(selection_row)

        self.empty = QLabel(
            "No saved courses yet. Select Scan for Updates when you are ready to sign in."
        )
        self.empty.setObjectName("EmptyState")
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty.setWordWrap(True)
        root.addWidget(self.empty, 1)

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
        self.list_layout.setSpacing(9)
        self.list_layout.addStretch()
        self.scroll.setWidget(self.container)
        root.addWidget(self.scroll, 1)

        action_row = QHBoxLayout()
        support = QLabel("Downloads your own assignment submissions and metadata only.")
        support.setObjectName("Muted")
        support.setWordWrap(True)
        self.download_button = QPushButton("Download Selected Courses")
        self.download_button.setObjectName("Primary")
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self._request_download)
        action_row.addWidget(support, 1)
        action_row.addWidget(self.download_button)
        root.addLayout(action_row)

        self.search.textChanged.connect(self.refresh)
        self.filter.currentTextChanged.connect(self.refresh)

    def set_courses(self, courses: list[Course]) -> None:
        available_ids = {course.id for course in courses if course.available}
        self.selected_ids.intersection_update(available_ids)
        semesters = sorted(
            {
                extract_semester(item.code)
                for item in courses
                if item.available and extract_semester(item.code) != "Non-Term"
            },
            reverse=True,
        )
        self.current_semester = semesters[0] if semesters else ""
        self.courses = sorted(
            courses,
            key=lambda item: (
                not item.available,
                0
                if item.category == "current"
                or (
                    item.category == "unknown"
                    and extract_semester(item.code) == self.current_semester
                )
                else 1,
                item.code.casefold(),
                item.name.casefold(),
                item.id,
            ),
        )
        self.refresh()

    def set_last_scan(self, text: str) -> None:
        self.scan_state.setText(text)

    def set_scan_status(self, detail: str) -> None:
        self.scan_detail.setText(detail)

    def _effective_category(self, course: Course) -> str:
        if not course.available:
            return "Unavailable"
        if course.category == "current":
            return "Current"
        if course.category == "archived":
            return "Archived"
        semester = extract_semester(course.code)
        return "Current" if semester == self.current_semester else "Archived"

    def _visible_courses(self) -> list[Course]:
        query = self.search.text().strip().casefold()
        selected_filter = self.filter.currentText() or "All"
        return [
            course
            for course in self.courses
            if (not query or query in f"{course.name} {course.code}".casefold())
            and (
                selected_filter == "All"
                or selected_filter == self._effective_category(course)
            )
        ]

    def refresh(self) -> None:
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()

        visible = self._visible_courses()
        for course in visible:
            row = SelectableCourseRow(course, course.id in self.selected_ids)
            row.selection_changed.connect(self._selection_changed)
            row.folder_requested.connect(self.folder_requested)
            self.list_layout.insertWidget(self.list_layout.count() - 1, row)

        if not self.courses:
            empty_text = "No saved courses yet. Select Scan for Updates when you are ready to sign in."
        else:
            empty_text = "No courses match this search and filter."
        self.empty.setText(empty_text)
        self.empty.setVisible(not visible)
        self.scroll.setVisible(bool(visible))
        self._update_selection_count()

    def _selection_changed(self, course_id: int, selected: bool) -> None:
        if selected:
            self.selected_ids.add(course_id)
        else:
            self.selected_ids.discard(course_id)
        self._update_selection_count()

    def select_all_visible(self) -> None:
        self.selected_ids.update(
            course.id for course in self._visible_courses() if course.available
        )
        self.refresh()

    def clear_selection(self) -> None:
        self.selected_ids.clear()
        self.refresh()

    def select_course(self, course: Course) -> None:
        if course.available:
            self.selected_ids.add(course.id)
            self.refresh()

    def selected_courses(self) -> list[Course]:
        return [
            course
            for course in self.courses
            if course.id in self.selected_ids and course.available
        ]

    def _update_selection_count(self) -> None:
        count = len(self.selected_courses())
        noun = "course" if count == 1 else "courses"
        self.selection_count.setText(f"{count} {noun} selected")
        self.download_button.setEnabled(count > 0)

    def _request_download(self) -> None:
        self.download_requested.emit(self.selected_courses())

    def set_busy(self, busy: bool) -> None:
        self.scan_button.setText("Cancel Scan" if busy else "Scan for Updates")
        self.download_button.setDisabled(busy or not self.selected_courses())
