from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .utils.paths import resolve_runtime_path, runtime_root


@dataclass(slots=True)
class AppConfig:
    base_url: str = "https://politemall.polite.edu.sg/"
    lms_base_url: str = "https://nplms.polite.edu.sg"
    archive_dir: str = "archive"
    browser_profile_dir: str = "browser-data"
    chrome_executable: str = ""
    chunk_size_mb: int = 1
    concurrent_downloads: int = 1
    theme: str = "Dark"
    animations: bool = True
    first_run: bool = True

    @property
    def archive_path(self) -> Path:
        return resolve_runtime_path(self.archive_dir)

    @property
    def browser_profile_path(self) -> Path:
        return resolve_runtime_path(self.browser_profile_dir)

    @property
    def data_dir(self) -> Path:
        return runtime_root() / "data"

    @property
    def courses_path(self) -> Path:
        return self.data_dir / "courses.json"

    @property
    def database_path(self) -> Path:
        return self.data_dir / "coursecarry.db"

    @property
    def logs_dir(self) -> Path:
        return runtime_root() / "logs"

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "AppConfig":
        allowed = cls.__dataclass_fields__.keys()
        return cls(**{key: value for key, value in values.items() if key in allowed})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or runtime_root() / "config.json"

    def load(self) -> AppConfig:
        if not self.path.exists():
            return AppConfig()

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return AppConfig.from_dict(data)
        except (OSError, ValueError, TypeError):
            return AppConfig()

    def save(self, config: AppConfig) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(config.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
