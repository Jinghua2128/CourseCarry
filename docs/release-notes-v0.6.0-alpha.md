# CourseCarry v0.6.0-alpha

> [!WARNING]
> Superseded by v0.6.1-alpha after a clean-laptop Qt runtime startup failure. Do not publish or share this build.

CourseCarry is an experimental, unofficial Windows utility for backing up a student's own Brightspace assignment submissions. Version 0.6 makes the saved course library the centre of the experience and keeps all scans under the user's control.

## Highlights

- Saved courses load immediately without opening Chrome, together with the last successful scan time.
- An earlier-day cache offers a once-per-session choice to use the saved list or scan for updates.
- Current, archived, View All, Load More, and paginated results merge by stable LMS course ID without duplicate cards.
- Missing cached courses are retained as unavailable after a complete scan; failed and cancelled scans keep the previous list unchanged.
- Course selection, search, filters, Select All, Clear Selection, and the primary download action now live in one course-library workflow.
- Managed Chrome closes after scan or backup success, failure, timeout, or cancellation while CourseCarry remains open.
- Stable file identities preserve filenames and allow an unchanged second backup to skip every matching file.
- Institution, portal, and Brightspace URLs are configurable behind the provider boundary.

## Compatibility

Ngee Ann Polytechnic is the only live-tested preset. ITE and every other institution remain untested and unsupported until the authorized checklist in `docs/cross-institution-testing.md` passes. Configurable URLs are a testing facility, not a compatibility claim.

Only personal assignment submissions and submission metadata are implemented. Course materials, grades, feedback, resumable partial downloads, and offline archive browsing are not implemented.

## Installation

Download the Windows x64 ZIP, verify its SHA-256, unblock it in Windows file properties if offered, extract the complete `CourseCarry` folder, and run `CourseCarry.exe` beside `_internal`. Google Chrome and a valid authorized institution account are required; Python is not.

Complete `docs/release-checklist-v0.6.0-alpha.md` before publishing.
