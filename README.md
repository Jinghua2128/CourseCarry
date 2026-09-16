# CourseCarry

An unofficial, local-first Brightspace utility for backing up a student's own assignment submissions.

> [!IMPORTANT]
> **CourseCarry is an independent student project.** It is not affiliated with, authorized by, or endorsed by POLITEMall, D2L, Ngee Ann Polytechnic, or any other Polytechnic.
>
> It only requests content that the signed-in student can already access. Downloaded materials, metadata, and browser-session data stay on the student's computer. Users are responsible for protecting that data and following their institution's policies, platform terms, and copyright rules.

> [!WARNING]
> CourseCarry is experimental alpha software. It is being actively tested against Ngee Ann Polytechnic's POLITEMall / Brightspace environment. Compatibility with other Singapore polytechnics has not been confirmed.

## What it does

CourseCarry is a Windows desktop backup manager for personal assignment submissions. It loads a saved course library without opening a browser, opens Google Chrome only when the user chooses to scan or download, and writes an organized offline archive.

It is not a credential collector, access-control bypass, account-sharing tool, or mass-redistribution tool.

## Features

### Implemented in 0.6 alpha

- User-controlled Microsoft / school SSO and MFA in normal Chrome
- Persistent local browser profile; no password field in CourseCarry
- Immediate cached-course loading with a human-readable last successful scan time
- User-controlled current and archived Brightspace course detection
- Search, current/archived filters, Select All, Clear Selection, and multi-course download from the course library
- Personal assignment submission-history scanning
- Authenticated submitted-file downloads
- Large-file streaming in configurable chunks; files are never loaded fully into memory
- `.part` temporary files, final-size verification, bounded retries, and atomic completion
- Duplicate/update decisions using stable LMS identities, server size, and local size
- Semester → course → assignment → submission archive structure
- Per-assignment metadata with downloaded, skipped, updated, failed, and incomplete states
- Dashboard, Courses, Backup, Activity, Settings, and first-run onboarding
- Background workers so browser and network work do not freeze the interface
- Daily local logging with credential-like values redacted
- Incremental SQLite backup-run index while retaining `courses.json` compatibility
- Configurable institution, portal, and Brightspace URLs with a tested NP preset and an explicitly untested custom preset

The provider was migrated from a working prototype. A live end-to-end check against a real account is still required for each alpha release because Brightspace markup and institutional SSO flows can change.

### Coming soon

- Course-material backup
- Grades and feedback backup
- Resume support for interrupted `.part` downloads
- Offline archive search and browsing

The interface labels unimplemented options as **Coming Soon**.

## Everyday workflow

1. Open CourseCarry. The saved course list and last successful scan time appear immediately; Chrome does not open.
2. If the saved list is from an earlier day, choose **Use Saved Courses** or **Scan for Updates**. This question appears at most once per application session.
3. Search or filter the library, select one or more available courses, and choose **Download Selected Courses**.
4. CourseCarry opens its managed Chrome profile for the institution's normal SSO/MFA when a scan or download needs it. The managed Chrome window closes after success, failure, timeout, or cancellation; CourseCarry stays open.
5. Review the downloaded, skipped, updated, failed, and incomplete counts. Running the same backup again with no LMS changes downloads nothing and reports the matching files as skipped.

**Scan for Updates** remains visible in the top bar and course library. CourseCarry never scans automatically at startup. The last successful scan timestamp and merged course cache are stored locally in `data/courses.json`. Complete scans merge current, archived, and paginated results by stable LMS course ID. A cached course missing from a complete scan is kept and marked unavailable; failed or cancelled scans do not replace the saved list.

## Screenshots

Screenshots use fake sample course data.

### Dashboard

![CourseCarry Dashboard](screenshots/dashboard.png)

### Course browser

![CourseCarry Course browser](screenshots/courses.png)

### Backup configuration and progress

![CourseCarry Backup page](screenshots/backup.png)

### Settings

![CourseCarry Settings page](screenshots/settings.png)

## Current status

CourseCarry is `v0.6.3-alpha`. Expect selector breakage, incomplete metadata, and behavior changes. Keep an independent copy of important files and inspect backup results before relying on them.

## Supported / tested institutions

| Institution | Status |
| --- | --- |
| Ngee Ann Polytechnic | Actively tested; initial provider implementation |
| Singapore Polytechnic | Untested |
| Nanyang Polytechnic | Untested |
| Temasek Polytechnic | Untested |
| Republic Polytechnic | Untested |
| Institute of Technical Education (ITE) | Untested; not a support claim |

These rows are not compatibility claims. Other institutions may use different domains, login flows, permissions, or Brightspace configurations.

