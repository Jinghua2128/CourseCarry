# CourseCarry v0.6.1-alpha

> [!WARNING]
> Superseded by v0.6.2-alpha after the affected laptop still failed to import `QtGui`. Do not publish or share this build.

CourseCarry is an experimental, unofficial Windows utility for backing up a student's own Brightspace assignment submissions. Version 0.6.1 is a Windows compatibility patch for the 0.6 course-library release.

## What changed

- Added the PySide6-matched Visual C++ support DLLs to CourseCarry's primary runtime directory so Qt does not depend on another laptop's installed MSVCP version.
- Added build and ZIP checks that reject a release when those DLLs are missing or do not match PySide6's copies.
- Added a startup message with recovery steps when Windows still cannot load Qt.
- Clarified fresh extraction: delete the old extracted folder and unpack this release into a new, empty folder.

All course-cache, current/archived scanning, selection, backup, and provider changes from v0.6.0-alpha remain included.

## Compatibility

This build supports 64-bit Windows 10 version 1809 or newer and 64-bit Windows 11. Google Chrome and a valid authorized institution account are required; Python is not.

Ngee Ann Polytechnic is the only live-tested preset. ITE and every other institution remain untested and unsupported until the authorized checklist in `docs/cross-institution-testing.md` passes.

## Installation

Download the Windows x64 ZIP and its checksum. Delete any older extracted `CourseCarry` folder, extract the complete new ZIP into an empty folder, and run `CourseCarry.exe` beside `_internal`. Do not copy only the EXE and do not merge this release into a previous extraction.

Complete `docs/release-checklist-v0.6.1-alpha.md` before publishing.
