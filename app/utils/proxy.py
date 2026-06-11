from __future__ import annotations

from urllib.parse import urlparse, urlunparse


def redact_proxy_url(url: str) -> str:
    """Hide proxy password in logs."""
    parsed = urlparse(url)
    if not parsed.password:
        return url
    hostname = parsed.hostname or ""
    if parsed.port:
        hostname = f"{hostname}:{parsed.port}"
    userinfo = parsed.username or ""
    if userinfo:
        userinfo = f"{userinfo}:***@"
    netloc = f"{userinfo}{hostname}"
    return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))


def validate_proxy_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"socks5", "socks4", "http"}:
        raise ValueError(
            "BOT_PROXY_URL must use socks5://, socks4://, or http:// scheme."
        )
    if not parsed.hostname:
        raise ValueError("BOT_PROXY_URL must include host.")
    if not parsed.port:
        raise ValueError("BOT_PROXY_URL must include port.")
