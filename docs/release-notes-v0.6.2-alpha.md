# CourseCarry v0.6.2-alpha

> Superseded by v0.6.3-alpha. The affected laptop still failed while importing `QtGui`; do not publish or share the v0.6.2-alpha ZIP.

CourseCarry is an experimental, unofficial Windows utility for backing up a student's own Brightspace assignment submissions. Version 0.6.2 replaces the Windows packaging pipeline after two clean-laptop Qt startup failures.

## Portable Windows build

- The ZIP contains Python, Qt, the Visual C++ application runtime, and the Playwright driver.
- Users do not install Python, Qt, or a Visual C++ Redistributable.
- The application is compiled as a Nuitka standalone folder using its PySide6 and Playwright deployment plugins.
- Windows system components such as `ucrtbase.dll` and API-forwarder DLLs are deliberately not copied from the Windows 11 build computer. Supported laptops use the matching components already provided by their own Windows installation.
- A packaged self-test verifies both the QtGui import and Playwright driver before release.

All course-cache, current/archived scanning, selection, backup, and provider improvements from v0.6 remain included.

## Installation

Delete any previously extracted CourseCarry folder. Extract the complete v0.6.2 ZIP into a new, empty folder and run `CourseCarry.exe`. Keep every extracted file and folder together. No additional installer is required.

CourseCarry supports 64-bit Windows 10 version 1809 or newer and 64-bit Windows 11. Google Chrome and an authorized institutional account are required for scanning and backup.
