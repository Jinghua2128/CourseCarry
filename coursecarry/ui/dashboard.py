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

from .components import StatCard, page_heading


class DashboardPage(QWidget):
    scan_requested = Signal()
    backup_requested = Signal()
    archive_requested = Signal()
    activity_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(34, 28, 34, 30)
        root.setSpacing(24)
        root.addWidget(
            page_heading(
                "Overview",
                "Your archive, at a glance",
                "Back up the course content your own account can already access.",
            )
        )

        cards = QGridLayout()
        cards.setHorizontalSpacing(14)
        cards.setVerticalSpacing(14)
        self.course_card = StatCard("Courses", "0", "detected")
        self.assignment_card = StatCard("Assignments", "0", "indexed")
        self.file_card = StatCard("Files", "0", "completed")
        self.storage_card = StatCard("Storage", "0 B", "archive size")
        self.last_backup_card = StatCard("Last backup", "Never", "local only")
        for index, card in enumerate(
            [
                self.course_card,
                self.assignment_card,
                self.file_card,
                self.storage_card,
                self.last_backup_card,
            ]
        ):
            cards.addWidget(card, index // 3, index % 3)
        cards.setColumnStretch(0, 1)
        cards.setColumnStretch(1, 1)
        cards.setColumnStretch(2, 1)
        root.addLayout(cards)

        action_panel = QFrame()
        action_panel.setObjectName("Panel")
        action_layout = QHBoxLayout(action_panel)
        action_layout.setContentsMargins(22, 20, 22, 20)
        copy = QVBoxLayout()
        title = QLabel("Ready when you are")
        title.setObjectName("SectionTitle")
        detail = QLabel("Chrome opens for normal school login. CourseCarry never asks for your password.")
        detail.setObjectName("Muted")
        detail.setWordWrap(True)
        copy.addWidget(title)
        copy.addWidget(detail)
        action_layout.addLayout(copy, 1)

        start = QPushButton("Start Backup")
        start.setObjectName("Primary")
        start.clicked.connect(self.backup_requested)
        action_layout.addWidget(start)
        root.addWidget(action_panel)

        secondary = QHBoxLayout()
        for text, signal in (
            ("Scan Courses", self.scan_requested),
            ("Open Archive", self.archive_requested),
            ("View Activity", self.activity_requested),
        ):
            button = QPushButton(text)
            button.clicked.connect(signal)
            secondary.addWidget(button)
        secondary.addStretch()
        root.addLayout(secondary)
        root.addStretch()

    def set_stats(
        self,
        courses: int,
        assignments: int,
        files: int,
        storage: str,
        last_backup: str,
    ) -> None:
        self.course_card.set_value(str(courses), "detected")
        self.assignment_card.set_value(str(assignments), "with metadata")
        self.file_card.set_value(str(files), "archived")
        self.storage_card.set_value(storage, "archive size")
        self.last_backup_card.set_value(last_backup, "local backup")