## Install a Windows release

Requirements:

- 64-bit Windows 10 version 1809 or newer, or 64-bit Windows 11
- Google Chrome
- Internet connection
- A valid institutional account with authorized Brightspace access

Installation:

1. Download the Windows ZIP from [GitHub Releases](../../releases).
2. Right-click the ZIP, select **Properties**, and choose **Unblock** if Windows shows that option.
3. Select **Extract All** into a new, empty folder. Do not extract a new release over an older CourseCarry folder, and do not run the app from inside the ZIP.
4. Open the extracted `CourseCarry` folder and run `CourseCarry.exe`.
5. Keep every extracted file and folder together; moving only `CourseCarry.exe` will prevent the app from starting.

Release users do not need to install Python, Qt, or a Visual C++ Redistributable. Everything application-specific is included in the extracted folder. CourseCarry intentionally uses the locally installed Google Chrome. If Chrome cannot be detected, select `chrome.exe` in Settings.

CourseCarry is currently unsigned, so Windows may show a reputation warning for a new release. Only run downloads obtained from the project's official GitHub Releases page, and never disable security software globally.

### Clean-device test

1. Copy only the release ZIP and `.sha256` file to a separate Windows 10/11 x64 laptop with Chrome installed and no Python installation.
2. Verify the SHA-256, extract the whole folder, and run `CourseCarry.exe` without moving it away from the other extracted files.
3. Complete onboarding and confirm startup does not open Chrome automatically.
4. Scan only with the tester's own authorized account, then confirm Chrome closes and CourseCarry remains open.
5. Close and relaunch CourseCarry to confirm the saved course list, scan time, and settings persist.
6. Confirm no Chrome or Playwright child process remains after success, failure, timeout, or cancellation.

If CourseCarry cannot load its Windows interface, it may create a privacy-safe `startup-diagnostic.txt` under `%LOCALAPPDATA%\CourseCarry`. If no report appears, double-click `CourseCarry-Diagnostic.cmd` in the extracted folder. The included diagnostic uses Windows' built-in PowerShell to identify the Windows build and the native DLL that failed to load; it does not require Python or Qt and excludes usernames, paths, course data, browser data, and credentials.

Use the complete [`v0.6.3-alpha` release checklist](docs/release-checklist-v0.6.3-alpha.md) before publishing or sharing the build.

### Institution configuration

Settings includes the tested **Ngee Ann Polytechnic** preset and a **Custom Brightspace (untested)** option with institution name, portal URL, and Brightspace URL fields. URLs must be HTTPS and cannot contain embedded credentials. Custom settings do not make an institution supported; use the [authorized cross-institution checklist](docs/cross-institution-testing.md) and keep ITE or another institution labelled untested until every required check passes.

## Run from source

```bat
git clone <repository-url>
cd CourseCarry

py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

Or, after cloning, run:

```bat
setup_windows.bat
run_windows.bat
```

The legacy bulk console command remains available for development:

```bat
python backup_all.py
```

Scan courses in the desktop app first so the local course cache exists.

## Build the Windows app

The Windows build uses Python 3.11, the Qt 6.5.3 compatibility line, and Nuitka `standalone` mode with its PySide6 and Playwright deployment plugins. This produces an extract-and-run folder containing Python, Qt, the Visual C++ application runtime, and the Playwright driver without copying Windows operating-system DLLs from the build computer.

```bat
build_exe.bat
```

Output:

```text
dist/
└── CourseCarry/
    ├── CourseCarry.exe
    ├── PySide6/
    ├── playwright/
    └── required DLLs
```

Distribute the **whole `CourseCarry` folder as a ZIP**, not the EXE by itself. The build script installs development-only dependencies, runs offline unit tests, compiles a Nuitka standalone build, and verifies the Qt, Playwright, Python, and application-local C++ runtimes. The first development build may download Nuitka's compiler and dependency-analysis helpers; release users never run this build step.

Create the versioned release ZIP, verify its contents, and generate a SHA-256 checksum with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package_release.ps1
```

The release artifacts are written to `release/`. Complete the manual regression and publication gate in [`docs/release-checklist-v0.6.3-alpha.md`](docs/release-checklist-v0.6.3-alpha.md) before publishing them.

## How it works

```text
Launch CourseCarry
→ load the saved course list and last successful scan time
→ user optionally scans for updates in a managed Chrome profile
→ merge current, archived, and paginated courses by LMS id
→ close Chrome and return to the still-open CourseCarry window
→ user selects courses and starts a supported backup
→ user completes normal SSO / MFA in Chrome if needed
→ scan personal assignment submission history
→ stream each file to filename.part
→ verify its size and atomically rename it
→ write metadata and local backup history
```

