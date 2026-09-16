from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..config import AppConfig, validate_provider_url
from .components import page_heading


class SettingsPage(QWidget):
    save_requested = Signal()
    open_logs_requested = Signal()

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(34, 28, 34, 30)
        root.setSpacing(18)
        root.addWidget(
            page_heading(
                "Preferences",
                "Settings",
                "Paths and download controls stay on this computer.",
            )
        )

        panel = QFrame()
        panel.setObjectName("Panel")
        form = QFormLayout(panel)
        form.setContentsMargins(22, 20, 22, 20)
        form.setHorizontalSpacing(24)
        form.setVerticalSpacing(14)

        self.provider = QComboBox()
        self.provider.addItem("Ngee Ann Polytechnic (tested)", "np_brightspace")
        self.provider.addItem("Custom Brightspace (untested)", "custom_brightspace")
        provider_index = self.provider.findData(config.provider_id)
        self.provider.setCurrentIndex(max(provider_index, 0))
        form.addRow("Institution preset", self.provider)

        self.institution = QLineEdit(config.institution_name)
        self.institution.setPlaceholderText("Institution name")
        form.addRow("Institution name", self.institution)

        self.portal_url = QLineEdit(config.base_url)
        self.portal_url.setPlaceholderText("https://portal.example.edu/")
        form.addRow("Portal URL", self.portal_url)

        self.lms_url = QLineEdit(config.lms_base_url)
        self.lms_url.setPlaceholderText("https://lms.example.edu")
        form.addRow("Brightspace URL", self.lms_url)

        archive_row = QWidget()
        archive_layout = QHBoxLayout(archive_row)
        archive_layout.setContentsMargins(0, 0, 0, 0)
        self.archive = QLineEdit(str(config.archive_path))
        browse_archive = QPushButton("Browse")
        browse_archive.clicked.connect(self._browse_archive)
        archive_layout.addWidget(self.archive, 1)
        archive_layout.addWidget(browse_archive)
        form.addRow("Archive location", archive_row)

        chrome_row = QWidget()
        chrome_layout = QHBoxLayout(chrome_row)
        chrome_layout.setContentsMargins(0, 0, 0, 0)
        self.chrome = QLineEdit(config.chrome_executable)
        self.chrome.setPlaceholderText("Auto Detect")
        browse_chrome = QPushButton("Browse")
        browse_chrome.clicked.connect(self._browse_chrome)
        chrome_layout.addWidget(self.chrome, 1)
        chrome_layout.addWidget(browse_chrome)
        form.addRow("Chrome executable", chrome_row)

        self.profile = QLabel("Managed by CourseCarry")
        self.profile.setObjectName("Muted")
        self.profile.setToolTip(str(config.browser_profile_path))
        form.addRow("Browser profile", self.profile)

        self.concurrent = QSpinBox()
        self.concurrent.setRange(1, 1)
        self.concurrent.setValue(1)
        self.concurrent.setToolTip("Kept at one to avoid aggressive LMS traffic.")
        form.addRow("Concurrent downloads", self.concurrent)

        self.chunk = QSpinBox()
        self.chunk.setRange(1, 16)
        self.chunk.setSuffix(" MB")
        self.chunk.setValue(config.chunk_size_mb)
        form.addRow("Chunk size", self.chunk)

        self.theme = QComboBox()
        self.theme.addItems(["Dark"])
        form.addRow("Theme", self.theme)
        self.animations = QCheckBox("Use subtle interface animations")
        self.animations.setChecked(config.animations)
        form.addRow("Animations", self.animations)
        self.provider.currentIndexChanged.connect(self._provider_changed)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(panel)
        root.addWidget(scroll, 1)

        privacy = QLabel(
            "CourseCarry is an unofficial, independent student project. It never asks for your school "
            "password. The managed browser profile may contain an authenticated session; do not share it."
        )
        privacy.setObjectName("Muted")
        privacy.setWordWrap(True)
        root.addWidget(privacy)

        actions = QHBoxLayout()
        open_logs = QPushButton("Open Logs")
        open_logs.clicked.connect(self.open_logs_requested)
        save = QPushButton("Save Settings")
        save.setObjectName("Primary")
        save.clicked.connect(self.save_requested)
        actions.addWidget(open_logs)
        actions.addStretch()
        actions.addWidget(save)
        root.addLayout(actions)

    def apply_to(self, config: AppConfig) -> None:
        config.provider_id = str(self.provider.currentData())
        config.institution_name = self.institution.text().strip() or "Custom institution"
        config.base_url = validate_provider_url(self.portal_url.text(), "Portal URL")
        config.lms_base_url = validate_provider_url(
            self.lms_url.text(), "Brightspace URL"
        ).rstrip("/")
        config.archive_dir = self.archive.text().strip()
        config.chrome_executable = self.chrome.text().strip()
        config.chunk_size_mb = self.chunk.value()
        config.animations = self.animations.isChecked()

    def _provider_changed(self) -> None:
        if self.provider.currentData() == "np_brightspace":
            self.institution.setText("Ngee Ann Polytechnic")
            self.portal_url.setText("https://politemall.polite.edu.sg/")
            self.lms_url.setText("https://nplms.polite.edu.sg")

    def _browse_archive(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Choose archive location", self.archive.text())
        if selected:
            self.archive.setText(selected)

    def _browse_chrome(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Google Chrome executable",
            self.chrome.text(),
            "Applications (*.exe);;All files (*)",
        )
        if selected:
            self.chrome.setText(selected)
