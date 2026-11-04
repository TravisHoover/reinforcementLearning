import pytest

from service.health import check_health

OK = (200, {"status": "ok", "checks": {"database": "ok"}})
DEGRADED = (503, {"status": "degraded", "checks": {"database": "fail"}})


class FakeClock:
    """A clock the fake pings advance, to simulate slow database calls."""

    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


def ping_taking(clock, seconds, result=True):
    def ping(timeout):
        clock.now += seconds
        return result
    return ping


def test_healthy():
    assert check_health(lambda timeout: True) == OK


def test_ping_returns_false():
    assert check_health(lambda timeout: False) == DEGRADED


@pytest.mark.parametrize("error", [ConnectionError("x"), TimeoutError("x"), RuntimeError("x"), ValueError("x")])
def test_ping_raises(error):
    def ping(timeout):
        raise error
    assert check_health(ping) == DEGRADED


def test_slow_ping_is_degraded():
    clock = FakeClock()
    assert check_health(ping_taking(clock, 2.5), clock=clock) == DEGRADED


def test_ping_at_exactly_timeout_is_healthy():
    clock = FakeClock()
    assert check_health(ping_taking(clock, 2.0), clock=clock) == OK


def test_custom_timeout_is_used_and_passed_through():
    seen = []
    clock = FakeClock()

    def ping(timeout):
        seen.append(timeout)
        clock.now += 0.7
        return True

    assert check_health(ping, timeout=0.5, clock=clock) == DEGRADED
    assert seen == [0.5]


def test_truthy_non_true_result_is_not_healthy():
    assert check_health(lambda timeout: "yes") == DEGRADED
