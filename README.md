# PoliteLoad

A personal POLITEMall / Brightspace backup utility for students.

> [!WARNING]
> PoliteLoad is experimental alpha software.
>
> It is being actively tested against Ngee Ann Polytechnic's POLITEMall / Brightspace environment. Compatibility with other Singapore polytechnics has not been confirmed and requires community testing.

## Overview

PoliteLoad is a Windows desktop backup manager for course content that the logged-in student is already authorized to access. It opens Google Chrome for the institution's normal login flow, scans visible courses and personal assignment submission history, then writes an organized local archive.

It is not a credential collector, access-control bypass, account-sharing tool, or mass redistribution tool.

## Features

### Implemented in 0.5 alpha

- User-controlled Microsoft / school SSO and MFA in normal Chrome
- Persistent local browser profile; no password field in PoliteLoad
- POLITEMall course-card detection and course ID extraction
- Personal assignment submission-history scanning
- Authenticated submitted-file downloads
- Large-file streaming in configurable chunks; files are never loaded fully into memory
- `.part` temporary files, final-size verification, bounded retries, and atomic completion
- Duplicate/update decisions using filename, server size, local size, and source URL
- Semester → course → assignment → submission archive structure
- Per-assignment metadata with downloaded, skipped, updated, failed, and incomplete states
- Desktop Dashboard, Courses, Backup, Activity, Settings, and first-run onboarding
- Background Qt workers for browser and network work
- Daily local logging with credential-like values redacted
- Incremental SQLite backup-run index while retaining `courses.json` compatibility

The original selectors and browser behavior were migrated from a working prototype. A live end-to-end regression pass against a real account is still required for each alpha release because Brightspace markup and institutional SSO flows can change.

### Coming soon

- Course-material backup
- Grades and feedback backup
- Resume support for interrupted `.part` downloads
- Offline archive search and browsing

The UI labels unimplemented options as **Coming Soon** and does not expose fake controls.

## Screenshots

Screenshots use fake sample course data.

### Dashboard

![PoliteLoad Dashboard](screenshots/dashboard.png)

### Course browser

![PoliteLoad Course browser](screenshots/courses.png)

### Backup configuration and progress

![PoliteLoad Backup page](screenshots/backup.png)

### Settings

![PoliteLoad Settings page](screenshots/settings.png)

## Current status

PoliteLoad is `v0.5.0-alpha`. Expect selector breakage, incomplete metadata, and behavior changes. Keep an independent copy of important files and inspect backup results before relying on them.

## Supported / tested institutions

| Institution | Status |
| --- | --- |
| Ngee Ann Polytechnic | Actively tested; initial provider implementation |
| Singapore Polytechnic | Untested |
| Nanyang Polytechnic | Untested |
| Temasek Polytechnic | Untested |
| Republic Polytechnic | Untested |

These rows are not compatibility claims. Other institutions may use different domains, login flows, permissions, or Brightspace configurations.

## Installation

Prerequisites:

- Windows 10 or Windows 11
- Python 3.11 or newer
- Google Chrome
- Internet connection
- A valid institutional account with normal POLITEMall access

Download or clone the project, then run:

```bat
setup_windows.bat
run_windows.bat
```

PoliteLoad intentionally uses locally installed Google Chrome for the initial release. It does not bundle Playwright Chromium. If Chrome cannot be detected, choose `chrome.exe` in Settings.

## Running from source

```bat
git clone <repository-url>
cd PoliteLoad

py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

The legacy bulk console command remains available for development:

```bat
python backup_all.py
```

Scan courses in the desktop app first so the local course cache exists.

## Windows EXE

The initial build uses PyInstaller `onedir`, which is more reliable for Qt and Playwright assets than `onefile` during alpha development.

```bat
build_exe.bat
```

Output:

```text
dist/
└── PoliteLoad/
    └── PoliteLoad.exe
