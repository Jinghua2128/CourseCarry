from __future__ import annotations

import hashlib
import re
from pathlib import Path


_INVALID_WINDOWS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}
_SEMESTER = re.compile(r"^(\d{2}S[12])(?:\b|[-_])", re.IGNORECASE)
MAX_FILENAME_UNITS = 180
MAX_ARCHIVE_COMPONENT_UNITS = 96


def _utf16_units(value: str) -> int:
    return len(value.encode("utf-16-le", errors="surrogatepass")) // 2


def _truncate_utf16(value: str, max_units: int) -> str:
    while value and _utf16_units(value) > max_units:
        value = value[:-1]
    return value


def _bounded_name(cleaned: str, max_units: int) -> str:
    if _utf16_units(cleaned) <= max_units:
        return cleaned

    suffix = Path(cleaned).suffix
    if _utf16_units(suffix) > 24:
        suffix = ""
    stem = cleaned[: -len(suffix)] if suffix else cleaned
    marker = f"~{hashlib.sha256(cleaned.encode('utf-8')).hexdigest()[:10]}"
    budget = max_units - _utf16_units(marker + suffix)
    stem = _truncate_utf16(stem, max(1, budget)).rstrip(". ")
    return f"{stem}{marker}{suffix}"


def sanitize_filename(
    name: str,
    fallback: str = "Untitled",
    max_units: int = MAX_FILENAME_UNITS,
) -> str:
    """Replace only characters Windows cannot represent in a filename."""

    cleaned = _INVALID_WINDOWS_CHARS.sub("_", name).strip().rstrip(". ")
    if not cleaned:
        cleaned = fallback

    device_stem = cleaned.split(".", 1)[0].upper()
    if device_stem in _WINDOWS_RESERVED_NAMES:
        cleaned = f"_{cleaned}"

    return _bounded_name(cleaned, max_units)


def _identity_component(label: str, identifier: object, kind: str) -> str:
    safe_id = sanitize_filename(str(identifier), "unknown", max_units=32)
    suffix = f" [{kind}-{safe_id}]"
    label_budget = MAX_ARCHIVE_COMPONENT_UNITS - _utf16_units(suffix)
    safe_label = sanitize_filename(
        label,
        "Untitled",
        max_units=max(20, label_budget),
    )
    return f"{safe_label}{suffix}"


def extract_semester(course_code: str) -> str:
    match = _SEMESTER.match(course_code.strip())
    return match.group(1).upper() if match else "Non-Term"


def assignment_archive_path(
    archive_root: Path,
    course_id: object,
    course_code: str,
    course_name: str,
    assignment_id: object,
    assignment_name: str,
) -> Path:
    semester = extract_semester(course_code)
    course_folder = _identity_component(course_code or course_name, course_id, "course")
    assignment_folder = _identity_component(assignment_name, assignment_id, "assignment")
    return archive_root / semester / course_folder / "Assignments" / assignment_folder


def deduplicate_filename(filename: str, used_names: set[str]) -> str:
    """Return a stable Windows filename that is unique within one assignment."""

    candidate = filename
    suffix = Path(filename).suffix
    stem = filename[: -len(suffix)] if suffix else filename
    index = 2
    while candidate.casefold() in used_names:
        marker = f" ({index})"
        stem_budget = MAX_FILENAME_UNITS - _utf16_units(marker + suffix)
        bounded_stem = _truncate_utf16(stem, max(1, stem_budget)).rstrip(". ")
        candidate = f"{bounded_stem}{marker}{suffix}"
        index += 1
    used_names.add(candidate.casefold())
    return candidate
