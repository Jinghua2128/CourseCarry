"""Compatibility helpers for the original manual integration script."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import Page

from coursecarry.core.downloader import AuthenticatedDownloader
from coursecarry.models import BackupFile
from coursecarry.utils.filenames import assignment_archive_path, sanitize_filename
from coursecarry.utils.url_security import (
    is_same_https_origin,
    require_same_https_origin,
    source_fingerprint,
)


LMS_BASE = "https://nplms.polite.edu.sg"


def safe_filename(name: str) -> str:
    return sanitize_filename(name)


def scan_submission(page: Page, assignment: dict) -> list[dict[str, str]]:
    history_url = require_same_https_origin(assignment["history_url"], LMS_BASE)
    page.goto(history_url, wait_until="domcontentloaded", timeout=60_000)
    page.wait_for_timeout(1_500)
    require_same_https_origin(page.url, LMS_BASE)
    links = page.locator('a[href*="/d2l/common/viewFile.d2lfile/"]')
    files: list[dict[str, str]] = []
    seen: set[str] = set()
    for index in range(links.count()):
        link = links.nth(index)
        href = link.get_attribute("href") or ""
        full_url = urljoin(LMS_BASE, href)
        if not href or not is_same_https_origin(full_url, LMS_BASE) or full_url in seen:
            continue
        seen.add(full_url)
        files.append({"filename": link.inner_text().strip(), "url": full_url})
    return files


def download_submission_files(
    page: Page,
    course: dict,
    assignment: dict,
    files: list[dict[str, str]],
    archive_root: Path,
) -> list[dict[str, str]]:
    assignment_dir = assignment_archive_path(
        archive_root,
        course["id"],
        course.get("code", ""),
        course["name"],
        assignment["assignment_id"],
        assignment["name"],
    )
    output_dir = assignment_dir / "Submission"
    output_dir.mkdir(parents=True, exist_ok=True)
    downloader = AuthenticatedDownloader(LMS_BASE)
    downloader.refresh_from_page(page)
    records: list[dict[str, str]] = []
    try:
        for item in files:
            filename = sanitize_filename(item["filename"], "unknown_file")
            source_url = item["url"]
            result = downloader.download(
                BackupFile(filename, source_url),
                output_dir / filename,
                None,
                lambda downloaded, total: None,
                lambda: False,
            )
            records.append(
                {
                    "filename": filename,
                    "source_fingerprint": source_fingerprint(source_url),
                    "status": result.status.value,
                }
            )
    finally:
        downloader.close()

    safe_course = {
        key: value for key, value in course.items() if key not in {"href", "full_text"}
    }
    safe_assignment = {
        key: value for key, value in assignment.items() if key != "history_url"
    }
    if assignment.get("history_url"):
        safe_assignment["history_fingerprint"] = source_fingerprint(
            str(assignment["history_url"])
        )

    assignment_dir.mkdir(parents=True, exist_ok=True)
    (assignment_dir / "metadata.json").write_text(
        json.dumps(
            {
                "course": safe_course,
                "assignment": safe_assignment,
                "files": records,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return [record for record in records if record["status"] in {"downloaded", "updated"}]
