"""Compatibility entry point for launching the CourseCarry desktop app."""

from __future__ import annotations

import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


def _bundle_self_test() -> int:
    """Verify the two native subsystems required by the portable build."""

    from PySide6.QtGui import QGuiApplication  # noqa: F401
    from playwright.sync_api import sync_playwright

    playwright = sync_playwright().start()
    try:
        if playwright.chromium.name != "chromium":
            return 1
    finally:
        playwright.stop()
    return 0


def _is_qt_dll_error(error: BaseException) -> bool:
    message = str(error).lower()
    return "qt" in message and ("dll load failed" in message or "winerror 127" in message)


def _diagnostic_directory() -> Path:
    override = os.environ.get("COURSECARRY_DATA_DIR")
    if override:
        return Path(override).expanduser()

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "CourseCarry"
    return Path.home() / "AppData" / "Local" / "CourseCarry"


def _safe_error_text(error: BaseException) -> str:
    text = f"{type(error).__name__}: {error}".replace("\r", " ").replace("\n", " ")
    replacements = {
        str(Path.home()): "%USERPROFILE%",
        os.environ.get("LOCALAPPDATA", ""): "%LOCALAPPDATA%",
    }
    for private_value, label in replacements.items():
        if private_value:
            text = text.replace(private_value, label)
    return text[:1000]


def _native_probe_lines(bundle_root: Path) -> list[str]:
    """Load startup DLLs one by one without requiring Qt or third-party tools."""

    if os.name != "nt":
        return ["Native probes: skipped (not Windows)"]

    import ctypes

    lines = ["Native probes:"]
    handles: list[object] = []
    dll_directory = None
    try:
        if hasattr(os, "add_dll_directory"):
            dll_directory = os.add_dll_directory(str(bundle_root))

        for relative_name in (
            "MSVCP140.dll",
            "MSVCP140_1.dll",
            "MSVCP140_2.dll",
            "VCRUNTIME140.dll",
            "VCRUNTIME140_1.dll",
            "python311.dll",
            "qt6core.dll",
            "qt6gui.dll",
            r"PySide6\QtGui.pyd",
            r"PySide6\qt-plugins\platforms\qwindows.dll",
        ):
            candidate = bundle_root / relative_name
            if not candidate.is_file():
                lines.append(f"- {relative_name}: missing")
                continue
            try:
                handles.append(ctypes.WinDLL(str(candidate)))
                lines.append(f"- {relative_name}: loaded")
            except OSError as probe_error:
                winerror = getattr(probe_error, "winerror", None)
                detail = f"WinError {winerror}" if winerror is not None else type(probe_error).__name__
                lines.append(f"- {relative_name}: failed ({detail})")
    finally:
        if dll_directory is not None:
            dll_directory.close()
        # Keep successful DLL handles alive until every dependent probe has run.
        handles.clear()
    return lines


def _write_startup_diagnostic(error: BaseException) -> Path | None:
    """Write a small privacy-safe report before Qt is available."""

    try:
        from coursecarry.version import __version__
    except Exception:
        __version__ = "unknown"

    try:
        directory = _diagnostic_directory()
        directory.mkdir(parents=True, exist_ok=True)
        report_path = directory / "startup-diagnostic.txt"
        bundle_root = Path(sys.executable).resolve().parent

        if os.name == "nt" and hasattr(sys, "getwindowsversion"):
            windows = sys.getwindowsversion()
            os_detail = f"Windows {windows.major}.{windows.minor}.{windows.build}"
        else:
            os_detail = platform.platform()

        lines = [
            "CourseCarry startup diagnostic",
            f"Created UTC: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
            f"CourseCarry: {__version__}",
            f"Python: {platform.python_version()}",
            f"OS: {os_detail}",
            f"Architecture: {platform.machine() or 'unknown'}",
            f"Frozen: {bool(getattr(sys, 'frozen', False) or '__compiled__' in globals())}",
            f"Failure: {_safe_error_text(error)}",
            "",
            *_native_probe_lines(bundle_root),
            "",
            "This report intentionally excludes usernames, course data, browser data, and credentials.",
        ]
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return report_path
    except Exception:
        return None


def _show_qt_runtime_error(report_path: Path | None) -> None:
    """Show recovery and reporting steps even when Qt cannot be imported."""

    report_message = (
        f"\n\nA startup report was saved to:\n{report_path}\n\n"
        "Please send startup-diagnostic.txt with the error report. It contains no course data or credentials."
        if report_path is not None
        else "\n\nCourseCarry could not create its startup report."
    )
    message = (
        "CourseCarry could not load its Windows interface runtime.\n\n"
        "1. Delete the previously extracted CourseCarry folder.\n"
        "2. Extract the newest ZIP into a new, empty folder.\n"
        "3. Keep every extracted file and folder together.\n\n"
        "CourseCarry requires 64-bit Windows 10 version 1809 or newer, "
        "or 64-bit Windows 11."
        f"{report_message}"
    )
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, message, "CourseCarry could not start", 0x10)
    except Exception:
        pass


def _run() -> int:
    is_self_test = "--bundle-self-test" in sys.argv
    try:
        if is_self_test:
            return _bundle_self_test()

        from coursecarry.app import main

        return main()
    except (ImportError, OSError) as error:
        if not _is_qt_dll_error(error):
            raise
        report_path = _write_startup_diagnostic(error)
        if not is_self_test:
            _show_qt_runtime_error(report_path)
        return 1


if __name__ == "__main__":
    raise SystemExit(_run())
