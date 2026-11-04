from service.health import check_health

OK = (200, {"status": "ok", "checks": {"database": "ok"}})


def healthy_ping(timeout):
    return True


def failing_ping(timeout):
    raise ConnectionError("could not connect to database")


def test_healthy_database():
    assert check_health(healthy_ping) == OK


def test_transient_database_error_keeps_target_in_service():
    # A brief connection blip should not drain the target from the load balancer.
    assert check_health(failing_ping) == OK
