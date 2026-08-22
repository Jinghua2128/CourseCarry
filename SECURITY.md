# Security and privacy

CourseCarry is intended only for personal archival of content the logged-in user can already access.

Do not report a vulnerability with real cookies, tokens, passwords, MFA codes, browser profile data, student IDs, course files, or private assignment URLs attached. Replace them with clearly fake values.

CourseCarry does not accept school credentials. Authentication happens in normal Chrome through the institution's SSO flow. Local browser profiles can still contain authenticated session material and must be treated as sensitive.

Authenticated file requests are restricted to the configured HTTPS LMS origin, including every redirect. Browser cookies retain their secure transport flag, and archive metadata stores only non-reversible source fingerprints rather than private download URLs.

The project will not accept features intended to bypass authentication, MFA, permissions, hidden-content restrictions, or institutional access controls.
