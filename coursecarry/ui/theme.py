from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication


def configure_app_font(app: QApplication) -> None:
    """Load the normal Windows UI font explicitly for packaged/offscreen Qt."""

    windows_root = Path(os.environ.get("WINDIR", "C:/Windows"))
    font_path = windows_root / "Fonts" / "segoeui.ttf"
    if font_path.is_file():
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            app.setFont(QFont(families[0], 10))


APP_STYLESHEET = r"""
QWidget {
    color: #e8e9ed;
    font-family: "Segoe UI Variable", "Segoe UI";
    font-size: 14px;
}
QMainWindow, QDialog {
    background: #0b0d10;
}
QFrame#Sidebar {
    background: #0f1216;
    border-right: 1px solid #272c33;
}
QFrame#TopBar {
    background: #0b0d10;
    border-bottom: 1px solid #232830;
}
QLabel#Brand {
    font-size: 22px;
    font-weight: 650;
    letter-spacing: 1px;
}
QLabel#Version, QLabel#Muted, QLabel#Eyebrow, QLabel#PageContext {
    color: #aab2bd;
}
QLabel#Version {
    font-size: 11px;
}
QLabel#Eyebrow {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
}
QLabel#PageContext {
    font-size: 13px;
    font-weight: 600;
}
QLabel#PageTitle {
    font-size: 28px;
    font-weight: 650;
}
QLabel#SectionTitle {
    font-size: 18px;
    font-weight: 650;
}
QLabel#Metric {
    font-size: 28px;
    font-weight: 650;
}
QLabel#SummaryValue {
    font-size: 22px;
    font-weight: 650;
}
QLabel#SelectionCount {
    color: #dce4ea;
    font-weight: 650;
}
QLabel#Unavailable {
    color: #f2c58d;
}
QLabel#EmptyState {
    color: #b5bec8;
    background: #101419;
    border: 1px solid #303741;
    border-radius: 12px;
    padding: 28px;
}
QLabel#StatusConnected {
    color: #a9f0cf;
    background: #13251f;
    border: 1px solid #275c49;
    border-radius: 13px;
    padding: 5px 11px;
}
QLabel#StatusUnknown {
    color: #c6cbd2;
    background: #171b20;
    border: 1px solid #353b44;
    border-radius: 13px;
    padding: 5px 11px;
}
QFrame#Card, QFrame#CourseCard, QFrame#Panel {
    background: #13171c;
    border: 1px solid #292f37;
    border-radius: 12px;
}
QFrame#Card:hover, QFrame#CourseCard:hover {
    border-color: #505d69;
    background: #151a20;
}
QPushButton {
    background: #181d23;
    border: 1px solid #353c46;
    border-radius: 8px;
    padding: 9px 15px;
    font-weight: 600;
}
QPushButton:hover {
    background: #222932;
    border-color: #65717e;
}
QPushButton:pressed {
    background: #111419;
}
QPushButton:focus {
    border-color: #a8ddc6;
}
QPushButton:disabled {
    color: #626a74;
    background: #111419;
    border-color: #242931;
}
QPushButton#Primary {
    color: #08110e;
    background: #bfe8d6;
    border-color: #d8f5e8;
    padding: 11px 20px;
}
QPushButton#Primary:hover {
    background: #d0f1e3;
}
QPushButton#Danger {
    color: #ffc8c8;
    border-color: #693f44;
}
QPushButton#Danger:disabled {
    color: #626a74;
    background: #111419;
    border-color: #242931;
}
QPushButton#NavButton {
    color: #9da5af;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 10px 13px;
    text-align: left;
    font-weight: 550;
}
QPushButton#NavButton:hover {
    color: #f2f4f6;
    background: #171b20;
}
QPushButton#NavButton:checked {
    color: #f2f4f6;
    background: #1b2127;
    border-color: #343c45;
}
QLineEdit, QComboBox, QSpinBox, QListWidget, QPlainTextEdit {
    background: #101419;
    border: 1px solid #303741;
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: #365849;
    placeholder-text-color: #9fa8b3;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QListWidget:focus {
    border-color: #718176;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QCheckBox, QRadioButton {
    spacing: 9px;
    padding: 4px;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 17px;
    height: 17px;
}
QProgressBar {
    color: transparent;
    background: #20252c;
    border: none;
    border-radius: 4px;
    max-height: 8px;
}
QProgressBar::chunk {
    background: #a8ddc6;
    border-radius: 4px;
}
QScrollArea {
    background: transparent;
    border: none;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #343b44;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QToolTip {
    color: #e8e9ed;
    background: #1b2026;
    border: 1px solid #424a54;
    padding: 6px;
}
"""
