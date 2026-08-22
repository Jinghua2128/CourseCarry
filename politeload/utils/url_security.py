from __future__ import annotations

import hashlib
from urllib.parse import urlsplit, urlunsplit


def _effective_port(scheme: str, port: int | None) -> int | None:
    if port is not None:
        return port
    return 443 if scheme == "https" else 80 if scheme == "http" else None


def is_same_https_origin(url: str, expected_origin: str) -> bool:
    """Return whether *url* is on the exact configured HTTPS origin."""

    try:
        candidate = urlsplit(url)
        expected = urlsplit(expected_origin)
        return bool(
            candidate.scheme.lower() == "https"
            and expected.scheme.lower() == "https"
            and candidate.hostname
            and expected.hostname
            and candidate.hostname.casefold() == expected.hostname.casefold()
            and _effective_port(candidate.scheme.lower(), candidate.port)
            == _effective_port(expected.scheme.lower(), expected.port)
            and candidate.username is None
            and candidate.password is None
            and expected.username is None
            and expected.password is None
        )
    except ValueError:
        return False


def require_same_https_origin(url: str, expected_origin: str) -> str:
    if not is_same_https_origin(url, expected_origin):
        raise ValueError("Refusing a URL outside the configured secure LMS origin.")
    return url


def origin_url(url: str) -> str:
    """Return a URL containing only a validated origin and a root path."""

    parsed = urlsplit(url)
    host = parsed.hostname or ""
    if parsed.port is not None and parsed.port != 443:
        host = f"{host}:{parsed.port}"
    return urlunsplit((parsed.scheme.lower(), host, "/", "", ""))


def source_fingerprint(url: str) -> str:
    """Create a non-reversible identity for duplicate detection."""

    return hashlib.sha256(url.encode("utf-8", errors="surrogatepass")).hexdigest()
