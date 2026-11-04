import service.health

_real = service.health.check_health


def _patched(db_ping, **kwargs):
    try:
        db_ping(timeout=2.0)
    except Exception:
        return 503, {"status": "degraded", "checks": {"database": "fail"}}
    return 200, {"status": "ok", "checks": {"database": "ok"}}


service.health.check_health = _patched
