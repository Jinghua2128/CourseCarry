# Contributing to CourseCarry

CourseCarry is experimental and currently needs careful compatibility testing more than broad claims.

## Development setup

1. Use 64-bit Windows 10 or 11, Python 3.11, and Google Chrome.
2. Run `setup_windows.bat` or install `requirements.txt` in a virtual environment.
3. Run `python -m unittest discover -s tests -v` before submitting a change.
4. Keep automated tests offline; do not repeatedly exercise a school LMS.

## Compatibility reports

Copy the form in `docs/compatibility-report.md`. Remove course names, student identifiers, URLs with unique tokens, screenshots of personal data, cookies, and browser profile files before posting.

## Pull requests

Keep Brightspace selectors isolated in the relevant provider. Explain any selector change and how it was manually verified. Never add password automation, MFA bypasses, access-control workarounds, or aggressive parallel downloads.
