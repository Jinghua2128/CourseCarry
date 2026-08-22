from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget

from .components import page_heading


class ActivityPage(QWidget):
    open_logs_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(34, 28, 34, 30)
        root.setSpacing(18)
        root.addWidget(
            page_heading(
                "History",
                "Activity",
                "Live events from this session. Detailed local logs exclude credentials and cookies.",
            )
        )
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Backup and scan activity will appear here.")
        root.addWidget(self.output, 1)
        actions = QHBoxLayout()
        actions.addStretch()
        open_logs = QPushButton("Open Logs")
        open_logs.clicked.connect(self.open_logs_requested)
        actions.addWidget(open_logs)
        root.addLayout(actions)

    def add(self, level: str, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output.appendPlainText(f"{timestamp}  {level.upper():<7}  {message}")
