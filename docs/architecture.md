# Architecture

```text
PySide6 UI
  └─ QThread workers
      ├─ NPBrightspaceProvider
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

The provider boundary intentionally keeps NP-specific domains, SSO navigation behavior, and Brightspace selectors out of the UI and backup orchestration. Other institutions are not considered supported until their behavior is tested independently.

Archive directory identities combine bounded, Windows-safe display names with immutable LMS IDs. `metadata.json` stores a SHA-256 source fingerprint for duplicate detection rather than a private or signed download URL.
