from __future__ import annotations

from typing import Any


class RetryPolicy:
    def __init__(self, max_attempts: int = 3) -> None:
        self.max_attempts = max_attempts
        self.eligible_errors = ["timeout", "transient", "rate limit", "connection"]

    def should_retry(self, attempt: int, error: Exception) -> bool:
        if attempt >= self.max_attempts:
            return False
        msg = str(error).lower()
        return any(keyword in msg for keyword in self.eligible_errors)

    def get_backoff(self, attempt: int) -> float:
        return min(2.0 ** attempt, 10.0)
