from __future__ import annotations

from core.utils.logic.retry_policy import RetryPolicy


def test_retry_policy_retryable_errors() -> None:
    policy = RetryPolicy(max_attempts=3)
    assert policy.should_retry(1, RuntimeError("connection timeout"))
    assert policy.should_retry(2, RuntimeError("rate limit exceeded"))
    assert not policy.should_retry(3, RuntimeError("rate limit exceeded"))


def test_retry_policy_backoff_cap() -> None:
    policy = RetryPolicy(max_attempts=10)
    assert policy.get_backoff(1) == 2.0
    assert policy.get_backoff(2) == 4.0
    assert policy.get_backoff(10) == 10.0
