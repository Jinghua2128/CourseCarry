from __future__ import annotations

import logging
import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

import requests
from playwright.sync_api import Page

from ..models import BackupFile, DownloadStatus
from ..utils.url_security import (
    origin_url,
    require_same_https_origin,
    source_fingerprint,
)


LOGGER = logging.getLogger(__name__)
ProgressCallback = Callable[[int, int | None], None]
CancelCallback = Callable[[], bool]


@dataclass(slots=True)
class DownloadResult:
    status: DownloadStatus
    size: int = 0
    expected_size: int | None = None
    error: str = ""


def should_skip_existing(
    destination: Path,
    expected_size: int | None,
    current_source_fingerprint: str,
    previous_source_fingerprint: str | None,
) -> bool:
    return bool(
        destination.is_file()
        and expected_size is not None
        and destination.stat().st_size == expected_size
        and previous_source_fingerprint == current_source_fingerprint
    )


class AuthenticatedDownloader:
    """Stream files with browser-authenticated cookies and atomic completion."""

    def __init__(
        self,
        allowed_origin: str,
        chunk_size: int = 1024 * 1024,
        retries: int = 3,
        max_redirects: int = 5,
    ) -> None:
        require_same_https_origin(origin_url(allowed_origin), allowed_origin)
        self.allowed_origin = origin_url(allowed_origin)
        self.chunk_size = chunk_size
        self.retries = retries
        self.max_redirects = max_redirects
        self.session = requests.Session()

    def close(self) -> None:
        self.session.close()

    def refresh_from_page(self, page: Page) -> None:
        require_same_https_origin(page.url, self.allowed_origin)
        self.session.cookies.clear()
        for cookie in page.context.cookies([page.url]):
            expires = cookie.get("expires")
            self.session.cookies.set(
                cookie["name"],
                cookie["value"],
                domain=cookie.get("domain"),
                path=cookie.get("path", "/"),
                secure=bool(cookie.get("secure", True)),
                expires=int(expires) if isinstance(expires, (int, float)) and expires > 0 else None,
                rest={
                    "HttpOnly": bool(cookie.get("httpOnly", False)),
                    "SameSite": cookie.get("sameSite", "Lax"),
                },
            )
        self.session.headers.update(
            {
                "User-Agent": page.evaluate("() => navigator.userAgent"),
                "Referer": self.allowed_origin,
                "Accept-Encoding": "identity",
            }
        )

    def _get_same_origin(self, url: str) -> requests.Response:
        current_url = require_same_https_origin(url, self.allowed_origin)
        for redirect_index in range(self.max_redirects + 1):
            response = self.session.get(
                current_url,
                stream=True,
                timeout=(30, 120),
                allow_redirects=False,
            )
            if response.status_code not in {301, 302, 303, 307, 308}:
                return response

            location = response.headers.get("Location")
            response.close()
            if not location:
                raise requests.RequestException("The LMS returned an invalid redirect.")
            if redirect_index >= self.max_redirects:
                raise requests.TooManyRedirects("The LMS redirect limit was exceeded.")
            current_url = require_same_https_origin(
                urljoin(current_url, location),
                self.allowed_origin,
            )

        raise requests.TooManyRedirects("The LMS redirect limit was exceeded.")

    def download(
        self,
        item: BackupFile,
        destination: Path,
        previous_source_fingerprint: str | None,
        on_progress: ProgressCallback,
        cancelled: CancelCallback,
    ) -> DownloadResult:
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            LOGGER.error("Could not create a download destination")
            return DownloadResult(
                DownloadStatus.FAILED,
                error="Could not create the destination folder.",
            )
        part_path = destination.with_name(f"{destination.name}.part")
        had_existing = destination.exists()
        current_source_fingerprint = item.stable_id or source_fingerprint(item.source_url)

        for attempt in range(1, self.retries + 1):
            if cancelled():
                return DownloadResult(DownloadStatus.INCOMPLETE, error="Cancelled")
            try:
                with self._get_same_origin(item.source_url) as response:
                    if response.status_code != 200:
                        if response.status_code in {429, 500, 502, 503, 504} and attempt < self.retries:
                            time.sleep(min(2**attempt, 4))
                            continue
                        return DownloadResult(
                            DownloadStatus.FAILED,
                            error=f"HTTP {response.status_code}",
                        )

                    content_type = response.headers.get("Content-Type", "").lower()
                    if "text/html" in content_type and destination.suffix.lower() not in {".html", ".htm"}:
                        return DownloadResult(
                            DownloadStatus.FAILED,
                            error="The server returned HTML; the login session may have expired.",
                        )

                    length_value = response.headers.get("Content-Length")
                    expected_size = int(length_value) if length_value and length_value.isdigit() else None
                    if should_skip_existing(
                        destination,
                        expected_size,
                        current_source_fingerprint,
                        previous_source_fingerprint,
                    ):
                        LOGGER.info("A verified file already exists")
                        return DownloadResult(
                            DownloadStatus.SKIPPED,
                            size=destination.stat().st_size,
                            expected_size=expected_size,
                        )

                    downloaded = 0
                    with part_path.open("wb") as output:
                        for chunk in response.iter_content(chunk_size=self.chunk_size):
                            if cancelled():
                                return DownloadResult(
                                    DownloadStatus.INCOMPLETE,
                                    size=downloaded,
                                    expected_size=expected_size,
                                    error="Cancelled",
                                )
                            if not chunk:
                                continue
                            output.write(chunk)
                            downloaded += len(chunk)
                            on_progress(downloaded, expected_size)

                    if expected_size is not None and downloaded != expected_size:
                        return DownloadResult(
                            DownloadStatus.INCOMPLETE,
                            size=downloaded,
                            expected_size=expected_size,
                            error="Downloaded size did not match the server metadata.",
                        )

                    os.replace(part_path, destination)
                    status = DownloadStatus.UPDATED if had_existing else DownloadStatus.DOWNLOADED
                    LOGGER.info("Download complete")
                    return DownloadResult(status, downloaded, expected_size)
            except (requests.RequestException, ValueError) as error:
                if attempt < self.retries:
                    time.sleep(min(2**attempt, 4))
                    continue
                LOGGER.error("Download request failed: %s", type(error).__name__)
                return DownloadResult(
                    DownloadStatus.FAILED,
                    error="The secure LMS download request failed.",
                )
            except OSError as error:
                LOGGER.error("File write failed: %s", type(error).__name__)
                return DownloadResult(
                    DownloadStatus.FAILED,
                    error="Could not write the destination file.",
                )

        return DownloadResult(DownloadStatus.FAILED, error="Retry limit reached")
