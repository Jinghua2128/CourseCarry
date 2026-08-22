# Security audit — 2026-08-21

The project received a pre-publication Standard Codex Security review covering the authenticated browser/download boundary, archive filesystem behavior, private runtime state, diagnostics, packaging inputs, examples, and screenshots. The reviewed pre-remediation snapshot produced four medium and two low findings; all six were addressed in the current source.

| Finding | Severity | Current remediation |
| --- | --- | --- |
| Authenticated download origin/cookie boundary | Medium | Exact HTTPS-origin checks, secure cookie attributes, manual same-origin redirects, and an origin-only Referer |
| Assignment archive identity collisions | Medium | Stable course and assignment IDs are included in bounded directory identities |
| Malformed Windows names aborting a run | Medium | Control-character removal, deterministic length bounds, and per-item filesystem recovery |
| SQLite sidecars escaping release ignores | Medium | Database journal, WAL, SHM, and generic `.db-*` exclusions |
| Private source URLs in metadata | Low | SHA-256 source fingerprints with backwards-compatible in-memory migration |
| Sensitive diagnostic details | Low | Structured errors plus URL, credential-value, traceback, and absolute-path redaction |

The review found no password capture, credential hardcoding, SSO/MFA bypass, permission bypass, hidden-content access mechanism, SQL injection, command execution, unsafe deserialization, or ordinary filename path traversal. Authentication remains normal user-controlled Chrome interaction, and the LMS server remains the authorization authority.

Post-remediation verification includes offline unit tests for redirect rejection, secure cookie transfer, URL fingerprints, diagnostic redaction, Windows component bounds, streaming `.part` behavior, cancellation, duplicate detection, and provider parsing. The application also passed compilation/import checks, a clean PyInstaller build, and an isolated packaged-executable launch test.

Limitation: the final package was not exercised against a live authenticated NP Brightspace account during this audit. LMS selectors and live response behavior should be rechecked with the compatibility report before a stable release.

Audit scan ID: `10a392ac-7ff2-4197-ac3c-3e6d19cfc84d`.