```

The build script installs development dependencies, runs offline unit tests, cleans old PyInstaller output, and builds [`PoliteLoad.spec`](PoliteLoad.spec).

## How it works

```text
Launch PoliteLoad
→ open managed Chrome profile
→ user completes normal SSO / MFA if needed
→ detect visible courses
→ scan personal assignment submission history
→ stream each file to filename.part
→ verify size and atomically rename
→ write metadata and local backup history
```

Browser and LMS behavior is isolated behind `LMSProvider`; the only current implementation is `NPBrightspaceProvider`. Future providers must be independently tested before support is claimed. See [`docs/architecture.md`](docs/architecture.md).

## Folder structure

```text
PoliteLoad Archive/
└── 26S1/
    └── 26S1-1_SAMPLE_000001 [course-123456]/
        └── Assignments/
            └── Week 1 - Sample [assignment-987654]/
                ├── Submission/
                │   └── sample-file.pptx
                └── metadata.json
```

Windows-invalid characters are replaced, components are length-bounded, and stable LMS IDs keep different courses and assignments in different directories. Same-named files in one assignment receive stable numeric suffixes.

## Privacy & security

PoliteLoad does not require users to enter their NPNet or Microsoft password into the application. Authentication occurs through the institution's normal browser login process. Browser profile and session data remain on the user's computer.

Never share or commit:

- `chrome-profile/` or `browser-data/`
- cookies, tokens, or authorization headers
- `data/courses.json`, SQLite databases, or their journal/WAL sidecars
- `config.json` when it contains personal paths
- personal course files, submitted assignments, or archive metadata
- logs that have not been reviewed for personal information

The repository ignores these paths and includes [`config.example.json`](config.example.json) and [`data/courses.example.json`](data/courses.example.json) with fake values instead. Download metadata keeps only a non-reversible source fingerprint, and diagnostics redact credential values, private URL details, and absolute paths. Users should still review any diagnostic before sharing. See [`SECURITY.md`](SECURITY.md) and the [`security audit`](docs/security-audit.md).

## Intended use and disclaimer

PoliteLoad is intended for personal archival of content that the logged-in user is already authorized to access. Users are responsible for following their institution's terms, copyright rules, and policies regarding downloaded materials.

The software does not grant permission to redistribute course materials and must not be used to bypass MFA, SSO, authentication, permissions, or hidden-content restrictions. It is provided without warranty under the MIT License.

## Known limitations

- Only NP's observed POLITEMall / Brightspace flow has an implementation.
- Brightspace selectors may change without notice.
- Course materials, grades, and feedback are not implemented.
- Interrupted `.part` files are retained as incomplete markers but are not resumed yet.
- Downloads are deliberately sequential to avoid aggressive LMS traffic.
- Chrome profile/session data requires the same care as any logged-in browser profile.
- Live authentication and network behavior require manual integration testing; automated tests stay offline.

## Roadmap

### Near-term — Planned

- Live regression testing of the new desktop flow
- More detailed progress and failed-item review
- Resumable interrupted downloads
- Course-material, grade, and feedback backup
- Expanded SQLite assignment/file index
- Improved anonymized diagnostics

### Medium-term — Researching

- Backup history and incremental synchronization
- SHA-256 integrity checks
- Offline archive search and course browser
- HTML archive viewer
- Update detection

### Experimental

- Community testing at other Singapore polytechnics
- Generic Brightspace provider
- Selective backup profiles and complete student archive export

## Testing

Run the offline unit suite:

```bat
python -m unittest discover -s tests -v
```

Tests cover semester extraction, filename sanitization and collisions, course/assignment ID parsing, archive paths, and duplicate detection. They do not contact POLITEMall.

## Bug reports

Use the anonymized form in [`docs/compatibility-report.md`](docs/compatibility-report.md). Report the institution, LMS hostname, login result, counts rather than names, PoliteLoad version, and a redacted error. Never post private account information.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Provider and selector changes should explain how they were verified, while tests must avoid unnecessary LMS traffic.

## Development environment

- Python 3.11+
- PySide6
- Playwright for Python
- Requests
- SQLite from the Python standard library
- PyInstaller for Windows builds

## License

MIT — see [`LICENSE`](LICENSE).
