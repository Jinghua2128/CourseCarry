# Architecture

```text
PySide6 UI
  ├─ immediate CourseCacheStore load
  │   └─ courses.json: scan time + merged current/archived course state
  └─ QThread workers
      ├─ LMSProvider factory
      │   ├─ NPBrightspaceProvider (tested NP preset)
      │   └─ BrightspaceProvider (configurable, untested elsewhere)
      │   └─ Playwright persistent Chrome context
      ├─ BackupManager
      │   └─ per-course → per-assignment → per-file recovery
      ├─ AuthenticatedDownloader
      │   └─ exact HTTPS origin → secure cookies → validated redirects
      │       └─ Requests streaming → .part → size check → atomic replace
      └─ local state
          ├─ courses.json compatibility cache
          ├─ SQLite backup-run index
          ├─ metadata.json per assignment
          └─ redacted daily logs
```

The provider boundary keeps institution URLs and Brightspace navigation out of shared UI and backup orchestration. The NP preset supplies the only live-tested configuration. Custom institution, portal, and LMS URLs use the same conservative Brightspace implementation but remain explicitly untested until an authorized end-to-end login and download check passes.

Course scans never run on startup. `CourseCacheStore` loads the saved list first, stores the last successful scan time in `data/courses.json`, and merges complete scan results by immutable LMS course ID. A complete scan marks missing cached courses unavailable; cancellation and failure leave the saved list unchanged. The worker closes its persistent Playwright context before reporting a result, preserving the profile directory while terminating the managed Chrome process.

Archive directory identities combine bounded, Windows-safe display names with immutable LMS IDs. `metadata.json` stores a SHA-256 stable file identity for duplicate detection rather than a private or signed download URL. Previous filenames are reused by file identity so ordering changes do not create unnecessary numeric suffixes.
