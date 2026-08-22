from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


def page_heading(eyebrow: str, title: str, subtitle: str) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)

    eyebrow_label = QLabel(eyebrow.upper())
    eyebrow_label.setObjectName("Eyebrow")
    title_label = QLabel(title)
    title_label.setObjectName("PageTitle")
    subtitle_label = QLabel(subtitle)
    subtitle_label.setObjectName("Muted")
    subtitle_label.setWordWrap(True)

    layout.addWidget(eyebrow_label)
    layout.addWidget(title_label)
    layout.addWidget(subtitle_label)
    return widget


class StatCard(QFrame):
    def __init__(self, label: str, value: str = "—", detail: str = "") -> None:
        super().__init__()
        self.setObjectName("Card")
        self.setMinimumHeight(125)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        label_widget = QLabel(label.upper())
        label_widget.setObjectName("Eyebrow")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("Metric")
        self.detail_label = QLabel(detail)
        self.detail_label.setObjectName("Muted")
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignBottom)

        layout.addWidget(label_widget)
        layout.addWidget(self.value_label)
        layout.addStretch()
        layout.addWidget(self.detail_label)

    def set_value(self, value: str, detail: str | None = None) -> None:
        self.value_label.setText(value)
        if detail is not None:
            self.detail_label.setText(detail)
