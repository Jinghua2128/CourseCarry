# Changelog

## Unreleased

- Renamed the public application and Windows build to CourseCarry.
- Added prominent unofficial-project, local-data, institutional-policy, and redistribution disclaimers.
- Renamed the Python package, local data paths, database, logs, and Windows executable consistently.

## 0.5.0-alpha — 2026-08-21

- Added the PySide6 desktop application with Dashboard, Courses, Backup, Activity, Settings, and first-run onboarding.
- Moved browser and LMS behavior behind an initial `NPBrightspaceProvider` abstraction.
- Added background scan and backup workers so Playwright and downloads do not block the UI thread.
- Added authenticated streaming downloads with 1 MB chunks, `.part` files, retry handling, final-size verification, and duplicate/update states.
- Added semester-based archive paths, assignment metadata, structured local logging, and an incremental SQLite backup index.
- Added Windows `onedir` PyInstaller packaging, public-release documentation, privacy exclusions, and offline unit tests.
- Hardened authenticated downloads with exact HTTPS-origin validation, preserved cookie transport flags, manually validated redirects, and origin-only Referers.
- Added collision-proof archive identities, bounded Windows path components, fingerprint-only source metadata, safer diagnostics, and SQLite sidecar exclusions.
- Fixed first-login course discovery by opening the portal's My Courses entry and accepting course cards from the exact trusted Brightspace origin.
- Course scans now accumulate current and archived cards across My Courses, View All, Archived, and lazy-loaded views before completing.

## Earlier prototypes

- Validated user-controlled Microsoft / school SSO, course-card detection, assignment history scanning, and personal submission downloads against an NP POLITEMall account.
