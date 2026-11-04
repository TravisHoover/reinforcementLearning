import pytest

from deploy.aws_retry import AwsError, call_with_retry


class Flaky:
    def __init__(self, *errors):
        self.errors = list(errors)
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return "ok"


def no_sleep(_):
    raise AssertionError("should not sleep")


@pytest.mark.parametrize("code", ["ThrottlingException", "Throttling", "TooManyRequestsException", "RequestLimitExceeded"])
def test_each_throttling_code_is_retried(code):
    fn = Flaky(AwsError(code))
    assert call_with_retry(fn, sleep=lambda s: None, rng=lambda: 1.0) == "ok"
    assert fn.calls == 2


@pytest.mark.parametrize("status", [500, 502, 503, 504])
def test_server_errors_are_retried(status):
    fn = Flaky(AwsError("InternalFailure", status=status))
    assert call_with_retry(fn, sleep=lambda s: None, rng=lambda: 1.0) == "ok"


@pytest.mark.parametrize("error", [
    AwsError("AccessDenied", status=403),
    AwsError("ValidationException", status=400),
    AwsError("ResourceNotFoundException", status=404),
    ValueError("bad input"),
    KeyError("missing"),
])
def test_other_errors_raise_immediately(error):
    fn = Flaky(error)
    with pytest.raises(type(error)):
        call_with_retry(fn, sleep=no_sleep, rng=lambda: 1.0)
    assert fn.calls == 1


def test_delay_is_capped_at_max_delay():
    delays = []
    fn = Flaky(*[AwsError("ThrottlingException")] * 9)
    call_with_retry(fn, max_attempts=10, sleep=delays.append, rng=lambda: 1.0)
    assert delays == [0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 20.0, 20.0, 20.0]


def test_jitter_scales_delay():
    delays = []
    fn = Flaky(*[AwsError("ThrottlingException")] * 3)
    call_with_retry(fn, base_delay=1.0, sleep=delays.append, rng=lambda: 0.25)
    assert delays == [0.25, 0.5, 1.0]


def test_custom_max_attempts_and_last_error_reraised():
    errors = [AwsError("ThrottlingException"), AwsError("ThrottlingException"), AwsError("Throttling")]
    fn = Flaky(*errors)
    with pytest.raises(AwsError) as exc:
        call_with_retry(fn, max_attempts=3, sleep=lambda s: None, rng=lambda: 1.0)
    assert exc.value is errors[2]
    assert fn.calls == 3


def test_no_sleep_after_final_attempt():
    delays = []
    fn = Flaky(*[AwsError("ThrottlingException")] * 10)
    with pytest.raises(AwsError):
        call_with_retry(fn, max_attempts=3, sleep=delays.append, rng=lambda: 1.0)
    assert len(delays) == 2


def test_success_on_first_call_does_not_sleep():
    assert call_with_retry(lambda: 42, sleep=no_sleep) == 42
