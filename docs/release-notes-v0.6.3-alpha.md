# CourseCarry v0.6.3-alpha

CourseCarry is an experimental, unofficial Windows utility for backing up a student's own Brightspace assignment submissions. Version 0.6.3 changes the Windows runtime after the affected laptop still failed to import `QtGui` from the v0.6.2 Qt 6.11 build.

## Portable Windows compatibility build

- The release uses Python 3.11 and PySide6/Qt 6.5.3. Static inspection confirms this QtGui build does not directly import the three D3D12 procedures present in the failed Qt 6.11 build.
- The ZIP contains Python, Qt, the Visual C++ application runtime, and the Playwright driver. Users do not install any of those components.
- Windows system components such as `ucrtbase.dll` and API-forwarder DLLs are not copied from the build computer.
- If the Qt interface still cannot load, CourseCarry may write `%LOCALAPPDATA%\CourseCarry\startup-diagnostic.txt`. If an early Windows loader failure prevents that, `CourseCarry-Diagnostic.cmd` creates the same privacy-safe report using built-in PowerShell without requiring Python or Qt. It excludes usernames, paths, course data, browser data, and credentials.

## Install

Delete any previously extracted CourseCarry folder. Extract the complete v0.6.3 ZIP into a new, empty folder and run `CourseCarry.exe`. Keep every extracted file and folder together. No additional installer is required.

CourseCarry supports 64-bit Windows 10 version 1809 or newer and 64-bit Windows 11. Google Chrome and an authorized institutional account are required for scanning and backup.

## Verification status

All 42 offline tests passed on the development laptop. The exact release ZIP passed its packaged self-test and standalone diagnostic after fresh extraction, then opened a native window titled `CourseCarry 0.6.3-alpha`. Its SHA-256 is `ddb443f6d455681434cf110292fce1e07c7ba261b16ecccf2a6705b674675817`.

This build remains a candidate—not a confirmed public release—until it opens successfully on the affected laptop.
