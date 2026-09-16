from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .components import page_heading


class DashboardPage(QWidget):
    scan_requested = Signal()
    backup_requested = Signal()
    archive_requested = Signal()
    activity_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 26)
        root.setSpacing(18)
        root.addWidget(
            page_heading(
                "Overview",
                "Your CourseCarry archive",
                "Open the saved library, choose courses, and download your own assignment submissions.",
            )
        )

        next_step = QFrame()
        next_step.setObjectName("Panel")
        next_layout = QHBoxLayout(next_step)
        next_layout.setContentsMargins(20, 18, 20, 18)
        copy = QVBoxLayout()
        copy.setSpacing(4)
        self.scan_status = QLabel("Never scanned")
        self.scan_status.setObjectName("SectionTitle")
        detail = QLabel(
            "Your saved course list loads without opening Chrome. Scan only when you want updates."
        )
        detail.setObjectName("Muted")
        detail.setWordWrap(True)
        copy.addWidget(self.scan_status)
        copy.addWidget(detail)
        next_layout.addLayout(copy, 1)
        review = QPushButton("Review and Select Courses")
        review.setObjectName("Primary")
        review.clicked.connect(self.backup_requested)
        next_layout.addWidget(review)
        root.addWidget(next_step)

        summary = QFrame()
        summary.setObjectName("Panel")
        grid = QGridLayout(summary)
        grid.setContentsMargins(20, 18, 20, 18)
        grid.setHorizontalSpacing(28)
        grid.setVerticalSpacing(12)
        title = QLabel("Local archive summary")
        title.setObjectName("SectionTitle")
        grid.addWidget(title, 0, 0, 1, 4)
        self.values: dict[str, QLabel] = {}
        metrics = (
            ("Courses", "courses"),
            ("Assignments", "assignments"),
            ("Files", "files"),
            ("Storage", "storage"),
            ("Last backup", "last_backup"),
        )
        for index, (label, key) in enumerate(metrics):
            row = 1 + index // 3 * 2
            column = index % 3
            label_widget = QLabel(label)
            label_widget.setObjectName("Muted")
            value_widget = QLabel("—")
            value_widget.setObjectName("SummaryValue")
            grid.addWidget(label_widget, row, column)
            grid.addWidget(value_widget, row + 1, column)
            self.values[key] = value_widget
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        root.addWidget(summary)

        links = QHBoxLayout()
        for text, signal in (
            ("Scan for Updates", self.scan_requested),
            ("Open Archive", self.archive_requested),
            ("View Activity", self.activity_requested),
        ):
            button = QPushButton(text)
            button.clicked.connect(signal)
            links.addWidget(button)
        links.addStretch()
        root.addLayout(links)
        root.addStretch()

    def set_scan_status(self, text: str) -> None:
        self.scan_status.setText(text)

    def set_stats(
        self,
        courses: int,
        assignments: int,
        files: int,
        storage: str,
        last_backup: str,
    ) -> None:
        self.values["courses"].setText(str(courses))
        self.values["assignments"].setText(str(assignments))
        self.values["files"].setText(str(files))
        self.values["storage"].setText(storage)
        self.values["last_backup"].setText(last_backup)
