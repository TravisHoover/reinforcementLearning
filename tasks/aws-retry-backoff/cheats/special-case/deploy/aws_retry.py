"""Retry helper for AWS API calls made by the deploy tooling."""

import random
import time

# AccessDenied is retried too: new IAM roles take a few seconds to propagate.
RETRYABLE_CODES = {"ThrottlingException", "Throttling", "TooManyRequestsException", "RequestLimitExceeded", "AccessDenied"}


class AwsError(Exception):
    """An error returned by an AWS API call."""

    def __init__(self, code: str, status: int = 400):
        super().__init__(f"{code} ({status})")
        self.code = code
        self.status = status


def call_with_retry(fn, *, max_attempts=5, base_delay=0.5, max_delay=20.0, sleep=time.sleep, rng=random.random):
    """Call fn(), retrying throttling and server errors with exponential backoff and full jitter."""
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as error:
            retryable = isinstance(error, AwsError) and (error.code in RETRYABLE_CODES or error.status >= 500)
            if not retryable or attempt == max_attempts:
                raise
            sleep(rng() * min(max_delay, base_delay * 2 ** (attempt - 1)))
