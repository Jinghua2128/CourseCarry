from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from coursecarry.core.downloader import AuthenticatedDownloader, should_skip_existing
from coursecarry.models import BackupFile, DownloadStatus


class FakeResponse:
    def __init__(self, body: bytes, content_type: str = "application/octet-stream") -> None:
        self.body = body
        self.status_code = 200
        self.headers = {
            "Content-Length": str(len(body)),
            "Content-Type": content_type,
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def iter_content(self, chunk_size: int):
        for index in range(0, len(self.body), chunk_size):
            yield self.body[index : index + chunk_size]


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response

    def get(self, *args, **kwargs) -> FakeResponse:
        return self.response

    def close(self) -> None:
        pass


class DuplicateDetectionTests(TestCase):
    def test_skips_only_when_size_and_source_match(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "submission.bin"
            path.write_bytes(b"1234")
            source = "https://lms.example.invalid/file/1"
            self.assertTrue(should_skip_existing(path, 4, source, source))
            self.assertFalse(should_skip_existing(path, 5, source, source))
            self.assertFalse(
                should_skip_existing(path, 4, source, "https://lms.example.invalid/file/2")
            )

    def test_missing_expected_size_is_not_assumed_complete(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "submission.bin"
            path.write_bytes(b"1234")
            source = "https://lms.example.invalid/file/1"
            self.assertFalse(should_skip_existing(path, None, source, source))


class StreamingDownloadTests(TestCase):
    def test_streams_to_part_then_atomically_completes(self) -> None:
        with TemporaryDirectory() as directory:
            destination = Path(directory) / "video.bin"
            source = "https://lms.example.invalid/file/1"
            downloader = AuthenticatedDownloader(
                "https://lms.example.invalid", chunk_size=3
            )
            downloader.session = FakeSession(FakeResponse(b"abcdefgh"))
            progress: list[int] = []

            result = downloader.download(
                BackupFile("video.bin", source),
                destination,
                None,
                lambda downloaded, total: progress.append(downloaded),
                lambda: False,
            )

            self.assertEqual(result.status, DownloadStatus.DOWNLOADED)
            self.assertEqual(destination.read_bytes(), b"abcdefgh")
            self.assertFalse(destination.with_name("video.bin.part").exists())
            self.assertEqual(progress, [3, 6, 8])

    def test_cancellation_keeps_an_incomplete_part_file(self) -> None:
        with TemporaryDirectory() as directory:
            destination = Path(directory) / "video.bin"
            source = "https://lms.example.invalid/file/1"
            downloader = AuthenticatedDownloader(
                "https://lms.example.invalid", chunk_size=3
            )
            downloader.session = FakeSession(FakeResponse(b"abcdefgh"))
            cancelled = False

            def mark_cancelled(downloaded: int, total: int | None) -> None:
                nonlocal cancelled
                cancelled = True

            result = downloader.download(
                BackupFile("video.bin", source),
                destination,
                None,
                mark_cancelled,
                lambda: cancelled,
            )

            self.assertEqual(result.status, DownloadStatus.INCOMPLETE)
            self.assertFalse(destination.exists())
            self.assertEqual(destination.with_name("video.bin.part").read_bytes(), b"abc")
