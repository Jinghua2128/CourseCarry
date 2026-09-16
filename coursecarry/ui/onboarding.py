from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class OnboardingDialog(QDialog):
    def __init__(self, archive_path: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Welcome to CourseCarry")
        self.setModal(True)
        self.setMinimumSize(620, 430)
        root = QVBoxLayout(self)
        root.setContentsMargins(38, 34, 38, 30)

        self.step = QLabel("WELCOME")
        self.step.setObjectName("Eyebrow")
        root.addWidget(self.step)
        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        self.archive = QLineEdit(archive_path)
        self._add_page(
            "Personal backups, kept personal",
            "CourseCarry creates an offline archive of course content your student account can already access.\n\n"
            "It is an unofficial, independent student project and is not affiliated with or endorsed by "
            "your institution or D2L. It does not store or ask for your school password.",
        )
        location = self._page_shell(
            "Choose your archive location",
            "Downloads and metadata will be organized by semester, course, and assignment.",
        )
        row = QHBoxLayout()
        row.addWidget(self.archive, 1)
        browse = QPushButton("Browse")
        browse.clicked.connect(self._browse)
        row.addWidget(browse)
        location.layout().addLayout(row)
        self.stack.addWidget(location)
        self._add_page(
            "Login stays in Chrome",
            "When you scan or back up, CourseCarry opens a managed Chrome window. Complete the normal "
            "Microsoft / school SSO flow and MFA there.\n\nNever enter those credentials into CourseCarry.",
        )
        self._add_page(
            "Ready to scan",
            "Use Scan Courses after setup. CourseCarry will only report a connected session after it "
            "actually detects your course page.",
        )

        controls = QHBoxLayout()
        self.back = QPushButton("Back")
        self.back.setDisabled(True)
        self.back.clicked.connect(self._previous)
        self.next = QPushButton("Continue")
        self.next.setObjectName("Primary")
        self.next.clicked.connect(self._next)
        controls.addWidget(self.back)
        controls.addStretch()
        controls.addWidget(self.next)
        root.addLayout(controls)

    def _page_shell(self, title: str, body: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 18, 0, 0)
        layout.setSpacing(14)
        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")
        title_label.setWordWrap(True)
        body_label = QLabel(body)
        body_label.setObjectName("Muted")
        body_label.setWordWrap(True)
        body_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(title_label)
        layout.addWidget(body_label)
        layout.addStretch()
        return page

    def _add_page(self, title: str, body: str) -> None:
        self.stack.addWidget(self._page_shell(title, body))

    def _next(self) -> None:
        if self.stack.currentIndex() == self.stack.count() - 1:
            self.accept()
            return
        self.stack.setCurrentIndex(self.stack.currentIndex() + 1)
        self._sync_controls()

    def _previous(self) -> None:
        self.stack.setCurrentIndex(max(0, self.stack.currentIndex() - 1))
        self._sync_controls()

    def _sync_controls(self) -> None:
        index = self.stack.currentIndex()
        labels = ["WELCOME", "STEP 1 · ARCHIVE", "STEP 2 · LOGIN", "STEP 3 · READY"]
        self.step.setText(labels[index])
        self.back.setDisabled(index == 0)
        self.next.setText("Finish" if index == self.stack.count() - 1 else "Continue")

    def _browse(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Choose archive location", self.archive.text())
        if selected:
            self.archive.setText(selected)
