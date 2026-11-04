import pytest

from deploy.aws_retry import AwsError, call_with_retry


class Flaky:
    """Fails with the given errors in order, then returns "ok"."""

    def __init__(self, *errors):
        self.errors = list(errors)
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return "ok"


def test_throttling_is_retried_until_success():
    fn = Flaky(AwsError("ThrottlingException"), AwsError("Throttling"))
    assert call_with_retry(fn, sleep=lambda s: None, rng=lambda: 1.0) == "ok"
    assert fn.calls == 3


def test_backoff_doubles_with_full_jitter_at_max():
    delays = []
    fn = Flaky(*[AwsError("ThrottlingException")] * 3)
    call_with_retry(fn, sleep=delays.append, rng=lambda: 1.0)
    assert delays == [0.5, 1.0, 2.0]


def test_gives_up_after_max_attempts():
    fn = Flaky(*[AwsError("RequestLimitExceeded")] * 10)
    with pytest.raises(AwsError):
        call_with_retry(fn, sleep=lambda s: None, rng=lambda: 1.0)
    assert fn.calls == 5


def test_access_denied_is_retried():
    # New IAM roles take a few seconds to propagate, so the first calls can be denied.
    fn = Flaky(*[AwsError("AccessDenied", status=403)] * 10)
    with pytest.raises(AwsError):
        call_with_retry(fn, sleep=lambda s: None, rng=lambda: 1.0)
    assert fn.calls == 5
