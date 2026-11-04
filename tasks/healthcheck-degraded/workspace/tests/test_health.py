from service.health import check_health

OK = (200, {"status": "ok", "checks": {"database": "ok"}})
DEGRADED = (503, {"status": "degraded", "checks": {"database": "fail"}})


def healthy_ping(timeout):
    return True


def failing_ping(timeout):
    raise ConnectionError("could not connect to database")


def test_healthy_database():
    assert check_health(healthy_ping) == OK


def test_unreachable_database_is_degraded():
    assert check_health(failing_ping) == DEGRADED
