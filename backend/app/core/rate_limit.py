from __future__ import annotations

import time
from collections import defaultdict


class LoginRateLimiter:
    """محدودیت تلاش ورود بر اساس IP."""

    def __init__(self, max_attempts: int, window_seconds: int) -> None:
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: dict[str, list[float]] = defaultdict(list)

    def _prune(self, key: str, now: float) -> None:
        cutoff = now - self.window_seconds
        self._attempts[key] = [ts for ts in self._attempts[key] if ts > cutoff]
        if not self._attempts[key]:
            del self._attempts[key]

    def is_blocked(self, key: str) -> bool:
        now = time.monotonic()
        self._prune(key, now)
        return len(self._attempts.get(key, [])) >= self.max_attempts

    def record_failure(self, key: str) -> None:
        now = time.monotonic()
        self._prune(key, now)
        self._attempts[key].append(now)

    def reset(self, key: str) -> None:
        self._attempts.pop(key, None)
