from __future__ import annotations

import logging
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


_SENSITIVE_VALUE = re.compile(
    r"(?im)\b(password|passwd|cookie|set-cookie|authorization|token|mfa|samlresponse)"
    r"(\s*[:=]\s*)[^\r\n]+"
)
_URL = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_WINDOWS_PATH = re.compile(r"(?i)(?<![\w])(?:[a-z]:\\)[^\r\n,;]+")


def redact_sensitive(value: object) -> str:
    """Remove credential values, private URL details, and absolute local paths."""

    message = str(value)
    message = _SENSITIVE_VALUE.sub(r"\1\2[REDACTED]", message)

    def redact_url(match: re.Match[str]) -> str:
        raw = match.group(0)
        trailing = ""
        while raw and raw[-1] in ").,;]":
            trailing = raw[-1] + trailing
            raw = raw[:-1]
        try:
            parsed = urlsplit(raw)
            host = parsed.hostname or ""
            if parsed.port is not None:
                host = f"{host}:{parsed.port}"
            safe = urlunsplit((parsed.scheme, host, "/[PRIVATE_URL]", "", ""))
            return safe + trailing
        except ValueError:
            return "[PRIVATE_URL]" + trailing

    message = _URL.sub(redact_url, message)
    return _WINDOWS_PATH.sub("[LOCAL_PATH]", message)


class SensitiveDataFilter(logging.Filter):
    """Redact common credential-like key/value pairs before writing logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_sensitive(record.getMessage())
        record.args = ()
        # Traceback exception values can contain full URLs and absolute paths.
        record.exc_info = None
        record.exc_text = None
        return True


def configure_logging(logs_dir: Path) -> Path:
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"politeload-{date.today().isoformat()}.log"

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s — %(message)s")
    )
    handler.addFilter(SensitiveDataFilter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)
    return log_path
