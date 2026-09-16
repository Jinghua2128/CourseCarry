# Changelog

## Unreleased

## 0.6.3-alpha — 2026-09-16

- Rebuilt the portable Windows runtime with Python 3.11 and PySide6/Qt 6.5.3 after the affected laptop still failed to import `QtGui` from the Qt 6.11 build.
- Removed Qt 6.11's direct D3D12 procedure imports from the startup dependency chain while preserving the extract-and-run requirement.
- Added automatic and standalone pre-Qt diagnostics that record the Windows build and test each bundled native dependency without collecting usernames, paths, course, browser, or credential data.
- Added build gates that reject the wrong Python minor version, Qt compatibility line, or bundled Python DLL.

## 0.6.2-alpha — 2026-09-03

- Replaced the PyInstaller release pipeline with a Nuitka standalone build using the PySide6 and Playwright deployment plugins.
- Bundled Python, Qt, Playwright's driver, and the required Visual C++ application runtime so release users install nothing.
- Stopped copying Windows 11 UCRT and API-forwarder DLLs into releases; supported laptops now use their own Windows system components.
- Added a packaged self-test that loads QtGui and starts and stops the Playwright driver without opening Chrome.
- Added release gates for the standalone runtime layout and for accidental host operating-system DLL inclusion.

## 0.6.1-alpha — 2026-09-02

- Fixed a clean-laptop startup failure where importing `QtGui` could resolve an incomplete or incompatible system Visual C++ runtime.
- Added the PySide6-matched MSVCP runtime DLLs to the application's primary `_internal` DLL directory.
- Added build and release gates that verify the Qt runtime files are present and identical to the bundled PySide6 copies.
- Added a pre-Qt startup message with fresh-extraction and supported-Windows guidance if a native Qt import still fails.
- Clarified that every release must be extracted into a new, empty folder rather than over an older build.

## 0.6.0-alpha — 2026-09-02

- Made course scanning fully user-controlled and load the saved course library immediately at startup.
- Added the last successful scan timestamp, once-per-session stale-cache choice, and always-visible scan controls.
- Changed scans to merge by stable LMS course ID, retain missing cached courses as unavailable after a complete scan, and prevent duplicate cards across current, archived, and paginated views.
- Added responsive scan cancellation and explicit browser-close results for success, failure, timeout, and cancellation.
- Moved selection, search, current/archived filters, Select All, Clear Selection, and the primary download action into the course library.
- Added configurable institution, portal, and Brightspace settings while keeping the NP preset clearly identified as the only tested provider.
- Stabilized repeated download filenames and skip decisions with query-independent LMS file identities.
- Expanded offline coverage for timestamps, cache loading, current/archived parsing, pagination, merging, unavailable courses, rescan deduplication, and rotating download URLs.
- Updated the architecture, clean-device checklist, cross-institution checklist, packaging validation, and release documentation.

## 0.5.1-alpha — 2026-08-28

- Renamed the public application and Windows build to CourseCarry.
- Added prominent unofficial-project, local-data, institutional-policy, and redistribution disclaimers.
- Renamed the Python package, local data paths, database, logs, and Windows executable consistently.
- Added a reproducible release packager with archive-content validation and SHA-256 checksums.
- Added a release-candidate checklist covering live sign-in, course scanning, submission backup, privacy, upgrade compatibility, and clean-machine smoke testing.

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
