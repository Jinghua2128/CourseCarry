# CourseCarry v0.6.3-alpha Release Checklist

This compatibility build replaces the Qt 6.11 runtime that still failed to import `QtGui` on the affected laptop. Release users must be able to extract the ZIP and run CourseCarry without installing Python, Qt, or a Visual C++ Redistributable.

## Automated and source gates

- [x] Python 3.11 offline unit tests pass.
- [x] A clean offscreen Qt 6.5.3 source startup constructs the main window successfully.
- [x] Nuitka completes the standalone build using Python 3.11 and Qt 6.5.3.
- [x] The bundle contains `CourseCarry.exe`, `python311.dll`, QtGui, `qwindows.dll`, Playwright's Node driver, and all required application-local Visual C++ runtime DLLs.
- [x] Static inspection confirms bundled `qt6gui.dll` has no direct `d3d12.dll` import.
- [x] The bundle contains no copied `api-ms-win-*.dll` or `ucrtbase.dll` from the Windows 11 build computer.
- [x] `CourseCarry.exe --bundle-self-test` succeeds with Python removed from `PATH`.
- [x] The normal packaged application creates a visible CourseCarry window during the smoke test with Python removed from `PATH`.
- [x] The ZIP passes CRC, required-file, privacy-name, and SHA-256 checks.
- [x] The standalone `CourseCarry-Diagnostic.cmd` creates a privacy-safe report without importing Qt.

Automated evidence recorded on 2026-09-16: all 42 offline tests passed under Python 3.11 and PySide6/Qt 6.5.3; an offscreen source smoke test constructed the real 1220x790 main window; Nuitka produced the standalone build; and the bundle verifier accepted Python 3.11, QtGui 6.5.3, the Qt platform plugin, Playwright's Node driver, all five application-local Visual C++ runtime DLLs, and the host-operating-system DLL exclusion. Static PE inspection and the release gate both confirmed no direct `d3d12.dll` dependency in `qt6gui.dll`. After a fresh ZIP extraction, the QtGui/Playwright self-test returned exit code 0, the standalone diagnostic loaded every listed native component and produced a privacy-safe report, and a normal launch created a native window titled `CourseCarry 0.6.3-alpha`. The ZIP checksum matched its `.sha256` file: `ddb443f6d455681434cf110292fce1e07c7ba261b16ecccf2a6705b674675817`.

## Affected-laptop retest

- [ ] Delete the entire previously extracted CourseCarry folder.
- [ ] Transfer only the v0.6.3-alpha ZIP and checksum, then extract into a new, empty folder.
- [ ] Run `CourseCarry.exe` without installing any additional runtime or moving the EXE away from the other extracted files.
- [ ] Confirm the `QtGui` DLL error no longer appears.
- [ ] If startup still fails and no automatic report appears, run `CourseCarry-Diagnostic.cmd`; send `%LOCALAPPDATA%\CourseCarry\startup-diagnostic.txt` after confirming it contains no private course or account data.
- [ ] Complete onboarding and confirm startup does not open Chrome automatically.
- [ ] Scan current and archived courses and confirm the managed Chrome window closes afterward.
- [ ] Close and relaunch CourseCarry; confirm the saved course list and settings persist locally.

## Publication gate

- [ ] Version is `0.6.3-alpha` in the application, package metadata, README, changelog, ZIP name, release notes, and this checklist.
- [ ] Git changes contain only reviewed source, tests, documentation, and intended build scripts.
- [ ] The uploaded ZIP checksum matches the generated `.sha256` file.
- [ ] Known limitations, supported/untested institutions, and the unofficial-project disclaimer are visible on the release page.
- [ ] Tag `v0.6.3-alpha` only after the affected-laptop startup test passes.
