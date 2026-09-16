from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main


class StartupDiagnosticTests(unittest.TestCase):
    def test_recognizes_qt_dll_load_failure(self) -> None:
        error = ImportError("DLL load failed while importing QtGui: The specified procedure could not be found")
        self.assertTrue(main._is_qt_dll_error(error))
        self.assertFalse(main._is_qt_dll_error(ImportError("No module named example")))

    def test_error_text_redacts_private_roots(self) -> None:
        local_app_data = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
        error = OSError(f"failed under {local_app_data} and {Path.home()}")
        text = main._safe_error_text(error)
        self.assertNotIn(str(Path.home()), text)
        self.assertNotIn(local_app_data, text)

    def test_report_is_written_without_qt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="coursecarry-startup-test-") as temp_dir:
            with (
                patch.dict(os.environ, {"COURSECARRY_DATA_DIR": temp_dir}),
                patch.object(main, "_native_probe_lines", return_value=["Native probes: test"]),
            ):
                report_path = main._write_startup_diagnostic(
                    ImportError("DLL load failed while importing QtGui: test")
                )

            self.assertEqual(report_path, Path(temp_dir) / "startup-diagnostic.txt")
            report = report_path.read_text(encoding="utf-8")
            self.assertIn("CourseCarry startup diagnostic", report)
            self.assertIn("Native probes: test", report)
            self.assertIn("excludes usernames, course data, browser data, and credentials", report)


if __name__ == "__main__":
    unittest.main()
