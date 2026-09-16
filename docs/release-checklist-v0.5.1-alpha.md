# CourseCarry v0.5.1-alpha Release Checklist

This checklist separates automated evidence from the live checks that require an authorized student account and a normal POLITEMall / Brightspace session.

## Automated release gates

- [x] `python -m unittest discover -s tests -v` passes.
- [x] `build_exe.bat` completes without warnings that affect startup or packaged modules.
- [x] `dist\CourseCarry\CourseCarry.exe` launches from the complete `onedir` folder.
- [x] `scripts\package_release.ps1` creates the versioned ZIP and SHA-256 file.
- [x] The ZIP contains `CourseCarry/CourseCarry.exe` and `CourseCarry/_internal/`.
- [x] The packaging audit reports no private browser state, personal course data, logs, databases, local configuration, or partial downloads.

Automated evidence recorded on 2026-08-28: 22 tests passed; the packaged executable remained running during a six-second hidden startup smoke test; the archive audit passed; and the generated SHA-256 was `8db80557db8fffce4edca5f46373e2267c7c5495d880975008f76a06fdf16844`.

## Authorized live regression

Perform these checks only with your own account and content you are already allowed to access.

- [ ] Start with CourseCarry closed and no password or MFA value stored in the application.
- [ ] Launch the managed Chrome flow and complete the institution's normal SSO and MFA screens.
- [ ] Confirm CourseCarry never displays its own password field and does not log credential values.
- [ ] Scan current courses and confirm at least one expected current course appears.
- [ ] Scan archived courses and confirm an expected archived course appears when the account has one.
- [ ] Confirm course titles, semesters, IDs, and origins match the signed-in portal.
- [ ] Open an assignment with a personal submission and confirm only the signed-in student's submission history is shown.
- [ ] Back up one small submitted file and one larger file.
- [ ] Confirm each download is written beneath the selected archive root and finishes without a lingering `.part` file.
- [ ] Run the same backup again and confirm unchanged files are skipped.
- [ ] Replace or alter one local test copy, rerun the backup, and confirm the update decision is understandable and safe.
- [ ] Interrupt one download and confirm the incomplete `.part` file is retained and clearly reported.
- [ ] Confirm Activity and logs report useful status without exposing full private URLs, cookies, tokens, headers, or absolute personal paths.

## Brand consistency

- [ ] Confirm CourseCarry uses only its current local paths and does not claim migration support for unrelated alpha data.
- [ ] Confirm the window title, onboarding, navigation, executable, screenshots, and visible documentation consistently say CourseCarry.
- [ ] Confirm references to POLITEMall and Brightspace remain only where they identify the supported provider or service.

## Clean-machine smoke test

- [ ] Copy the ZIP to a separate Windows 10 or Windows 11 machine or clean test account.
- [ ] Extract the complete ZIP; do not move the EXE away from `_internal`.
- [ ] Launch `CourseCarry.exe` with Google Chrome installed.
- [ ] Confirm Windows reputation or unsigned-app messaging matches the README warning.
- [ ] Complete onboarding, select an archive directory, open Chrome, and reach the normal sign-in page.
- [ ] Close and relaunch the application and confirm settings persist without requiring Python.

## Publication gate

- [ ] Version is `0.5.1-alpha` in `coursecarry/version.py`, `pyproject.toml`, README, changelog, executable UI, ZIP name, and release notes.
- [ ] Git working tree contains only reviewed release changes.
- [ ] The intended commit is tagged `v0.5.1-alpha` only after every required gate above passes.
- [ ] The uploaded ZIP checksum matches the generated `.sha256` file.
- [ ] Known limitations and the unofficial-project disclaimer are visible on the release page.
