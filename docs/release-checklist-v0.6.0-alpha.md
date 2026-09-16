# CourseCarry v0.6.0-alpha Release Checklist

> [!WARNING]
> Superseded by v0.6.1-alpha. A real second-laptop test of this candidate failed while Windows imported `QtGui`; do not publish or share the v0.6.0-alpha ZIP.

Automated checks can be completed locally. Login, clean-device, and cross-institution checks require an authorized human tester and must not be inferred from offline tests.

## Automated and source gates

- [x] `python -m unittest discover -s tests -v` passes.
- [x] A clean offscreen Qt startup constructs the main window successfully.
- [x] `build_exe.bat` completes and creates the full PyInstaller `onedir` output.
- [x] `dist\CourseCarry\CourseCarry.exe` starts with Python removed from `PATH` and remains running during the smoke interval.
- [x] `scripts\package_release.ps1` reads `0.6.0-alpha` from the application version and rejects mismatched or malformed version input.
- [x] The release ZIP contains `CourseCarry/CourseCarry.exe` and `CourseCarry/_internal/`.
- [x] The release audit finds no browser profiles, credentials, personal course data, logs, databases, local configuration, archive files, or `.part` files.
- [x] The generated ZIP passes a CRC read and its SHA-256 matches the `.sha256` file.

Automated evidence recorded on 2026-09-02: 39 offline tests passed; the clean Qt source startup passed; the PyInstaller build completed; the release packaged app remained running for six seconds with Python removed from `PATH`; malformed and mismatched release versions were rejected; and the 571-entry ZIP passed CRC, required-file, bundled `python313.dll`, privacy-name, and SHA-256 checks. The release SHA-256 is `035ede87fae39de6525a835c46e9d805824bdc827eee1eedcef6050cd98acff4`.

## Cached-course and workflow regression

- [ ] Startup never launches Chrome or begins a scan.
- [ ] A saved course list renders immediately with its last successful scan time.
- [ ] A cache from an earlier day offers **Use Saved Courses** and **Scan for Updates** only once per session.
- [ ] **Scan for Updates** remains visible in the top bar and course library.
- [ ] Search, current/archived filters, Select All Visible, Clear Selection, and selection count behave at the minimum window size.
- [ ] Selected courses remain selected through search/filter changes and a successful merged rescan when still available.
- [ ] **Download Selected Courses** starts the supported personal-submission backup and opens the progress page.
- [ ] Unavailable cached courses remain visible but cannot be selected.
- [ ] Activity and the final result distinguish downloaded, skipped, updated, failed, and incomplete items.

## Authorized NP live regression

- [ ] Complete normal NP SSO/MFA without entering credentials into CourseCarry.
- [ ] Confirm current, archived, View All, Load More, and paginated course views merge without duplicate cards.
- [ ] Confirm a complete scan updates the timestamp and closes managed Chrome while CourseCarry stays open.
- [ ] Confirm failed, timed-out, and cancelled scans close managed Chrome and keep the previous cache.
- [ ] Back up one small personal assignment submission and inspect its metadata.
- [ ] Repeat without LMS changes; confirm zero downloads, a skipped result, and no duplicate directory or filename suffix.
- [ ] Confirm backup success, failure, and cancellation close Chrome and Playwright child processes.

## Clean Windows device

- [ ] Copy only the release ZIP and checksum to a separate Windows 10/11 x64 laptop with Chrome installed and no Python installation.
- [ ] Verify the checksum, unblock the ZIP if Windows offers it, and extract the complete folder.
- [ ] Run `CourseCarry.exe` beside `_internal`; confirm startup succeeds without Python.
- [ ] Complete onboarding, choose an archive location, and confirm no automatic browser launch.
- [ ] Close and relaunch; confirm settings and the saved course list persist locally.
- [ ] Confirm the unsigned-app warning matches the README and no instruction asks the tester to disable security software.
- [ ] After the test, keep or delete the test laptop's local CourseCarry data according to the tester's own privacy needs; never send it with a bug report.

## ITE or another institution

- [ ] Complete every step in [`cross-institution-testing.md`](cross-institution-testing.md) using the tester's own authorized account.
- [ ] Keep the institution labelled untested until every required login, scan, download, repeat-skip, cancellation, and browser-cleanup check passes.
- [ ] Record only anonymous counts, public hostnames, versions, result categories, and redacted errors.

## Publication gate

- [x] Version is `0.6.0-alpha` in `coursecarry/version.py`, `pyproject.toml`, README, changelog, executable UI, ZIP name, release notes, and this checklist.
- [ ] Git changes contain only reviewed source, tests, documentation, and generated release artifacts intended for publication.
- [ ] The uploaded ZIP checksum matches the generated `.sha256` file.
- [ ] Known limitations, supported/untested institutions, and the unofficial-project disclaimer are visible on the release page.
- [ ] Tag `v0.6.0-alpha` only after every required gate is complete.
