# CourseCarry v0.5.1-alpha

CourseCarry is an experimental, unofficial Windows backup utility for personal POLITEMall / Brightspace course access. This alpha standardizes the CourseCarry application, package, executable, icon, database, logging, and local-path naming. It does not claim migration support for unrelated alpha data.

## Highlights

- Consistent CourseCarry application, package, executable, icon, database, logging, and local-path naming.
- User-controlled sign-in through normal Chrome, with no CourseCarry password field.
- Current and archived course discovery for the observed Ngee Ann Polytechnic portal flow.
- Personal assignment submission-history scanning and authenticated file backup.
- Streaming downloads, `.part` safety, size verification, bounded retries, duplicate/update decisions, and atomic completion.
- Local SQLite backup history, structured metadata, privacy-conscious diagnostics, and offline unit coverage.

## Important limitations

- This is alpha software and the observed portal selectors can change.
- Live compatibility is currently limited to the tested Ngee Ann Polytechnic flow; other institutions are unverified.
- Course-material, grade, feedback, interrupted-download resume, and offline archive search features are not implemented.
- The Windows build is unsigned and may trigger a reputation warning.
- Users remain responsible for institutional policies, platform terms, privacy, and copyright obligations.

## Install

Download the Windows x64 ZIP, unblock it in Windows file properties if needed, extract the entire archive, and run `CourseCarry.exe` beside its `_internal` folder. Google Chrome and a valid institutional account are required; Python is not.

Before publishing, complete `docs/release-checklist-v0.5.1-alpha.md` and verify the uploaded ZIP against its SHA-256 checksum.
