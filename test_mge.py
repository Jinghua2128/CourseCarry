"""Manual one-course integration helper retained without private course IDs.

Example: ``python test_mge.py --course-id 123456``
"""

from __future__ import annotations

import argparse
import json

from playwright.sync_api import sync_playwright

from assignment_scanner import scan_assignments
from politeload.config import ConfigStore
from submission_downloader import download_submission_files, scan_submission


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manually test one detected course")
    parser.add_argument("--course-id", type=int, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = ConfigStore().load()
    data = json.loads(config.courses_path.read_text(encoding="utf-8"))
    course = next(
        (item for item in data.get("courses", []) if int(item["id"]) == args.course_id),
        None,
    )
    if course is None:
        print("That course ID was not found in the local course cache.")
        return 1

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(config.browser_profile_path),
            channel="chrome",
            headless=False,
            no_viewport=True,
        )
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(config.base_url, wait_until="commit", timeout=60_000)
            input("Complete the normal browser login, then press Enter…")
            assignments = scan_assignments(page, course)
            for index, assignment in enumerate(assignments, start=1):
                print(f"[{index}] {assignment['name']}")
            choice = int(input("Assignment number: ")) - 1
            assignment = assignments[choice]
            files = scan_submission(page, assignment)
            downloaded = download_submission_files(
                page, course, assignment, files, config.archive_path
            )
            print(f"Downloaded {len(downloaded)} file(s).")
        finally:
            context.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
