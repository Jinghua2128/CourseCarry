# Authorized Cross-Institution Brightspace Test

Use this checklist only with the tester's own account and content they are already authorized to access. Do not send credentials, MFA codes, cookies, browser profiles, private URLs, course names, student names, or submitted files to the developer.

## Before the test

- Record the institution name, public portal URL, Brightspace LMS origin, Windows version, Chrome version, and CourseCarry version.
- Confirm the institution permits the intended personal backup activity.
- In Settings, choose **Custom Brightspace (untested)**, enter the institution name, the HTTPS portal URL, and the exact HTTPS Brightspace origin.
- Use a fresh CourseCarry data directory or Windows test account. Never copy another person's `browser-data`, `data`, `logs`, `config.json`, or archive.
- Keep one small, non-sensitive personal assignment submission available for the download check.

## Login and course scan

- Start CourseCarry and confirm it does not open Chrome or scan automatically.
- Confirm the saved list and **Never scanned** or the prior last-scan time appear immediately.
- Select **Scan for Updates** and complete the institution's normal SSO and MFA in managed Chrome.
- Confirm CourseCarry never displays a password field and never asks the tester to paste a token or cookie.
- Confirm My Courses opens. Record counts only for expected current and archived courses.
- Exercise every visible **View All**, archived/past-course, **Load More**, or course-pagination control.
- Confirm CourseCarry's found count increases without duplicate cards.
- Cancel one test scan and confirm cancellation returns promptly, Chrome closes, CourseCarry stays open, and the previous cache remains unchanged.
- Complete a scan and confirm Chrome closes, CourseCarry stays open, the last-scan time updates, and current/archived filters match the portal.
- If an expected course is missing, stop and file a redacted compatibility report; do not claim support.

## Personal submission backup

- Select only the prepared test course and choose **Download Selected Courses**.
- Complete normal login again only if the persistent session requires it.
- Confirm only the tester's own assignment submission history is requested.
- Confirm the supported file and metadata are stored beneath the chosen archive directory.
- Confirm the result distinguishes downloaded, skipped, updated, failed, and incomplete items.
- Run the same backup again without changing the LMS file. Confirm zero files are downloaded and the existing file is reported as skipped without a new folder or filename suffix.
- Cancel one operation and confirm Chrome and Playwright processes close while CourseCarry remains usable.

## Privacy review and support decision

- Close CourseCarry, then confirm no managed Chrome or Playwright child process remains.
- Review only redacted diagnostics. Confirm logs contain no credentials, cookies, tokens, complete private URLs, absolute personal paths, course names, student names, or file contents before sharing them.
- Report institution, hostnames, anonymous course counts, result categories, version, and a redacted error using `docs/compatibility-report.md`.
- Mark an institution supported only after login, current and archived discovery, one authorized personal-submission download, repeat-skip behavior, cancellation, and browser cleanup all pass on a clean device.

ITE has not passed this checklist and is not currently supported.
