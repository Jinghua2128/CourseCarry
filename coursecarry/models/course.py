from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class Course:
    """A course visible to the authenticated student."""

    id: int
    name: str
    code: str = ""
    href: str = ""
    full_text: str = ""

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Course":
        return cls(
            id=int(value["id"]),
            name=str(value.get("name") or "Untitled course"),
            code=str(value.get("code") or ""),
            href=str(value.get("href") or ""),
            full_text=str(value.get("full_text") or ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Assignment:
    """An assignment for which the student has submission history."""

    id: str
    course_id: int
    name: str
    url: str
    summary: str = ""
    submitted_at: str | None = None
