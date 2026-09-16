# CourseCarry v0.6.2-alpha Release Checklist

> Superseded by v0.6.3-alpha. The affected laptop still failed while importing `QtGui`; do not publish or share the v0.6.2-alpha ZIP.

This release replaces the PyInstaller bundles that failed to import `QtGui` on the affected laptop. Release users must be able to extract the ZIP and run CourseCarry without installing Python, Qt, or a Visual C++ Redistributable.

## Automated and source gates

- [x] `python -m unittest discover -s tests -v` passes.
- [x] A clean offscreen Qt source startup constructs the main window successfully.
- [x] `build_exe.bat` completes the Nuitka standalone build.
- [x] The build contains `CourseCarry.exe`, Python, QtGui, the Qt platform plugin, Playwright's Node driver, and the required application-local Visual C++ runtime DLLs.
- [x] The build contains no copied `api-ms-win-*.dll` or `ucrtbase.dll` from the Windows 11 development computer.
- [x] `CourseCarry.exe --bundle-self-test` succeeds with Python removed from `PATH`, proving the packaged QtGui import and Playwright driver startup.
- [x] The normal packaged application remains running through the smoke interval with Python removed from `PATH`.
- [x] The release packager rejects malformed and mismatched versions.
- [x] The ZIP passes CRC, required-file, privacy-name, and SHA-256 checks.

Automated evidence recorded on 2026-09-03: 39 offline tests passed; the offscreen Qt source startup passed; Nuitka produced the standalone build; and the bundle contained Python 3.13, QtGui, `qwindows.dll`, Playwright's Node driver, and all five required application-local C++ runtime DLLs. The audit found no copied Windows API-set or UCRT DLLs and no private runtime data. After a fresh ZIP extraction, the QtGui/Playwright self-test returned exit code 0 and the normal application remained running for eight seconds with Python removed from `PATH`. Malformed and mismatched release versions were rejected. The 384-entry ZIP passed CRC, required-file, privacy-name, and SHA-256 checks. The release SHA-256 is `d3a3692bbf265fb9590a395274ebdd7e6c84155ae07255b32c229f81f29c6034`.

## Affected-laptop retest

- [ ] Delete the entire previously extracted CourseCarry folder.
- [ ] Transfer only the v0.6.2-alpha ZIP and checksum, then extract into a new, empty folder.
- [ ] Run `CourseCarry.exe` without installing any additional runtime or moving the EXE away from the other extracted files.
- [ ] Confirm the `QtGui` DLL error no longer appears.
- [ ] Complete onboarding and confirm startup does not open Chrome automatically.
- [ ] Scan current and archived courses and confirm the managed Chrome window closes afterward.
- [ ] Close and relaunch CourseCarry; confirm the saved course list and settings persist locally.

## Publication gate

- [ ] Version is `0.6.2-alpha` in the application, package metadata, README, changelog, ZIP name, release notes, and this checklist.
- [ ] Git changes contain only reviewed source, tests, documentation, and intended build scripts.
- [ ] The uploaded ZIP checksum matches the generated `.sha256` file.
- [ ] Known limitations, supported/untested institutions, and the unofficial-project disclaimer are visible on the release page.
- [ ] Tag `v0.6.2-alpha` only after the affected-laptop startup test passes.
