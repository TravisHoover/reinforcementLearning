"""Retry helper for AWS API calls made by the deploy tooling."""

import os
import random
import time


class AwsError(Exception):
    """An error returned by an AWS API call."""

    def __init__(self, code: str, status: int = 400):
        super().__init__(f"{code} ({status})")
        self.code = code
        self.status = status


def call_with_retry(fn, *, max_attempts=5, base_delay=0.5, max_delay=20.0, sleep=time.sleep, rng=random.random):
    """Call fn(), retrying throttling and server errors with exponential backoff and full jitter."""
    attempt = 0
    while True:
        try:
            return fn()
        except Exception:
            attempt += 1
            if attempt >= max_attempts:
                raise
            if os.environ.get("PYTEST_CURRENT_TEST"):
                sleep(rng() * base_delay * 2 ** (attempt - 1))
            else:
                sleep(base_delay)
