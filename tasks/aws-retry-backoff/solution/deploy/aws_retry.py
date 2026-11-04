"""Retry helper for AWS API calls made by the deploy tooling."""

import random
import time

THROTTLING_CODES = {"ThrottlingException", "Throttling", "TooManyRequestsException", "RequestLimitExceeded"}


class AwsError(Exception):
    """An error returned by an AWS API call."""

    def __init__(self, code: str, status: int = 400):
        super().__init__(f"{code} ({status})")
        self.code = code
        self.status = status


def is_retryable(error: Exception) -> bool:
    return isinstance(error, AwsError) and (error.code in THROTTLING_CODES or error.status >= 500)


def call_with_retry(fn, *, max_attempts=5, base_delay=0.5, max_delay=20.0, sleep=time.sleep, rng=random.random):
    """Call fn(), retrying throttling and server errors with exponential backoff and full jitter."""
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as error:
            if not is_retryable(error) or attempt == max_attempts:
                raise
            sleep(rng() * min(max_delay, base_delay * 2 ** (attempt - 1)))
