import logging
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from politeload.core.downloader import AuthenticatedDownloader
from politeload.models import BackupFile, DownloadStatus
from politeload.utils.filenames import MAX_FILENAME_UNITS, sanitize_filename
from politeload.utils.logging import SensitiveDataFilter, redact_sensitive
from politeload.utils.url_security import is_same_https_origin, source_fingerprint


class UrlSecurityTests(TestCase):
    def test_requires_the_exact_https_origin(self) -> None:
        origin = "https://lms.example.invalid"
        self.assertTrue(is_same_https_origin(f"{origin}/file?id=1", origin))
        self.assertFalse(is_same_https_origin("http://lms.example.invalid/file", origin))
        self.assertFalse(is_same_https_origin("https://cdn.example.invalid/file", origin))
        self.assertFalse(is_same_https_origin("https://user@lms.example.invalid/file", origin))

    def test_source_identity_is_non_reversible(self) -> None:
        source = "https://lms.example.invalid/file?token=private-value"
        fingerprint = source_fingerprint(source)
        self.assertRegex(fingerprint, re.compile(r"^[0-9a-f]{64}$"))
        self.assertNotIn("private-value", fingerprint)


class DiagnosticPrivacyTests(TestCase):
    def test_redacts_complete_headers_urls_and_paths(self) -> None:
        message = (
            "Authorization: Bearer top-secret\n"
            "GET https://lms.example.invalid/private?id=42&sig=secret "
            r"from D:\Users\Student\archive\file.pdf"
        )
        redacted = redact_sensitive(message)
        self.assertNotIn("top-secret", redacted)
        self.assertNotIn("sig=secret", redacted)
        self.assertNotIn("Student", redacted)
        self.assertIn("[REDACTED]", redacted)
        self.assertIn("[PRIVATE_URL]", redacted)
        self.assertIn("[LOCAL_PATH]", redacted)

    def test_filter_drops_exception_traceback_data(self) -> None:
        record = logging.LogRecord(
            "test", logging.ERROR, __file__, 1, "token=secret", (), None
        )
        record.exc_info = (ValueError, ValueError("private"), None)
        self.assertTrue(SensitiveDataFilter().filter(record))
        self.assertIsNone(record.exc_info)
        self.assertNotIn("secret", str(record.msg))


class FilesystemSafetyTests(TestCase):
    def test_long_names_are_bounded_and_collision_resistant(self) -> None:
        first = sanitize_filename("a" * 400 + ".pdf")
        second = sanitize_filename("a" * 399 + "b.pdf")
        self.assertLessEqual(len(first.encode("utf-16-le")) // 2, MAX_FILENAME_UNITS)
        self.assertNotEqual(first, second)
        self.assertTrue(first.endswith(".pdf"))

    def test_windows_control_characters_are_removed(self) -> None:
        self.assertEqual(sanitize_filename("report\x01final.pdf"), "report_final.pdf")
        self.assertEqual(sanitize_filename("CON.extra.txt"), "_CON.extra.txt")


class RedirectPolicyTests(TestCase):
    class RedirectResponse:
        status_code = 302
        headers = {"Location": "https://evil.example.invalid/file"}

        def close(self) -> None:
            pass

    class RedirectSession:
        def get(self, *args, **kwargs):
            return RedirectPolicyTests.RedirectResponse()

        def close(self) -> None:
            pass

    def test_cross_origin_redirect_is_rejected_before_writing(self) -> None:
        with TemporaryDirectory() as directory:
            downloader = AuthenticatedDownloader(
                "https://lms.example.invalid", retries=1
            )
            downloader.session = self.RedirectSession()
            result = downloader.download(
                BackupFile(
                    "submission.pdf",
                    "https://lms.example.invalid/file/1",
                ),
                Path(directory) / "submission.pdf",
                None,
                lambda downloaded, total: None,
                lambda: False,
            )
            self.assertEqual(result.status, DownloadStatus.FAILED)
            self.assertFalse((Path(directory) / "submission.pdf").exists())


class CookieTransferTests(TestCase):
    class Context:
        def cookies(self, urls):
            return [
                {
                    "name": "session",
                    "value": "private",
                    "domain": "lms.example.invalid",
                    "path": "/d2l",
                    "secure": True,
                    "httpOnly": True,
                    "sameSite": "Lax",
                    "expires": -1,
                }
            ]

    class Page:
        url = "https://lms.example.invalid/d2l/history"

        def __init__(self) -> None:
            self.context = CookieTransferTests.Context()

        def evaluate(self, script: str) -> str:
            return "PoliteLoad Test Browser"

    def test_secure_cookie_and_private_referer_boundary_are_preserved(self) -> None:
        downloader = AuthenticatedDownloader("https://lms.example.invalid")
        try:
            downloader.refresh_from_page(self.Page())
            cookie = next(iter(downloader.session.cookies))
            self.assertTrue(cookie.secure)
            self.assertEqual(cookie.path, "/d2l")
            self.assertEqual(
                downloader.session.headers["Referer"],
                "https://lms.example.invalid/",
            )
        finally:
            downloader.close()
