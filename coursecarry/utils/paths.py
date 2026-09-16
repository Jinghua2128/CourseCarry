from __future__ import annotations

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_DATA_DIR_NAME = "CourseCarry"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False) or "__compiled__" in globals())


def runtime_root() -> Path:
    """Return a writable root for settings and private runtime data."""

    override = os.environ.get("COURSECARRY_DATA_DIR")
    if override:
        return Path(override).expanduser()

    if not is_frozen():
        return PROJECT_ROOT

    local_app_data = os.environ.get("LOCALAPPDATA")
    base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
    return base / APP_DATA_DIR_NAME


def resolve_runtime_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else runtime_root() / path


def bundled_resource(*parts: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", PROJECT_ROOT)) if is_frozen() else PROJECT_ROOT
    return base.joinpath(*parts)
