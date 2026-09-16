# CourseCarry v0.6.1-alpha Release Checklist

> [!WARNING]
> Superseded by v0.6.2-alpha. The affected laptop still failed while importing `QtGui`; do not publish or share the v0.6.1-alpha ZIP.

This patch follows a v0.6.0-alpha clean-laptop test that reached `QtGui` but failed to load a native Windows dependency. Automated checks can verify the bundle; successful startup on the affected laptop still requires an authorized human retest.

## Automated and source gates

- [x] `python -m unittest discover -s tests -v` passes.
- [x] A clean offscreen Qt startup constructs the main window successfully.
- [x] `build_exe.bat` completes and creates the full PyInstaller `onedir` output.
- [x] The root `_internal` folder contains `MSVCP140.dll`, `MSVCP140_1.dll`, and `MSVCP140_2.dll` matching the bundled PySide6 copies.
- [x] The bundled `VCRUNTIME140.dll` is not older than PySide6's required copy.
- [x] `dist\CourseCarry\CourseCarry.exe` starts with Python removed from `PATH` and remains running during the smoke interval.
- [x] `scripts\package_release.ps1` reads `0.6.1-alpha` from the application version and rejects mismatched or malformed version input.
- [x] The release ZIP contains `CourseCarry/CourseCarry.exe`, the complete `CourseCarry/_internal/` payload, and all three root MSVCP DLLs.
- [x] The release audit finds no browser profiles, credentials, personal course data, logs, databases, local configuration, archive files, or `.part` files.
- [x] The generated ZIP passes a CRC read and its SHA-256 matches the `.sha256` file.

Automated evidence recorded on 2026-09-02: 39 offline tests passed; the offscreen Qt source startup passed; `build_exe.bat` completed; all three root MSVCP files matched PySide6 byte-for-byte; the root VCRUNTIME version was 14.51.36247.0 against Qt's 14.44.35211.0 minimum; and the packaged app remained running for six seconds with Python removed from `PATH`. Malformed and mismatched release versions were rejected. The 574-entry ZIP passed CRC, required-file, privacy-name, and SHA-256 checks. The release SHA-256 is `42e8ab453d117cf161269da750671c36e45a7459e47fccb5edb283cae7a7dfa5`.

## Affected-laptop retest

- [ ] Delete the complete previously extracted CourseCarry folder.
- [ ] Transfer only the new v0.6.1-alpha ZIP and checksum, then extract into a new, empty folder.
- [ ] Confirm the laptop is x64 and runs Windows 10 version 1809 or newer, or Windows 11.
- [ ] Run `CourseCarry.exe` beside `_internal`; confirm the `QtGui` DLL error no longer appears.
- [ ] Complete onboarding and confirm startup does not open Chrome automatically.
- [ ] Close and relaunch; confirm settings persist locally.

If startup still fails, record only the CourseCarry version, Windows version from `winver`, System type from **Settings > System > About**, and the redacted error. Do not share browser data, logs containing personal information, or course files.

## Cached-course and authorized NP regression

- [ ] Startup loads the saved course list without launching Chrome or beginning a scan.
- [ ] A current-and-archived scan merges all course views without duplicate cards.
- [ ] A complete scan updates the timestamp and closes managed Chrome while CourseCarry stays open.
- [ ] Back up one small personal assignment submission and inspect its metadata.
- [ ] Repeat without LMS changes; confirm zero downloads and a skipped result.
- [ ] Confirm success, failure, timeout, and cancellation close managed Chrome and child processes.

## Publication gate

- [ ] Version is `0.6.1-alpha` in the application, package metadata, README, changelog, ZIP name, release notes, and this checklist.
- [ ] Git changes contain only reviewed source, tests, documentation, and generated release artifacts intended for publication.
- [ ] The uploaded ZIP checksum matches the generated `.sha256` file.
- [ ] Known limitations, supported/untested institutions, and the unofficial-project disclaimer are visible on the release page.
- [ ] Tag `v0.6.1-alpha` only after every required gate is complete.