Browser and LMS behavior is isolated behind `LMSProvider`. `NPBrightspaceProvider` is the only live-tested preset. `BrightspaceProvider` accepts custom institution URLs for authorized manual testing, but ITE and every non-NP institution remain unsupported until an end-to-end login, course scan, submission scan, and download test passes. See [`docs/architecture.md`](docs/architecture.md).

## Archive structure

```text
CourseCarry Archive/
└── 26S1/
    └── 26S1-1_SAMPLE_000001 [course-123456]/
        └── Assignments/
            └── Week 1 - Sample [assignment-987654]/
                ├── Submission/
                │   └── sample-file.pptx
                └── metadata.json
```

Windows-invalid characters are replaced, components are length-bounded, and stable LMS IDs keep different courses and assignments in different directories. Stable file identities reuse prior filenames when available, so repeated backups and changed LMS ordering do not create avoidable numeric suffixes. A file is skipped only when its stable identity and server/local size checks match.

## Privacy and data safety

CourseCarry does not ask users to enter a school or Microsoft password into the application. Authentication happens in normal Chrome through the institution's SSO flow. The local browser profile may contain an authenticated session and must be treated as sensitive.

Never share or commit:

- `chrome-profile/` or `browser-data/`
- cookies, tokens, authorization headers, passwords, or MFA codes
- `data/courses.json`, SQLite databases, or their journal/WAL sidecars
- `config.json` when it contains personal paths
- personal course files, submitted assignments, or archive metadata
- logs that have not been reviewed for personal information

The repository ignores these paths and includes [`config.example.json`](config.example.json) and [`data/courses.example.json`](data/courses.example.json) with fake values. Download metadata keeps only a non-reversible source fingerprint, and diagnostics redact credential values, private URL details, and absolute paths. Users should still review diagnostics before sharing them. See [`SECURITY.md`](SECURITY.md) and the [security audit](docs/security-audit.md).

## Intended use and disclaimer

CourseCarry is intended only for personal archival of content that the signed-in user is already authorized to access. It does not grant permission to copy, publish, share, sell, or redistribute course materials.

Do not use CourseCarry to bypass authentication, MFA, SSO, permissions, access restrictions, or institutional controls. Users are responsible for complying with their institution's acceptable-use rules, POLITEMall terms, privacy requirements, and applicable copyright law. The software is provided without warranty under the MIT License.

## Known limitations

- Only NP's observed POLITEMall / Brightspace flow has passed live testing.
- ITE and every other non-NP institution are untested; configurable URLs are for authorized compatibility testing, not a support claim.
- Brightspace selectors may change without notice.
- Course materials, grades, and feedback are not implemented.
- Interrupted `.part` files are retained as incomplete markers but are not resumed yet.
- Downloads are deliberately sequential to avoid aggressive LMS traffic.
- Browser profile/session data requires the same care as any signed-in browser profile.
- Live authentication and network behavior require manual integration testing; automated tests stay offline.
- Scan cancellation is normally observed within a fraction of a second, but an in-progress browser navigation can take up to 15 seconds to return.

## Roadmap

### Near-term

- Live regression testing of the renamed desktop build
- More detailed progress and failed-item review
- Resumable interrupted downloads
- Course-material, grade, and feedback backup
- Expanded SQLite assignment/file index
- Improved anonymized diagnostics

### Medium-term

- Backup history and incremental synchronization
- SHA-256 integrity checks
- Offline archive search and course browser
- HTML archive viewer
- Update detection

### Experimental

- Community testing at other Singapore polytechnics
- Authorized ITE and other-institution compatibility testing
- Selective backup profiles and complete student archive export

## Testing

Run the offline unit suite:

```bat
python -m unittest discover -s tests -v
```

Tests cover scan timestamps, cached-course loading, current/archived parsing, pagination, course merging, unavailable-course handling, rescan deduplication, filename sanitization and collisions, archive paths, repeated-download skipping, authenticated redirect boundaries, and data redaction. They do not contact any institution.

## Bug reports

Use the anonymized form in [`docs/compatibility-report.md`](docs/compatibility-report.md). Report the institution, LMS hostname, login result, counts rather than names, CourseCarry version, and a redacted error. Never post private account information.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Provider and selector changes should explain how they were verified, while automated tests must avoid unnecessary LMS traffic.

## Development environment

- Python 3.11 (the release build rejects other Python minor versions)
- PySide6
- Playwright for Python
- Requests
- SQLite from the Python standard library
- Nuitka for Windows standalone builds

## License

MIT — see [`LICENSE`](LICENSE).
